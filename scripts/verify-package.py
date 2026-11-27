#!/usr/bin/env python3
"""Unpack local DSH packages and run their installed entry points in isolation."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import tempfile
import sys


ROOT = Path(__file__).resolve().parent.parent


def unpack(package, dest):
    if package.name.endswith(".AppImage"):
        subprocess.run([package, "--appimage-extract"], cwd=dest, stdout=subprocess.DEVNULL,
                       check=True, timeout=120)
        app = dest / "squashfs-root"
        return app / "AppRun", app / "resources"
    if package.name.endswith(".deb"):
        command = ["dpkg-deb", "-x", package, dest]
    elif package.name.endswith((".pkg.tar.zst", ".rpm")):
        command = ["bsdtar", "-xf", package, "-C", dest]
    else:
        raise ValueError(f"不支持的包格式：{package.name}")
    subprocess.run(command, check=True, timeout=120)
    library = dest / "usr/lib"
    arch_resources = library / "dsh-desktop-macos-style/resources"
    resources = arch_resources if package.name.endswith(".pkg.tar.zst") and arch_resources.is_dir() else (
        library / "deepseek-harness/resources")
    return dest / "usr/bin/deepseek-harness", resources


def verify(package, display_mode):
    print(f"验证 {package.name}", flush=True)
    checksum = package.with_name(package.name + ".sha256")
    if checksum.is_file():
        with package.open("rb") as stream:
            actual = hashlib.file_digest(stream, "sha256").hexdigest()
        if actual != checksum.read_text().split()[0]:
            raise ValueError("SHA256 与校验文件不一致")
        print("SHA256 校验通过", flush=True)
    with tempfile.TemporaryDirectory(prefix="dsh-package-", dir="/tmp") as directory:
        work = Path(directory)
        extracted = work / "extracted"
        extracted.mkdir()
        launcher, resources = unpack(package, extracted)
        guard = resources / "netlink-guard/libdsh-netlink-guard.so"
        if not os.access(launcher, os.X_OK) or not guard.is_file():
            raise ValueError("包内缺少桌面启动器或 Netlink 守卫")
        for name in ("home", "config", "cache", "runtime", "data"):
            (work / name).mkdir(mode=0o700)
        primary = resources / "runtime/primary-runtime"
        manifest = json.loads((primary / "runtime.json").read_text())
        arch = {"x86_64": "x64", "aarch64": "arm64"}.get(os.uname().machine)
        if arch is None or manifest["arch"] != arch:
            raise ValueError(f"需要在 {manifest['arch']} 主机上执行启动验证")
        node = Path("/usr/bin/node") if manifest.get("nodeMode") == "system" else (
            primary / "dependencies/node/bin/node")
        for source in ("scripts/package-desktop-smoke.mjs", "scripts/check-agent-dependencies.mjs",
                       "image-worker-src/verify-image-worker.cjs"):
            shutil.copyfile(ROOT / source, work / Path(source).name)
        smoke = [str(node), str(work / "package-desktop-smoke.mjs"),
                 str(launcher), str(resources), display_mode]
        env = {
            "PATH": "/usr/local/bin:/usr/bin:/bin", "LANG": "C.UTF-8",
            "HOME": str(work / "home"), "DSH_HOME": str(work / "home/.dsh"),
            "XDG_CONFIG_HOME": str(work / "config"), "XDG_CACHE_HOME": str(work / "cache"),
            "XDG_DATA_HOME": str(work / "data"), "XDG_RUNTIME_DIR": str(work / "runtime"),
            "LIBGL_ALWAYS_SOFTWARE": "1",
        }
        mesa = Path("/usr/share/glvnd/egl_vendor.d/50_mesa.json")
        if mesa.is_file():
            env["__EGL_VENDOR_LIBRARY_FILENAMES"] = str(mesa)
        if display_mode in ("wayland", "xwayland"):
            env["WAYLAND_DISPLAY"] = "dsh-verify"
            display = ["dbus-run-session", "--", "kwin_wayland", "--virtual",
                       "--no-lockscreen", "--socket", "dsh-verify"]
            if display_mode == "xwayland":
                display.append("--xwayland")
            display += ["--exit-with-session", shlex.join(smoke)]
        else:
            display = ["xvfb-run", "-a", *smoke]
        isolated = ["bwrap", "--unshare-net", "--unshare-pid", "--new-session",
                    "--die-with-parent", "--clearenv", "--ro-bind", "/", "/",
                    "--proc", "/proc", "--dev", "/dev", "--tmpfs", "/dev/shm",
                    "--tmpfs", "/tmp", "--tmpfs", "/home", "--tmpfs", "/run/user",
                    "--perms", "01777", "--dir", "/tmp/.X11-unix",
                    "--bind", directory, directory, "--chdir", directory]
        for key, value in env.items():
            isolated += ["--setenv", key, value]
        subprocess.run([*isolated, "--", *display], check=True, timeout=100)
        marker = work / "desktop-tested"
        if not marker.is_file() or marker.read_text() != display_mode:
            raise ValueError("隔离桌面会话退出前未完成主界面验证")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("packages", metavar="PACKAGE", nargs="+", type=Path)
    display = parser.add_mutually_exclusive_group()
    display.add_argument("--wayland", dest="display_mode", action="store_const", const="wayland",
                         help="使用隔离的 KWin 虚拟 Wayland 会话")
    display.add_argument("--xwayland", dest="display_mode", action="store_const", const="xwayland",
                         help="在隔离的 KWin 虚拟会话中使用 XWayland")
    parser.set_defaults(display_mode="x11")
    args = parser.parse_args()
    for path in args.packages:
        try:
            verify(path.resolve(strict=True), args.display_mode)
        except (OSError, ValueError, KeyError, IndexError, subprocess.SubprocessError) as error:
            print(f"{path.name} 验证失败：{error}", file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
