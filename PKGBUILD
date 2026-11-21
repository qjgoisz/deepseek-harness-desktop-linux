pkgname=deepseek-harness-desktop
_upstream_version=0.2.2-rc.5
_electron_version=44.7.0
_node_version=24.21.0
pkgver="${_upstream_version/-/_}+systemruntime1"
pkgrel=1
pkgdesc='DeepSeek Harness Desktop with system Electron, Node.js, Python and pnpm'
arch=('x86_64')
url='https://deepseek.com/harness/'
license=('MIT')
depends=("electron${_electron_version%%.*}>=${_electron_version}"
         "nodejs>=${_node_version}" 'nodejs<27' 'pnpm>=12.21.0' 'pnpm<13'
         'xdg-utils' 'python' 'python-numpy' 'python-pandas' 'python-docx'
         'python-openpyxl' 'python-xlsxwriter' 'python-pillow' 'python-lxml' 'python-pptx')
makedepends=('curl' 'unzip' '7zip')
options=('!strip' '!debug')
_archive="deepseek-harness-${_upstream_version}-mac-arm64.zip"
_license_file="deepseek-harness-${_upstream_version}-LICENSE"
source=("https://download.deepseek.com/dsh-desk/bin/mac-arm64/${_archive}"
        "${_license_file}::https://raw.githubusercontent.com/deepseek-ai/deepseek-harness/9c2670d3bce5275e0d1610272958121af87787bb/LICENSE")
noextract=("${_archive}")
sha256sums=('c169975831897ee0925dbc23a661893511eff29bf645a7842ae1c2d2b5d5b8a0'
            'ebb4f09972aee8608be255debaf78451a68e95c290f55c240dec2ecfa16ea6be')

prepare() {
  local port="$srcdir/linux-port"
  if [[ -d "$port" ]]; then
    rm -r -- "$port"
  fi
  mkdir -p "$port"
  cp -a -- "$startdir"/{auto-build.sh,install-image-worker.sh,scripts,patches,icons,image-worker-src} "$port/"
}

build() {
  local port="$srcdir/linux-port"
  DSH_ELECTRON_VERSION="$_electron_version" bash "$port/auto-build.sh" \
    --arch x64 --formats pacman --electron system --only prepare,tree \
    --archive "$srcdir/$_archive" --store "$srcdir/build-cache"

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
  stage_arch_package "$pkgdir" "$ROOT/out-x64" "$_electron_version" 1
  install -Dm644 "$srcdir/$_license_file" "$pkgdir/usr/share/licenses/$pkgname/LICENSE"
}
