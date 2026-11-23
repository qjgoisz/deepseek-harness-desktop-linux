#!/bin/sh
set -e
app_root="$(dirname "$(readlink -f "$0")")/../lib/deepseek-harness"
dsh_resources="$app_root/resources"
. "$dsh_resources/netlink-guard/preload.sh"
exec "$app_root/deepseek-harness" "$@"
