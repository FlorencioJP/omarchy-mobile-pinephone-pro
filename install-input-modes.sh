#!/bin/bash
# SPDX-License-Identifier: MIT
set -euo pipefail
[[ $EUID == 0 && $(uname -m) == aarch64 ]] || { echo 'Requiert sudo sur ARM64.' >&2; exit 1; }
partition=$(findmnt -n -o SOURCE /)
disk=$(lsblk -n -o PKNAME "$partition")
[[ $disk == mmcblk* && $(cat "/sys/class/block/$disk/device/type") == SD ]] || {
  echo 'Refus : la racine cible doit être sur microSD.' >&2; exit 1;
}
[[ -f /var/lib/omarchy-ppp/provisioned ]] || {
  echo 'Créer le mot de passe local avant cette installation ; le premier provisionnement tactile reste à réaliser.' >&2; exit 1;
}
for command in Hyprland sddm squeekboard busctl gsettings python3 luac5.4 start-omarchy-ppp; do
  command -v "$command" >/dev/null
done
source_dir=$(cd -- "$(dirname -- "$0")" && pwd)
state=/var/lib/omarchy-ppp/input-modes
install -d -m700 "$state"
exec > >(tee -a "$state/install.log") 2>&1
for file in "$source_dir"/overlay/usr/share/omarchy-ppp/hypr/{device-mode,input-modes,greeter}.lua; do
  luac5.4 -p "$file"
done
python3 -c 'import ast,sys; ast.parse(open(sys.argv[1]).read())' "$source_dir/overlay/usr/bin/ppp-profile"
if [[ -L /etc/systemd/system/display-manager.service ]]; then
  [[ $(basename "$(readlink -f /etc/systemd/system/display-manager.service)") == sddm.service ]] || {
    echo 'Autre gestionnaire de connexion actif : arrêt sans le remplacer.' >&2; exit 1;
  }
fi
if [[ ! -f $state/before/complete ]]; then
  install -d -m700 "$state/before/root"
  for file in /usr/bin/ppp-display /usr/share/omarchy-ppp/hypr/hyprland.lua \
              /etc/sddm.conf.d /etc/systemd/system/omarchy-ppp-console.service \
              /etc/systemd/system/sddm.service.d /etc/systemd/system/default.target \
              /etc/systemd/system/display-manager.service; do
    [[ ! -e $file && ! -L $file ]] || cp -a --parents "$file" "$state/before/root"
  done
  systemctl get-default > "$state/before/default-target"
  touch "$state/before/complete"
fi
for file in ppp-profile ppp-display ppp-greeter; do
  install -m755 "$source_dir/overlay/usr/bin/$file" "/usr/bin/$file"
done
for file in usr/share/omarchy-ppp/hypr/{device-mode,input-modes,greeter}.lua \
            usr/share/wayland-sessions/omarchy-ppp.desktop \
            usr/share/sddm/themes/omarchy-ppp/{Main.qml,metadata.desktop} \
            etc/sddm.conf.d/90-pinephone-pro.conf \
            etc/systemd/system/sddm.service.d/pinephone-pro.conf \
            etc/systemd/system/omarchy-ppp-console.service; do
  install -Dm644 "$source_dir/overlay/$file" "/$file"
done
for file in "$source_dir"/applications/omarchy-{phone,keyboard}-mode.desktop; do
  install -m644 "$file" /usr/share/applications/
done
profile=/usr/share/omarchy-ppp/hypr/hyprland.lua
include="dofile('/usr/share/omarchy-ppp/hypr/input-modes.lua')"
grep -Fxq "$include" "$profile" || printf '\n%s\n' "$include" >> "$profile"
luac5.4 -p "$profile"
systemctl enable omarchy-ppp-console.service sddm.service
systemctl set-default graphical.target
sync
echo 'INPUT_MODES_INSTALLED_REBOOT_REQUIRED'
