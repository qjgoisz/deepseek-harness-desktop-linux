#!/usr/bin/env python3
"""Check or apply the dsh-sessions-manager 3.8.1 sidebar refresh fix."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import tempfile


PACKAGE = "dsh-sessions-manager"
VERSION = "3.8.1"
ORIGINAL = "36d2422c06417240d3ca2a1aa582d3a188289201195edd8f66d2aac0d27e7d0b"
PATCHED = "b09f81900d97b021da6faa9b5994b84ad9db8c915deb0e8a2b381df89188dc45"
PATCH = Path(__file__).with_name("client-3.8.1.patch")


def patch_client(source):
    with tempfile.TemporaryDirectory(prefix="dsh-sessions-sidebar-check-") as directory:
        original = Path(directory) / "client.js"
        original.write_bytes(source)
        revised = subprocess.run(
            ["patch", "--silent", "--batch", "--forward", "--fuzz=0", "--output=-", str(original)],
            input=PATCH.read_bytes(), stdout=subprocess.PIPE, check=True,
        ).stdout
    if hashlib.sha256(revised).hexdigest() != PATCHED:
        raise ValueError("补丁输出的 SHA256 与验证过的版本不一致。")
    subprocess.run(["node", "--check", "--input-type=module"], input=revised, check=True)
    return revised


def replace_client(target, source, revised):
    mode = stat.S_IMODE(target.stat().st_mode)
    with tempfile.TemporaryDirectory(dir=target.parent, prefix=".dsm-sidebar-refresh-") as directory:
        staged = Path(directory) / target.name
        staged.write_bytes(revised)
        staged.chmod(mode)
        with tempfile.NamedTemporaryFile(
            dir=target.parent, prefix="client.js.before-sidebar-refresh-", delete=False,
        ) as original:
            backup = Path(original.name)
            original.write(source)
        backup.chmod(mode)
        if target.read_bytes() != source:
            raise ValueError(f"Client 文件在检查后发生变化。原文件备份位于 {backup}")
        # pnpm may hard-link this file to its store. Replace the inode.
        staged.replace(target)
    return backup


def main():
    parser = argparse.ArgumentParser(description="检查或应用会话管理插件的侧栏刷新修复。")
    dsh_home = Path(os.environ.get("DSH_HOME", "").strip() or Path.home() / ".dsh")
    parser.add_argument("--profile", type=Path, default=dsh_home / "profiles/desktop")
    parser.add_argument("--apply", action="store_true", help="备份并应用补丁，默认只检查")
    args = parser.parse_args()

    try:
        modules = (args.profile.expanduser() / "node_modules").resolve(strict=True)
        package = (modules / PACKAGE).resolve(strict=True)
        target = (package / "lib/client.js").resolve(strict=True)
        if not package.is_relative_to(modules) or not target.is_relative_to(package) or not target.is_file():
            raise ValueError("插件路径超出指定 profile 的模块目录。")
        manifest = json.loads((package / "package.json").read_text(encoding="utf-8"))
        if (manifest.get("name"), manifest.get("version")) != (PACKAGE, VERSION):
            raise ValueError(f"补丁适用于 {PACKAGE} {VERSION}，请复核当前版本。")
        source = target.read_bytes()
        checksum = hashlib.sha256(source).hexdigest()
        if checksum == PATCHED:
            print(f"已应用修复：{target}")
            return
        if checksum != ORIGINAL:
            raise ValueError(f"Client 文件与已验证的原版不一致，请先复核：{target}")

        revised = patch_client(source)
        if args.apply:
            backup = replace_client(target, source, revised)
            print(f"已修复：{target}\n原文件备份：{backup}")
        else:
            print(f"原版和补丁校验通过，可使用 --apply 修复：{target}")
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        parser.exit(1, f"检查或应用失败：{error}\n")


if __name__ == "__main__":
    main()
