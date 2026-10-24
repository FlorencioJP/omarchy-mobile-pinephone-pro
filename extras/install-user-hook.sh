#!/bin/bash
set -euo pipefail
umask 077
[[ $EUID == 0 && $(uname -m) == aarch64 ]] || { echo 'Requiert sudo sur le PinePhone.' >&2; exit 1; }
partition=$(findmnt -n -o SOURCE /)
disk=$(lsblk -n -o PKNAME "$partition")
[[ $disk == mmcblk* && $(cat "/sys/class/block/$disk/device/type") =~ ^(SD|MMC)$ ]]
target=/usr/share/omarchy-ppp/hypr/desktop.lua
[[ -f $target && -f /usr/share/omarchy-ppp/hypr/hyprland.lua ]]
marker='-- PinePhone Pro: private user customization'
if grep -Fxq -- "$marker" "$target"; then echo 'PRIVATE_HOOK_ALREADY_INSTALLED'; exit 0; fi
backup=/var/lib/omarchy-ppp/private-hooks
install -d -m700 "$backup"
[[ -e $backup/desktop.lua.before ]] || cp -p "$target" "$backup/desktop.lua.before"
temporary=$(mktemp "${target}.XXXXXX")
trap 'rm -f "$temporary"' EXIT
cp -p "$target" "$temporary"
cat >> "$temporary" <<'LUA'

-- PinePhone Pro: private user customization
local customization = (os.getenv('XDG_CONFIG_HOME') or os.getenv('HOME') .. '/.config') .. '/omarchy-ppp/local.lua'
local customization_file = io.open(customization, 'r')
if customization_file then
  customization_file:close()
  dofile(customization)
end
LUA
luac5.4 -p "$temporary"
mv "$temporary" "$target"
sync
echo 'PRIVATE_HOOK_INSTALLED'
