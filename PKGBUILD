pkgname=dsh-desktop-macos-style
_upstream_version=0.2.2-rc.5
_electron_version=44.7.0
_node_version=24.21.0
pkgver="${_upstream_version/-/_}"
pkgrel=2
# Older builds appended +systemruntime1 to pkgver and sort above the upstream version.
epoch=1
pkgdesc='AI development workspace with macOS-style window controls'
arch=('x86_64')
url='https://deepseek.com/harness/'
license=('MIT')
depends=('bash' 'coreutils' "electron${_electron_version%%.*}>=${_electron_version}" 'glibc'
         'hicolor-icon-theme' 'libgcc' 'libstdc++' "nodejs>=${_node_version}" 'nodejs<27'
         'pnpm>=12.21.0' 'pnpm<13' 'python' 'xdg-utils')
makedepends=('7zip' 'curl' 'unzip')
optdepends=('python-docx: Word document editing'
            'python-lxml: Office XML processing'
            'python-numpy: numerical processing in workspace scripts'
            'python-openpyxl: Excel workbook editing'
            'python-pandas: tabular data processing'
            'python-pillow: image processing in Office scripts'
            'python-pptx: PowerPoint editing'
            'python-xlsxwriter: Excel workbook generation')
provides=("deepseek-harness-desktop=${pkgver}-${pkgrel}")
conflicts=('deepseek-harness-desktop')
options=('!strip' '!debug')
# The official download URL rolls forward. Keep each verified DMG under its versioned name.
_archive="deepseek-harness-${_upstream_version}-mac-arm64.dmg"
source=("${_archive}::https://download.deepseek.com/desktop/dsh-latest-macos-arm64.dmg"
        'DeepSeek-Harness.LICENSE')
noextract=("${_archive}")
sha256sums=('a257ded3fbcb9211d5ea0329cec68a07bbd05a5caaa73fd46693c02aa02c52e9'
            'ebb4f09972aee8608be255debaf78451a68e95c290f55c240dec2ecfa16ea6be')

prepare() {
  local port="$srcdir/linux-port"
  if [[ -d "$port" ]]; then
    rm -r -- "$port"
  fi
  mkdir -p "$port"
  cp -a -- "$startdir"/{auto-build.sh,install-image-worker.sh,scripts,patches,icons} \
    "$startdir"/{image-worker-src,netlink-guard} "$port/"
  cp -- "$srcdir/DeepSeek-Harness.LICENSE" "$port/"
}

build() {
  local port="$srcdir/linux-port"
  DSH_ELECTRON_VERSION="$_electron_version" bash "$port/auto-build.sh" \
    --arch x64 --formats pacman --electron system --only prepare,tree \
    --dmg "$srcdir/$_archive" --store "$srcdir/build-cache"

  python3 - "$port/out-x64/resources" "$_upstream_version" "$_node_version" <<'PY'
import json
import sys
from pathlib import Path

resources = Path(sys.argv[1])
app = json.loads((resources / 'app/package.json').read_text())
runtime = json.loads((resources / 'runtime/primary-runtime/runtime.json').read_text())
version, node = sys.argv[2:]
if app['version'] != version or runtime['desktopVersion'] != version or runtime['node'] != node:
    raise SystemExit('DSH payload versions do not match PKGBUILD')
PY
}

package() {
  local ROOT="$srcdir/linux-port" STORE="$srcdir/build-cache" WORK_BASE="$pkgdir" DRY_RUN=0
  source "$ROOT/scripts/build/common.sh"
  source "$ROOT/scripts/build/tree.sh"
  source "$ROOT/scripts/build/native-packages.sh"
  stage_arch_package "$pkgdir" "$ROOT/out-x64" "$_electron_version" 1 "$pkgname"
}
