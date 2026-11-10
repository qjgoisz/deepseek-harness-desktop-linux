"""Adapt the staged Debian package to system Python and Node."""

import argparse
import json
import re
from shutil import copytree, ignore_patterns
from pathlib import Path


SYSTEM_PYTHON = '''async function systemWorkspacePaths(root, manifest) {
	const paths = workspaceDependencyPaths(root, manifest);
	await validatePayloadEntries(paths);
	const python = "/usr/bin/python3";
	const pptx = join(root, "dependencies", "python-pptx");
	const probe = String.raw`import importlib.metadata as metadata
import json
import sys

site = "/usr/lib/python3/dist-packages"
required = ("numpy", "pandas", "python-docx", "python-pptx", "openpyxl", "Pillow", "lxml", "XlsxWriter")
installed = {dist.metadata["Name"].lower().replace("_", "-"): dist.version
             for dist in metadata.distributions(path=[site]) if dist.metadata["Name"]}
versions = {name: installed[name.lower()] for name in required if name.lower() in installed}
pptx = sys.argv[1]
versions.pop("python-pptx", None)
for dist in metadata.distributions(path=[pptx]):
    if (dist.metadata["Name"] or "").lower().replace("_", "-") == "python-pptx":
        versions["python-pptx"] = dist.version
print(json.dumps({
    "pythonVersion": ".".join(map(str, sys.version_info[:3])),
    "pythonPackages": site,
    "pythonPptxPackages": pptx,
    "pythonDistributions": versions,
    "missingPythonDistributions": [name for name in required if name not in versions],
}))`;
	const { stdout } = await promisify(execFile)(python, ["-I", "-B", "-c", probe, pptx], {
		timeout: 5000,
		encoding: "utf8"
	}).catch((error) => {
		throw new Error("workspace dependencies: unable to query /usr/bin/python3; check the Debian python3 package", { cause: error });
	});
	return { ...paths, python, ...JSON.parse(stdout) };
}
'''

OFFICE_GUIDANCE = {
    "office-docx": ("Use \x60python-docx\x60 for DOCX creation and ordinary edits.", "python-docx"),
    "office-xlsx": ("Follow an explicit user or applicable AGENTS.md requirement", "openpyxl and pandas"),
    "office-pptx": ("Follow an explicit user or applicable AGENTS.md requirement", "python-pptx"),
}


def replace_once(source, old, new):
    if source.count(old) != 1:
        raise ValueError(f"Unexpected system runtime patch target: {old[:100]!r}")
    return source.replace(old, new, 1)


def adapt_workspace_dependencies(source):
    source = replace_once(
        source, 'import { dirname, isAbsolute, join } from "node:path";',
        'import { dirname, isAbsolute, join } from "node:path";\n'
        'import { execFile } from "node:child_process";\nimport { promisify } from "node:util";',
    )
    source = replace_once(
        source, 'const pythonPackages = value.pythonPackages === void 0 && legacy ? {} : value.pythonPackages;',
        'const systemPython = value.pythonMode === "system";\n'
        '\tif (systemPython && (legacy || platform !== "linux" || python !== void 0 || value.pythonPackages !== void 0)) '
        'throw new Error("primary runtime: invalid system Python metadata");\n'
        '\tconst pythonPackages = systemPython || value.pythonPackages === void 0 && legacy ? {} : value.pythonPackages;',
    )
    source = replace_once(source, '|| !isVersion(python) ||', '|| (!systemPython && !isVersion(python)) ||')
    source = replace_once(source, '\t\tpython,\n', '')
    source = replace_once(source, '\t\tpythonPackages\n',
                          '\t\t...(systemPython ? { pythonMode: "system", nodeMode: value.nodeMode } : { python, pythonPackages })\n')
    source = replace_once(source, 'if (manifest.platform === "win32") return aliases;',
                          'if (manifest.platform === "win32" || manifest.pythonMode === "system") return aliases;')
    source = replace_once(
        source, 'const node = manifest.node === void 0 ? {} : {',
        'const node = manifest.node === void 0 ? {} : manifest.nodeMode === "system" ? { node: "/usr/bin/node" } : {',
    )
    source = replace_once(source, '\treturn {\n\t\tpython: join(dependencies,',
                          '\tif (manifest.pythonMode === "system") return { ...node, ...pnpm };\n'
                          '\treturn {\n\t\tpython: join(dependencies,')
    source = replace_once(source, 'async function compatibleManifest(source) {',
                          SYSTEM_PYTHON + 'async function compatibleManifest(source) {')
    for function in ('resolvePrimaryRuntime(source)', 'installPrimaryRuntime(source, root)'):
        start = f'async function {function} {{\n\tconst manifest = await compatibleManifest(source);'
        source = replace_once(source, start, start + '\n\tif (manifest.pythonMode === "system") return systemWorkspacePaths(source, manifest);')
    # Update both the model-facing text and the structured result schema.
    description = [line for line in source.splitlines() if 'description: "Get absolute paths to bundled Python' in line]
    if len(description) != 1:
        raise ValueError("Unexpected load_workspace_dependencies description")
    source = replace_once(source, description[0],
                          '\t\tdescription: "Get system Python and Node paths, the bundled pnpm entry, and library versions. '
                          'Use the returned Python for Office unless the user or workspace specifies another environment. '
                          'The private pythonPptxPackages directory is needed only for python-pptx. '
                          'If a needed system library is missing, report the missing Debian package. '
                          'When Node.js and pnpm paths are returned, run pnpm with that Node executable and script path.",')
    source = replace_once(source, '\t\t\t\t\tnode: {\n\t\t\t\t\t\ttype: "string",\n'
                          '\t\t\t\t\t\tdescription: "Absent when the payload ships no Node.js."',
                          '\t\t\t\t\tpythonVersion: { type: "string" },\n'
                          '\t\t\t\t\tpythonPptxPackages: { type: "string" },\n'
                          '\t\t\t\t\tmissingPythonDistributions: { type: "array", items: { type: "string" } },\n'
                          '\t\t\t\t\tnode: {\n\t\t\t\t\t\ttype: "string",\n'
                          '\t\t\t\t\t\tdescription: "Absent when no Node.js executable is provided."')
    source = replace_once(source, 'description: "Absent when the payload ships no Node.js."',
                          'description: "Present only for bundled Node.js."')
    return replace_once(
        source, 'Bundled distribution names and versions recorded in runtime.json; excludes user-installed additions.',
        'Distribution names and versions in the selected Python environment.',
    )


