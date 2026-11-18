"""Adapt the staged Linux package to distribution-managed runtimes."""

import argparse
import json
import re
from shutil import copytree, ignore_patterns
from pathlib import Path


SYSTEM_PYTHON = '''async function systemWorkspacePaths(root, manifest) {
	const paths = workspaceDependencyPaths(root, manifest);
	await validatePayloadEntries(paths);
	const python = "/usr/bin/python3";
__PPTX_PATH__
	const probe = String.raw`import importlib.metadata as metadata
import json
import sys
__SITE_IMPORT__

site = __SITE__
required = ("numpy", "pandas", "python-docx", "python-pptx", "openpyxl", "Pillow", "lxml", "XlsxWriter")
installed = {dist.metadata["Name"].lower().replace("_", "-"): dist.version
             for dist in metadata.distributions(path=[site]) if dist.metadata["Name"]}
versions = {name: installed[name.lower()] for name in required if name.lower() in installed}
__PPTX_PROBE__
print(json.dumps({
    "pythonVersion": ".".join(map(str, sys.version_info[:3])),
    "pythonPackages": site,
__PPTX_RESULT__
    "pythonDistributions": versions,
    "missingPythonDistributions": [name for name in required if name not in versions],
}))`;
	const { stdout } = await promisify(execFile)(python, ["-I", "-B", "-c", probe__PPTX_ARG__], {
		timeout: 5000,
		encoding: "utf8"
	}).catch((error) => {
		throw new Error("workspace dependencies: unable to query /usr/bin/python3; check the __PACKAGE__ package", { cause: error });
	});
	return { ...paths, python, ...JSON.parse(stdout) };
}
'''

PRIVATE_PPTX_PROBE = '''pptx = sys.argv[1]
versions.pop("python-pptx", None)
for dist in metadata.distributions(path=[pptx]):
    if (dist.metadata["Name"] or "").lower().replace("_", "-") == "python-pptx":
        versions["python-pptx"] = dist.version'''


def system_python_probe(arch_linux):
    parts = {
        '__SITE_IMPORT__': 'import sysconfig' if arch_linux else '',
        '__SITE__': 'sysconfig.get_path("purelib")' if arch_linux else '"/usr/lib/python3/dist-packages"',
        '__PPTX_PATH__': '' if arch_linux else '\tconst pptx = join(root, "dependencies", "python-pptx");',
        '__PPTX_PROBE__': '' if arch_linux else PRIVATE_PPTX_PROBE,
        '__PPTX_RESULT__': '' if arch_linux else '    "pythonPptxPackages": pptx,',
        '__PPTX_ARG__': '' if arch_linux else ', pptx',
        '__PACKAGE__': 'Arch python' if arch_linux else 'Debian python3',
    }
    return re.sub(r'__[A-Z_]+__', lambda match: parts[match[0]], SYSTEM_PYTHON)

OFFICE_GUIDANCE = {
    "office-docx": ("Use \x60python-docx\x60 for DOCX creation and ordinary edits.", "python-docx"),
    "office-xlsx": ("Follow an explicit user or applicable AGENTS.md requirement", "openpyxl and pandas"),
    "office-pptx": ("Follow an explicit user or applicable AGENTS.md requirement", "python-pptx"),
}
PPTX_GUIDANCE = (
    'Follow an explicit user or applicable AGENTS.md requirement for an environment or library. '
    'Otherwise call `load_workspace_dependencies` and run each PPTX script as '
    '`PYTHONPATH="<pythonPptxPackages>" "<python>" script.py`, substituting the returned paths. '
    'This loads the DSH-supplied python-pptx library with system Python for that command.'
)


def system_office_guidance(libraries):
    return (
        'Follow an explicit user or applicable AGENTS.md requirement for an environment or library. '
        'Otherwise call `load_workspace_dependencies` and use its system Python path with '
        f'{libraries}. If a required library is missing, report the missing Debian package.'
    )


def replace_once(source, old, new):
    if source.count(old) != 1:
        raise ValueError(f"Unexpected system runtime patch target: {old[:100]!r}")
    return source.replace(old, new, 1)


