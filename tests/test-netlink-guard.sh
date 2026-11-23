#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
work="$(mktemp -d /tmp/dsh-netlink-test.XXXXXX)"
trap 'rm -r -- "$work"' EXIT
case "$(uname -m)" in
  x86_64) arch=x64; cc="${CC_X64:-${CC:-cc}}" ;;
  aarch64) arch=arm64; cc="${CC_ARM64:-${CC:-cc}}" ;;
  *) echo "不支持当前测试架构" >&2; exit 1 ;;
esac
mkdir -p "$work/tree/resources"
"$ROOT/scripts/install-netlink-guard.sh" "$work/tree" "$arch"
"$cc" -std=c11 -O2 -Wall -Wextra -Werror "$ROOT/tests/netlink-guard-test.c" -o "$work/test"
guard="$work/tree/resources/netlink-guard/libdsh-netlink-guard.so"
DSH_NETLINK_GUARD_MAX_MS=8 "$work/test"
DSH_NETLINK_GUARD=1 DSH_NETLINK_GUARD_MAX_MS=8 EXPECT_BACKOFF=1 LD_PRELOAD="$guard" "$work/test"
DSH_NETLINK_GUARD=0 DSH_NETLINK_GUARD_MAX_MS=8 LD_PRELOAD="$guard" "$work/test"
