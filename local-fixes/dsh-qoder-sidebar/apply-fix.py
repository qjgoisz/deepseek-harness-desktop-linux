#!/usr/bin/env python3
"""Check or reapply the local DSH Qoder sidebar layout fix."""

import argparse
import json
import os
from pathlib import Path
import stat
import subprocess
import tempfile


ORIGINAL = b'[class*="_footArea"] [class*="_footerActions"]{flex-direction:column}'
FIXED = (
    b'[class*="_footArea"] > [class*="_footerActions"]:has(.qdp-foot,.qdp-railButton)'
    b'{flex-flow:column nowrap}'
)


def apply_fix(target, source, updated):
    mode = stat.S_IMODE(target.stat().st_mode)
    with tempfile.TemporaryDirectory(dir=target.parent, prefix=".qoder-sidebar-") as stage:
        staged = Path(stage) / "client.js"
        staged.write_bytes(updated)
        staged.chmod(mode)
        if target.read_bytes() != source:
            raise ValueError("插件文件在检查后发生变化，请重新运行。")
        # Unique names preserve earlier backups across updates and reinstalls.
        descriptor, name = tempfile.mkstemp(dir=target.parent, prefix="client.js.before-sidebar-layout-fix-")
        backup = Path(name)
        try:
            with os.fdopen(descriptor, "wb") as original:
                original.write(source)
        except OSError:
            backup.unlink(missing_ok=True)
            raise
        if target.read_bytes() != source:
            raise ValueError(f"插件文件在备份后发生变化。请重新检查，原文件备份位于 {backup}")
        staged.replace(target)
    return backup


def main():
    parser = argparse.ArgumentParser(description="检查或重新应用 DSH Qoder 侧栏兼容修复。")
    dsh_home = Path(os.environ.get("DSH_HOME", "").strip() or Path.home() / ".dsh")
    parser.add_argument("--profile", type=Path, default=dsh_home / "profiles/desktop",
                        help="DSH profile 目录，默认使用 Desktop profile")
    parser.add_argument("--apply", action="store_true", help="备份并应用修复，默认仅检查")
    args = parser.parse_args()

    try:
        modules = (args.profile.expanduser().resolve() / "node_modules").resolve(strict=True)
        package = (modules / "dsh-qoder-connect").resolve(strict=True)
        target = (package / "lib/client.js").resolve(strict=True)
        if not package.is_relative_to(modules) or not target.is_relative_to(package) or not target.is_file():
            raise ValueError("插件或客户端文件的实际路径超出了预期目录。")
        manifest = json.loads((package / "package.json").read_text(encoding="utf-8"))
        if manifest["name"] != "dsh-qoder-connect":
            raise ValueError("找到的包不是 dsh-qoder-connect。")
        version = manifest["version"]
        source = target.read_bytes()
        lines = source.splitlines()
        original_count = source.count(ORIGINAL)
        fixed_count = source.count(FIXED)
        if original_count == 0 and fixed_count == 1 and FIXED in lines:
            print(f"dsh-qoder-connect {version} 已应用修复：{target}")
            return
        if original_count != 1 or fixed_count != 0 or ORIGINAL not in lines:
            raise ValueError(f"dsh-qoder-connect {version} 的底栏规则已变化或存在重复，请先复核：{target}")

        updated = source.replace(ORIGINAL, FIXED, 1)
        subprocess.run(["node", "--check", "--input-type=commonjs"], input=updated, check=True)
        if not args.apply:
            print(f"dsh-qoder-connect {version} 仍包含已知的旧规则，可用 --apply 应用修复：{target}")
            return

        backup = apply_fix(target, source, updated)
        print(f"已修复：{target}\n原文件备份：{backup}\n请完全退出并重开 DSH。")
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError) as error:
        parser.exit(1, f"检查或应用失败：{error}\n")


if __name__ == "__main__":
    main()