def adapt_workspace_dependencies(source, arch_linux=False):
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
                          '\t\t...(systemPython ? { pythonMode: "system", nodeMode: value.nodeMode, pnpmMode: value.pnpmMode } : { python, pythonPackages })\n')
    source = replace_once(source, 'if (manifest.platform === "win32") return aliases;',
                          'if (manifest.platform === "win32" || manifest.pythonMode === "system") return aliases;')
    source = replace_once(
        source, 'const node = manifest.node === void 0 ? {} : {',
        'const node = manifest.node === void 0 ? {} : manifest.nodeMode === "system" ? { node: "/usr/bin/node" } : {',
    )
    source = replace_once(source, '\treturn {\n\t\tpython: join(dependencies,',
                          '\tif (manifest.pythonMode === "system") return { ...node, ...pnpm };\n'
                          '\treturn {\n\t\tpython: join(dependencies,')
    if arch_linux:
        source = replace_once(
            source, 'const pnpm = manifest.pnpm === void 0 ? {} : {',
            'const pnpm = manifest.pnpmMode === "system" ? { pnpm: "/usr/bin/pnpm" } : manifest.pnpm === void 0 ? {} : {',
        )
    source = replace_once(source, 'async function compatibleManifest(source) {',
                          system_python_probe(arch_linux) + 'async function compatibleManifest(source) {')
    for function in ('resolvePrimaryRuntime(source)', 'installPrimaryRuntime(source, root)'):
        start = f'async function {function} {{\n\tconst manifest = await compatibleManifest(source);'
        source = replace_once(source, start, start + '\n\tif (manifest.pythonMode === "system") return systemWorkspacePaths(source, manifest);')
    # Update both the model-facing text and the structured result schema.
    description = [line for line in source.splitlines() if 'description: "Get absolute paths to bundled Python' in line]
    if len(description) != 1:
        raise ValueError("Unexpected load_workspace_dependencies description")
    guidance = (
        'Get system Python and Node paths, the pnpm path, and library versions. '
        'Use the returned Python for Office unless the user or workspace specifies another environment. '
    )
    if arch_linux:
        guidance += 'Run the returned system pnpm executable directly. Report any missing Arch package.'
    else:
        guidance += (
            'The private pythonPptxPackages directory is needed only for python-pptx. '
            'If a needed system library is missing, report the missing Debian package. '
            'When Node.js and pnpm paths are returned, run pnpm with that Node executable and script path.'
        )
    source = replace_once(source, description[0], '\t\tdescription: ' + json.dumps(guidance) + ',')
    source = replace_once(source, '\t\t\t\t\tnode: {\n\t\t\t\t\t\ttype: "string",\n'
                          '\t\t\t\t\t\tdescription: "Absent when the payload ships no Node.js."',
                          '\t\t\t\t\tpythonVersion: { type: "string" },\n'
                          + ('' if arch_linux else '\t\t\t\t\tpythonPptxPackages: { type: "string" },\n') +
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


def office_updates(resources, package, arch_linux=False):
    entry = package / 'lib/index.js'
    source = entry.read_text(encoding='utf8')
    if 'const PYTHON_ENVIRONMENT_SECTIONS =' in source:
        defaults = re.findall(r'^\t"workspace-dependencies": "[^"\n]+",$', source, re.M)
        if len(defaults) != 1 or 'load_workspace_dependencies' not in defaults[0]:
            raise ValueError(f'Unexpected Python environment section in {entry}')
        guidance = (
            'Follow an explicit user or applicable AGENTS.md requirement for an environment or library. '
            'Otherwise call `load_workspace_dependencies` and use its system Python path and Office libraries. '
            'If a required library is missing, report the missing Arch package.'
            if arch_linux else system_office_guidance('the Debian libraries')
        )
        source = replace_once(source, defaults[0], '\t"workspace-dependencies": ' + json.dumps(guidance) + ',')
        if arch_linux:
            return {entry: source}
        source = replace_once(source, '${PYTHON_ENVIRONMENT_SECTIONS[config.pythonEnvironment]}',
                              '${config.pythonEnvironment === "workspace-dependencies" && candidate.name === "office-pptx" '
                              '? ' + json.dumps(PPTX_GUIDANCE) + ' : PYTHON_ENVIRONMENT_SECTIONS[config.pythonEnvironment]}')
        return {entry: source}

    updates = {}
    asset_roots = [package / 'assets']
    runtime_assets = resources / 'runtime/office-skills'
    if runtime_assets.exists():
        asset_roots.append(runtime_assets)
    for asset_root in asset_roots:
        for skill, (prefix, libraries) in OFFICE_GUIDANCE.items():
            path = asset_root / skill / 'SKILL.md'
            source = path.read_text(encoding='utf8')
            paragraphs = [line for line in source.splitlines() if line.startswith(prefix)]
            if len(paragraphs) != 1 or 'load_workspace_dependencies' not in paragraphs[0]:
                raise ValueError(f"Unexpected Python guidance in {path}")
            if arch_linux:
                guidance = system_office_guidance(libraries).replace('Debian package', 'Arch package')
            else:
                guidance = PPTX_GUIDANCE if skill == 'office-pptx' else system_office_guidance(libraries)
            updates[path] = replace_once(source, paragraphs[0], guidance)
    return updates


def arch_pnpm_updates(resources, packages, main, source):
    bundled_entry = 'join(desktopResourcesRoot(), "runtime", "primary-runtime", "dependencies", "pnpm", "bin", "pnpm.mjs")'
    host = packages / 'dsh-desktop-host/lib/index.js'
    cli = packages / 'dsh-desktop-host/lib/cli.js'
    wrapper = resources / 'runtime/bin/node'
    host_command = 'command: process.execPath,\n\t\t\targs: ["--expose-internals", process.argv[5]],'
    cli_command = ('command: process.execPath,\n\t\t\targs: ["--expose-internals", '
                   'join(supportDir, "primary-runtime", "dependencies", "pnpm", "bin", "pnpm.mjs")],')
    return {
        main: replace_once(source, bundled_entry, '"/usr/bin/pnpm"'),
        host: replace_once(host.read_text(encoding='utf8'), host_command,
                           'command: process.argv[5] === "/usr/bin/pnpm" ? process.argv[5] : process.execPath,\n'
                           '\t\t\targs: process.argv[5] === "/usr/bin/pnpm" ? [] : ["--expose-internals", process.argv[5]],'),
        cli: replace_once(cli.read_text(encoding='utf8'), cli_command, 'command: "/usr/bin/pnpm",\n\t\t\targs: [],'),
        wrapper: replace_once(wrapper.read_text(encoding='utf8'),
                              'export ELECTRON_RUN_AS_NODE=1\nexec "$DSH_DESKTOP_NODE_EXECUTABLE"',
                              'exec /usr/bin/node'),
    }


def patch(resources, arch_linux=False):
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
    if arch_linux:
        data['pnpmMode'] = 'system'
    dependencies = runtime.parent / 'dependencies'
    source_site = dependencies / 'python/lib' / f'python{python.rsplit(".", 1)[0]}' / 'site-packages'
    pptx_site = dependencies / 'python-pptx'
    pptx_entries = ('pptx', f'python_pptx-{pptx}.dist-info')
    if not arch_linux:
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
        tool: adapt_workspace_dependencies(tool.read_text(encoding='utf8'), arch_linux),
        main: replace_once(main.read_text(encoding='utf8'), host,
                           host.replace('node: process.execPath,', 'node: development ? process.execPath : "/usr/bin/node",')),
        cli: adapt_cli(cli.read_text(encoding='utf8')),
    }
    updates.update(office_updates(resources, packages / 'dsh-skill-office', arch_linux))
    if arch_linux:
        updates.update(arch_pnpm_updates(resources, packages, main, updates[main]))
    else:
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
    parser.add_argument('--arch-linux', action='store_true')
    parser.add_argument('resources', type=Path)
    args = parser.parse_args()
    try:
        print(patch(args.resources, args.arch_linux))
    except (ValueError, OSError) as error:
        parser.exit(1, f"system runtime patch: {error}\n")