def adapt_cli(source):
    start = '\n# 内置二进制在 resources 的**上一级**'
    end = '\nexport DSH_DESKTOP_FORCE_PACKAGED=1'
    if source.count(start) != 1 or source.count(end) != 1 or 'electron=$(find_electron)' not in source:
        raise ValueError("Unexpected Linux CLI launcher")
    source = source[:source.index(start)] + source[source.index(end):]
    source = replace_once(source, 'export DSH_DESKTOP_NODE_EXECUTABLE="$electron"',
                          'export DSH_DESKTOP_NODE_EXECUTABLE=/usr/bin/node')
    return replace_once(source, 'ELECTRON_RUN_AS_NODE=1 exec "$electron"',
                        'exec /usr/bin/node')


def patch(resources):
    runtime = resources / 'runtime/primary-runtime/runtime.json'
    data = json.loads(runtime.read_text(encoding='utf8'))
    if data.get('platform') != 'linux' or not isinstance(data.get('pythonPackages'), dict) or 'python' not in data:
        raise ValueError("Expected a Linux application tree with bundled Python metadata")
    python = data['python']
    pptx = data['pythonPackages'].get('python-pptx')
    node = data.get('node')
    for version in (python, pptx, node):
        if not isinstance(version, str) or not re.fullmatch(r'(?:0|[1-9]\d*)\.\d+\.\d+', version):
            raise ValueError(f"Expected a numeric Python, python-pptx or Node version, got {version!r}")
    data.pop('python')
    data.pop('pythonPackages')
    data.pop('payloadDigest', None)
    data['pythonMode'] = 'system'
    data['nodeMode'] = 'system'
    dependencies = runtime.parent / 'dependencies'
    source_site = dependencies / 'python/lib' / f'python{python.rsplit(".", 1)[0]}' / 'site-packages'
    pptx_site = dependencies / 'python-pptx'
    pptx_entries = ('pptx', f'python_pptx-{pptx}.dist-info')
    for entry in pptx_entries:
        if not (source_site / entry).is_dir():
            raise ValueError(f"Missing pinned python-pptx payload: {entry}")
    node_binary = dependencies / 'node/bin/node'
    if pptx_site.exists() or node_binary.is_symlink() or not node_binary.is_file():
        raise ValueError("Expected an unmodified bundled runtime tree")
    packages = resources / 'app/dsh/node_modules/@deepseek-ai'
    tool = packages / 'dsh-tool-workspace-dependencies/lib/index.js'
    main = resources / 'app/lib/main.js'
    cli = resources / 'runtime/cli/bin/dsh'
    host = 'function runtimeResources() {\n\tconst development = !desktopIsPackaged();\n\treturn {\n\t\tnode: process.execPath,'
    updates = {
        runtime: json.dumps(data, ensure_ascii=False, indent=2) + '\n',
        tool: adapt_workspace_dependencies(tool.read_text(encoding='utf8')),
        main: replace_once(main.read_text(encoding='utf8'), host,
                           host.replace('node: process.execPath,', 'node: development ? process.execPath : "/usr/bin/node",')),
        cli: adapt_cli(cli.read_text(encoding='utf8')),
    }
    for asset_root in (resources / 'runtime/office-skills', packages / 'dsh-skill-office/assets'):
        for skill, (prefix, libraries) in OFFICE_GUIDANCE.items():
            path = asset_root / skill / 'SKILL.md'
            source = path.read_text(encoding='utf8')
            paragraphs = [line for line in source.splitlines() if line.startswith(prefix)]
            if len(paragraphs) != 1 or 'load_workspace_dependencies' not in paragraphs[0]:
                raise ValueError(f"Unexpected Python guidance in {path}")
            guidance = (
                "Follow an explicit user or applicable AGENTS.md requirement for an environment or library. "
                "Otherwise call \x60load_workspace_dependencies\x60 and use its system Python path with "
                f"{libraries}. If a required library is missing, report the missing Debian package."
            )
            if skill == 'office-pptx':
                guidance = (
                    "Follow an explicit user or applicable AGENTS.md requirement for an environment or library. "
                    "Otherwise call \x60load_workspace_dependencies\x60 and run each PPTX script as "
                    '\x60PYTHONPATH="<pythonPptxPackages>" "<python>" script.py\x60, substituting the returned paths. '
                    "This loads the DSH-supplied python-pptx library with system Python for that command."
                )
            updates[path] = replace_once(source, paragraphs[0], guidance)
    for entry in pptx_entries:
        copytree(source_site / entry, pptx_site / entry, ignore=ignore_patterns('__pycache__', '*.pyc'))
    node_binary.unlink()
    node_binary.symlink_to('/usr/bin/node')
    (dependencies / 'node/LICENSE').unlink(missing_ok=True)
    for path, content in updates.items():
        path.write_text(content, encoding='utf8')
    return node


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('resources', type=Path)
    args = parser.parse_args()
    try:
        print(patch(args.resources))
    except (ValueError, OSError) as error:
        parser.exit(1, f"system runtime patch: {error}\n")
