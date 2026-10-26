#!/bin/bash
# SPDX-License-Identifier: MIT
set -euo pipefail
root=${1:?staging root required}
[[ -f /.dockerenv && $root == /src/image/work/run.*/root && -d $root/etc ]]
mobile=/src/cache/image/mobile/packages/omamobile-shell
cp -a --no-preserve=ownership overlay/usr/. "$root/usr/"
tar -C image/profile --exclude='__pycache__' --exclude='*.pyc' -cf - . |
  tar -C "$root" --no-same-owner -xf -
for path in etc/sddm.conf.d/90-pinephone-pro.conf etc/systemd/system/sddm.service.d/pinephone-pro.conf \
            etc/systemd/system/omarchy-ppp-console.service; do
  install -Dm644 "overlay/$path" "$root/$path"
done
chmod 755 "$root/usr/bin/"{start-omarchy-ppp,ppp-setup-user,ppp-connect,ppp-greeter,ppp-display,ppp-profile}
chmod 755 "$root/usr/lib/omarchy-ppp/"{set-password,welcome}
install -d "$root/usr/share/omarchy-ppp/plugins" "$root/usr/share/licenses/omarchy-ppp"
for name in bar quicksettings launcher switcher keyboard; do
  cp -a --no-preserve=ownership "$mobile/plugins/omamobile.$name" "$root/usr/share/omarchy-ppp/plugins/"
done
for name in launch bt-agent cell-watch call-watch osk-watch; do
  install -m755 "$mobile/bin/omamobile-$name" "$root/usr/bin/"
