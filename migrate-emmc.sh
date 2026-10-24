#!/bin/bash
# SPDX-License-Identifier: MIT
# Migration spécifique au partitionnement Sailfish observé ; aucun formatage.
set -euo pipefail
umask 027
die() { echo "ARRÊT : $*" >&2; exit 1; }
[[ $EUID == 0 && $(uname -m) == aarch64 ]] || die 'Requiert sudo sur ARM64.'
[[ $(findmnt -n -o SOURCE /) == /dev/mmcblk1p2 ]] || die 'Démarrer la microSD avant migration.'
[[ $(findmnt -n -o SOURCE /boot) == /dev/mmcblk1p1 ]] || die '/boot SD absent.'
[[ $(cat /sys/class/block/mmcblk1/device/type) == SD ]] || die 'Source non SD.'
[[ $(cat /sys/class/block/mmcblk2/device/type) == MMC ]] || die 'Cible non eMMC.'
[[ -f /var/lib/omarchy-ppp/provisioned ]] || die 'Compte local non provisionné.'
[[ ! -e /var/lib/pacman/db.lck ]] || die 'Transaction pacman en cours.'
for command in rsync sfdisk blkid tar dd sha256sum mkimage python3 flock du; do command -v "$command" >/dev/null; done
exec 9>/run/lock/omarchy-emmc-migration.lock
flock -n 9 || die 'Migration déjà en cours.'
for number in 1 2 3; do
  partition="/dev/mmcblk2p$number"
  [[ $(blkid -s TYPE -o value "$partition") == ext4 ]] || die "Type inattendu : $partition"
  ! findmnt -rn -S "$partition" >/dev/null || die "$partition est déjà montée."
done
[[ $(cat /sys/class/power_supply/rk818-battery/capacity) -ge 60 ]] || die 'Batterie inférieure à 60 %.'
[[ $(cat /sys/class/power_supply/rk818-battery/status) =~ ^(Charging|Full)$ ]] || die 'Téléphone non alimenté.'
source_dir=$(cd -- "$(dirname -- "$0")" && pwd)
operator_gid=$(id -g terminal)
state=/var/lib/omarchy-ppp/emmc-migration
[[ ! -e $state/started ]] || die 'Tentative précédente présente : examiner les sauvegardes avant de reprendre.'
install -d -m2750 -g "$operator_gid" "$state"
exec > >(tee -a "$state/migration.log") 2>&1
touch "$state/started"
work=$(mktemp -d /mnt/omarchy-emmc.XXXXXX)
root="$work/root"
old="$work/sailfish-system"
mkdir "$root" "$old"
gui_was_active=0
migration_ready=0
cleanup() {
  result=$?
  trap - EXIT
  sync || result=1
  for path in "$root/boot" "$old" "$root"; do
    if mountpoint -q "$path"; then
      if ! umount "$path"; then echo "À démonter : $path"; result=1; fi
    fi
  done
  rmdir "$root" "$old" "$work" 2>/dev/null || true
  if [[ $result == 0 && $migration_ready == 1 ]]; then
    touch "$state/complete"
    echo 'MIGRATION_COMPLETE : éteindre, retirer la SD puis tester le démarrage eMMC.'
  else
    echo "MIGRATION_FAILED=$result : garder la SD et examiner $state/migration.log"
  fi
  if [[ $gui_was_active == 1 ]]; then systemctl start sddm.service || echo 'Relancer SDDM manuellement.'; fi
  exit "$result"
}
trap cleanup EXIT
mount -o ro,noload /dev/mmcblk2p2 "$old"
grep -sEq '^ID="?sailfishos"?$' "$old/etc/os-release" "$old/usr/lib/os-release" || die 'Sailfish non identifié sur p2.'
mount /dev/mmcblk2p3 "$root"
[[ ! -e $root/.omarchy-migration && ! -e $root/.omarchy-root-stage ]] || die 'Cible contenant déjà une préparation Omarchy.'
home_bytes=$(du -sx -B1 "$root" | cut -f1)
system_bytes=$(du -sx -B1 "$old" | cut -f1)
source_bytes=$(df -B1 --output=used / | tail -1)
required=$(( home_bytes + system_bytes + source_bytes + 2147483648 ))
[[ $(df -B1 --output=avail "$root" | tail -1) -gt $required ]] || die "Espace insuffisant : $required octets requis."
backup="$root/.omarchy-migration"
stage="$root/.omarchy-root-stage"
install -d -m2750 -g "$operator_gid" "$backup"
stat -c '%u %g %a' "$root" > "$backup/home-root-metadata.txt"
sfdisk --dump /dev/mmcblk2 > "$backup/partitions-before.sfdisk"
sfdisk --json /dev/mmcblk2 > "$backup/partitions-before.json"
blkid /dev/mmcblk2p{1,2,3} > "$backup/filesystems-before.txt"
echo 'PHASE=BACKUP'
dd if=/dev/mmcblk2p1 of="$backup/boot-before.img" bs=4M status=progress conv=fsync
tar --acls --xattrs --xattrs-include='*' --numeric-owner --one-file-system -cpf "$backup/sailfish-system.tar" -C "$old" .
tar --acls --xattrs --xattrs-include='*' --numeric-owner --one-file-system \
  --exclude='./.omarchy-migration' --exclude='./lost+found' -cpf "$backup/sailfish-home.tar" -C "$root" .
