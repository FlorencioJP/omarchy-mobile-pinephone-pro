#!/bin/bash
# SPDX-License-Identifier: MIT
# Retour arrière depuis la SD ; conserve aussi la racine Omarchy mise de côté.
set -euo pipefail
[[ $EUID == 0 && $(findmnt -n -o SOURCE /) == /dev/mmcblk1p2 ]] || {
  echo 'Démarrer la SD et utiliser sudo.' >&2; exit 1;
}
[[ $(cat /sys/class/block/mmcblk1/device/type) == SD && $(cat /sys/class/block/mmcblk2/device/type) == MMC ]]
exec 9>/run/lock/omarchy-emmc-migration.lock
flock -n 9
for partition in /dev/mmcblk2p{1,2,3}; do ! findmnt -rn -S "$partition" >/dev/null; done
work=$(mktemp -d /mnt/omarchy-restore.XXXXXX)
cleanup() { sync; if mountpoint -q "$work"; then umount "$work"; fi; rmdir "$work"; }
trap cleanup EXIT
mount /dev/mmcblk2p3 "$work"
backup="$work/.omarchy-migration"
[[ -d $backup/sailfish-home && ! -e $backup/omarchy-root-before-restore ]]
current=$(mktemp)
sfdisk --dump /dev/mmcblk2 > "$current"
cmp "$backup/partitions-before.sfdisk" "$current"
rm "$current"
(cd "$backup" && sha256sum -c SHA256SUMS)
[[ $(stat -c %s "$backup/boot-before.img") == $(blockdev --getsize64 /dev/mmcblk2p1) ]]
read -r owner group mode < "$backup/home-root-metadata.txt"
[[ $owner =~ ^[0-9]+$ && $group =~ ^[0-9]+$ && $mode =~ ^[0-7]{3,4}$ ]]
mkdir -m700 "$backup/omarchy-root-before-restore"
shopt -s dotglob nullglob
for entry in "$work"/*; do
  case "${entry##*/}" in .omarchy-migration|lost+found) continue ;; esac
  mv -- "$entry" "$backup/omarchy-root-before-restore/"
done
for entry in "$backup/sailfish-home"/*; do mv -- "$entry" "$work/"; done
chown "$owner:$group" "$work"
chmod "$mode" "$work"
dd if="$backup/boot-before.img" of=/dev/mmcblk2p1 bs=4M conv=fsync status=progress
cmp "$backup/boot-before.img" /dev/mmcblk2p1
echo 'SAILFISH_RESTORED : éteindre et retirer la SD avant redémarrage normal.'
