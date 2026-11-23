# Sourced by desktop and CLI launchers with dsh_resources set to their resources root.
dsh_netlink_guard="$dsh_resources/netlink-guard/libdsh-netlink-guard.so"
if [ "${DSH_NETLINK_GUARD:-1}" != 0 ] && [ -r "$dsh_netlink_guard" ]; then
  case ":${LD_PRELOAD:-}:" in
    *":$dsh_netlink_guard:"*) ;;
    *) export LD_PRELOAD="$dsh_netlink_guard${LD_PRELOAD:+:$LD_PRELOAD}" ;;
  esac
fi
unset dsh_netlink_guard
