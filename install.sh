#!/bin/bash
# SPDX-License-Identifier: MIT
set -euo pipefail
[[ $EUID == 0 && $(uname -m) == aarch64 ]] || { echo 'Requiert sudo sur le PinePhone Pro.' >&2; exit 1; }
partition=$(findmnt -n -o SOURCE /)
disk=$(lsblk -n -o PKNAME "$partition")
[[ $disk == mmcblk* && $(cat "/sys/class/block/$disk/device/type") == SD ]] || {
  echo 'Refus : le système actif ne réside pas sur une SD.' >&2; exit 1;
}
source_dir=$(cd -- "$(dirname -- "$0")" && pwd)
state=/var/lib/omarchy-ppp/desktop
install -d -m700 "$state"
exec > >(tee -a "$state/install.log") 2>&1
[[ $(df -B1 --output=avail / | tail -1) -gt 2000000000 ]] || {
  echo 'Au moins 2 Go libres sont requis avant installation.' >&2; exit 1;
}

# Vérifier le lot entier avant de demander une transaction à pacman.
python3 - "$source_dir" > "$state/archives.txt" <<'PY'
import hashlib, json
from pathlib import Path
import sys
from urllib.parse import urlsplit
root = Path(sys.argv[1])
packages = json.loads((root / 'packages.lock.json').read_text())['packages']
if not packages or len({p['name'] for p in packages}) != len(packages):
    raise SystemExit('Lot vide ou doublons')
for package in packages:
    if package['arch'] not in ('aarch64', 'any') or package['name'].startswith(('linux', 'u-boot', 'tow-boot', 'mkinitcpio')):
        raise SystemExit('Paquet hors périmètre : ' + package['name'])
    archive = root / 'cache' / Path(urlsplit(package['url']).path).name
    with archive.open('rb') as stream:
        actual = hashlib.file_digest(stream, 'sha256').hexdigest()
    if archive.stat().st_size != package['size'] or actual != package['sha256']:
        raise SystemExit('Archive altérée : ' + package['name'])
    if not archive.with_name(archive.name + '.sig').is_file():
        raise SystemExit('Signature absente : ' + package['name'])
    print(archive)
PY
mapfile -t archives < "$state/archives.txt"

# Imposer aussi les signatures pour les archives locales, sans changer pacman.conf.
awk '/^[[:space:]]*LocalFileSigLevel[[:space:]]*=/ {next}
     {print}
     /^\[options\]$/ {print "LocalFileSigLevel = Required"}' /etc/pacman.conf > "$state/pacman-required.conf"
pacman-conf --config "$state/pacman-required.conf" LocalFileSigLevel | grep -qx PackageRequired
pacman --config "$state/pacman-required.conf" -U --needed --noconfirm "${archives[@]}"
pacman -Dk

profile=/usr/share/omarchy-ppp/hypr/hyprland.lua
[[ -f $state/hyprland.lua.before ]] || cp -p "$profile" "$state/hyprland.lua.before"
install -m644 "$source_dir/overlay/usr/share/omarchy-ppp/hypr/desktop.lua" /usr/share/omarchy-ppp/hypr/desktop.lua
luac5.4 -p /usr/share/omarchy-ppp/hypr/desktop.lua
include="dofile('/usr/share/omarchy-ppp/hypr/desktop.lua')"
if ! grep -Fxq "$include" "$profile"; then
  printf '\n%s\n' "$include" >> "$profile"
fi
luac5.4 -p "$profile"
pacman -Q > "$state/installed-after.txt"
sync
echo 'DESKTOP_INSTALL_COMPLETE'