tar --compare --acls --xattrs --numeric-owner -f "$backup/sailfish-system.tar" -C "$old"
tar --compare --acls --xattrs --numeric-owner -f "$backup/sailfish-home.tar" -C "$root"
(cd "$backup" && sha256sum boot-before.img sailfish-system.tar sailfish-home.tar > SHA256SUMS)
sync
echo 'BACKUPS_COMPLETE'
umount "$old"

# Arrêter les applications locales avant de copier leurs fichiers de configuration.
if systemctl is-active --quiet sddm.service; then gui_was_active=1; fi
systemctl stop sddm.service
echo 'PHASE=COPY_ROOT'
mkdir "$stage"
rsync -aHAXx --numeric-ids --info=progress2 \
  --exclude='/dev/***' --exclude='/proc/***' --exclude='/sys/***' --exclude='/run/***' \
  --exclude='/tmp/***' --exclude='/mnt/***' --exclude='/media/***' --exclude='/boot/***' \
  --exclude='/var/log/journal/***' --exclude='/var/lib/omarchy-ppp/emmc-migration/***' \
  --exclude='/lost+found' / "$stage/"
install -d -m755 "$stage"/{dev,proc,sys,run,mnt,media,boot,var/log}
install -d -m1777 "$stage/tmp"
if [[ -d /var/log/journal ]]; then install -d -m2755 -g systemd-journal "$stage/var/log/journal"; fi
rsync -aHAX --numeric-ids /boot/ "$stage/boot/"
root_uuid=$(blkid -s UUID -o value /dev/mmcblk2p3)
boot_uuid=$(blkid -s UUID -o value /dev/mmcblk2p1)
python3 "$source_dir/emmc-config.py" "$stage" "$root_uuid" "$boot_uuid"
mkimage -A arm -O linux -T script -C none -n 'Omarchy PinePhone Pro eMMC' \
  -d "$stage/boot/boot.txt" "$stage/boot/boot.scr"
cmp /boot/Image.gz "$stage/boot/Image.gz"
cmp /boot/initramfs-linux.img "$stage/boot/initramfs-linux.img"
pacman --sysroot "$stage" -Dk
[[ -x $stage/usr/bin/start-omarchy-ppp && -f $stage/usr/share/sddm/themes/omarchy-ppp/Main.qml ]] || die 'Session copiée incomplète.'

echo 'PHASE=COMMIT_ROOT'
mkdir -m700 "$backup/sailfish-home"
shopt -s dotglob nullglob
for entry in "$root"/*; do
  case "${entry##*/}" in .omarchy-migration|.omarchy-root-stage|lost+found) continue ;; esac
  mv -- "$entry" "$backup/sailfish-home/"
done
for entry in "$stage"/*; do mv -- "$entry" "$root/"; done
rmdir "$stage"
chmod --reference=/ "$root"
chown --reference=/ "$root"
mv "$root/boot" "$backup/boot-new"
mkdir -m755 "$root/boot"
mount /dev/mmcblk2p1 "$root/boot"
echo 'PHASE=COMMIT_BOOT'
# Conserver l'ancien boot.scr jusqu'à la copie du noyau et de l'initramfs.
rsync -aHAX --numeric-ids --exclude='/boot.scr' "$backup/boot-new/" "$root/boot/"
cmp /boot/Image.gz "$root/boot/Image.gz"
cmp /boot/initramfs-linux.img "$root/boot/initramfs-linux.img"
install -m644 "$backup/boot-new/boot.scr" "$root/boot/boot.scr.omarchy-new"
sync -f "$root/boot"
mv -f "$root/boot/boot.scr.omarchy-new" "$root/boot/boot.scr"
sync -f "$root/boot"
sfdisk --dump /dev/mmcblk2 > "$state/partitions-after.sfdisk"
cmp "$backup/partitions-before.sfdisk" "$state/partitions-after.sfdisk"
printf '%s\n' "$root_uuid" > "$state/root-uuid"
migration_ready=1