done
install -Dm644 "$mobile/environment.d/20-omamobile-osk.conf" "$root/usr/lib/environment.d/20-omamobile-osk.conf"
install -Dm644 "$mobile/squeekboard/keyboards/terminal/us.yaml" "$root/usr/share/squeekboard/keyboards/terminal/us.yaml"
install -m644 "$mobile/LICENSE" "$root/usr/share/licenses/omarchy-ppp/Omarchy-Mobile.txt"
install -m644 LICENSE "$root/usr/share/licenses/omarchy-ppp/LICENSE"
install -m755 power-status.py "$root/usr/bin/ppp-batteries"
install -m644 applications/*.desktop "$root/usr/share/applications/"

# Only show quick settings with a usable provider on this profile.
python3 - "$root" <<'PY'
from pathlib import Path
import re, sys
root=Path(sys.argv[1])
p=root/'usr/share/omarchy-ppp/plugins/omamobile.quicksettings/TilesModel.js'
text=p.read_text()
allowed={'wifi','bluetooth','mobile-data','airplane','hotspot','dnd','dark-theme','mic','screenshot','keyboard'}
text=re.sub(r'^  \{ id: "([^"]+)"[^\n]*\n', lambda m: m[0] if m[1] in allowed else '', text, flags=re.M)
text,count=re.subn(r'var DEFAULT_LAYOUT = \[[\s\S]*?\n\]', 'var DEFAULT_LAYOUT = ["wifi", "bluetooth", "keyboard", "dnd", "mobile-data", "airplane", "dark-theme", "screenshot"]', text, count=1)
assert count==1
p.write_text(text)
session=root/'usr/share/wayland-sessions/omarchy-ppp.desktop'
session.write_text(session.read_text().replace('Name=Omarchy Mobile (PinePhone Pro)', 'Name=Omarchy on PinePhone Pro'))
desktop=root/'usr/share/omarchy-ppp/hypr/desktop.lua'
desktop.write_text('\n'.join(line for line in desktop.read_text().splitlines() if "'CTRL + ALT + B'" not in line)+'\n')
PY

# No inherited factory account, shared password, or remote login in the image.
if chroot "$root" id alarm >/dev/null 2>&1; then chroot "$root" userdel -r alarm; fi
mkdir -p "$root/var/empty"
chroot "$root" useradd -m -U -k /var/empty -G wheel,video,input,audio -s /bin/bash terminal
chroot "$root" usermod --password '!' root
chroot "$root" usermod --password '!' terminal
chroot "$root" runuser -u terminal -- /usr/bin/ppp-setup-user
install -d -m755 "$root/etc/sudoers.d" "$root/var/lib/omarchy-ppp"
printf '%%wheel ALL=(ALL:ALL) ALL\n' > "$root/etc/sudoers.d/omarchy-ppp-wheel"
printf 'terminal ALL=(root) NOPASSWD: /usr/lib/omarchy-ppp/set-password ""\n' > "$root/etc/sudoers.d/omarchy-ppp-firstboot"
chmod 440 "$root/etc/sudoers.d/omarchy-ppp-"*
chroot "$root" visudo -c
cat > "$root/etc/sddm.conf.d/95-omarchy-ppp-firstboot.conf" <<'CONF'
[Autologin]
User=terminal
Session=omarchy-ppp.desktop
Relogin=false
CONF
chroot "$root" systemctl --root=/ disable sshd.service sshd.socket dhcpcd.service 2>/dev/null || true
chroot "$root" systemctl --root=/ enable sddm.service NetworkManager.service bluetooth.service ModemManager.service eg25-manager.service
chroot "$root" systemctl --root=/ set-default graphical.target

# Build a complete initramfs: the builder's devices are not the phone's.
python3 - "$root" <<'PY'
from pathlib import Path
import sys
r=Path(sys.argv[1])
p=r/'boot/boot.txt'
text=p.read_text()
old='root=/dev/mmcblk${linux_mmcdev}p${rootpart}'
assert text.count(old)==1
p.write_text(text.replace(old,'root=UUID=2d767a2c-b7d5-5680-b28c-ec8854a09fc1'))
(r/'etc/fstab').write_text('UUID=2d767a2c-b7d5-5680-b28c-ec8854a09fc1 / ext4 defaults,noatime 0 1\nUUID=4F50-5050 /boot vfat defaults 0 2\n')
(r/'etc/os-release').unlink(missing_ok=True)
(r/'etc/os-release').symlink_to('../usr/lib/os-release')
# linux-megi's preset explicitly passes -c, which bypasses config.d files.
p=r/'etc/mkinitcpio.conf'
import re
text,count=re.subn(r'^HOOKS=\([^\n]*\)', 'HOOKS=(base udev modconf kms keyboard keymap consolefont block filesystems fsck)', p.read_text(), count=1, flags=re.M)
assert count==1
p.write_text(text)
PY
chroot "$root" mkimage -A arm -O linux -T script -C none -n 'PinePhone Pro microSD' -d /boot/boot.txt /boot/boot.scr
mkdir -p "$root/etc/mkinitcpio.conf.d"
cat > "$root/etc/mkinitcpio.conf.d/zz-pinephone-pro.conf" <<'CONF'
HOOKS=(base udev modconf kms keyboard keymap consolefont block filesystems fsck)
CONF
chroot "$root" mkinitcpio -P
install -m644 image/inputs.json image/packages.lock.json "$root/usr/share/omarchy-ppp/"
chroot "$root" pacman -Q > "$root/usr/share/omarchy-ppp/installed-packages.txt"
python3 image/audit.py "$root"

# Build-time signing material and identities must never leave the builder.
chroot "$root" gpgconf --homedir /etc/pacman.d/gnupg --kill all
python3 - "$root" <<'PY'
from pathlib import Path
import shutil, sys
r=Path(sys.argv[1])
for name in ['root/.gnupg', 'root/.ssh', 'var/log/journal', 'var/lib/NetworkManager']:
    p=r/name
    if p.is_dir(): shutil.rmtree(p)
for p in list((r/'etc/ssh').glob('ssh_host_*')) + list((r/'etc/NetworkManager/system-connections').glob('*')):
    p.unlink()
for name in ['root/.bash_history','var/lib/systemd/random-seed','etc/resolv.conf','var/lib/dbus/machine-id', 'etc/shadow-', 'etc/gshadow-']:
    (r/name).unlink(missing_ok=True)
(r/'etc/machine-id').write_text('')
for p in (r/'var/log').rglob('*'):
    if p.is_file() and not p.is_symlink(): p.write_bytes(b'')
(r/'etc/resolv.conf').symlink_to('/run/NetworkManager/resolv.conf')
PY
chroot "$root" systemctl --root=/ enable omarchy-ppp-keyring.service
sync
