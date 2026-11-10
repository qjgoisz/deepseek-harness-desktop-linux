#!/usr/bin/env python3
"""Validate all active ELF payloads, including Python extensions and npm addons."""
import argparse
import json
import os
from pathlib import Path
from elf_payload import machine, MACHINES

def audit(root, arch):
    errors, count = [], 0
    root = Path(root)
    runtime = root / "resources/runtime/primary-runtime"
    manifest = runtime / "runtime.json"
    modes = json.loads(manifest.read_text(encoding="utf8")) if manifest.is_file() else {}
    python = runtime / "dependencies/python"
    node = runtime / "dependencies/node/bin/node"
    required = [root / "deepseek-harness"]
    if modes.get("nodeMode") == "system":
        if not node.is_symlink() or os.readlink(node) != "/usr/bin/node":
            errors.append("expected Node launcher symlink to /usr/bin/node")
    else:
        required.append(node)
    if modes.get("pythonMode") == "system":
        if python.exists() or python.is_symlink():
            errors.append("unexpected bundled Python in the system Python package")
    else:
        required.append(python / "bin/python3")
    for path in required:
        if not path.exists() or path.read_bytes()[:4] != b"\x7fELF":
            errors.append(f"missing ELF runtime: {path.relative_to(root)}")
    for directory, dirs, files in os.walk(root):
        dirs[:] = [name for name in dirs if name != ".sharp-native-backup"]
        # node-pty keeps upstream prebuilds for other OS/architectures. They are
        # dormant; the requested Linux prebuild is audited normally.
        if Path(directory).name == "prebuilds":
            dirs[:] = [name for name in dirs if name == f"linux-{arch}"]
        for name in files:
            path = Path(directory) / name
            if path.is_symlink():
                continue
            with path.open("rb") as handle:
                header = handle.read(64)
            if header[:4] != b"\x7fELF":
                continue
            count += 1
            try:
                actual = machine(header)
                if actual != MACHINES[arch]:
                    errors.append(f"wrong ELF machine {actual}: {path.relative_to(root)}")
            except ValueError as error:
                errors.append(f"{path.relative_to(root)}: {error}")
    if errors:
        raise ValueError("\n".join(errors))
    return count

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("tree")
    parser.add_argument("arch", choices=MACHINES)
    args = parser.parse_args()
    try:
        print(f"ELF 架构检查通过：{args.arch}，{audit(args.tree, args.arch)} 个文件")
    except (ValueError, OSError) as error:
        parser.exit(1, f"ELF 架构检查失败：{error}\n")
