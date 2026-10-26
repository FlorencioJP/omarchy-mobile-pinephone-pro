#!/bin/bash
# SPDX-License-Identifier: MIT
set -euo pipefail
[[ -f /.dockerenv && $EUID == 0 && $(uname -m) == aarch64 && $PWD == /src ]] || {
  echo 'Run through image/build.sh in the ARM64 builder container.' >&2; exit 1;
}
mode=${1:?}
[[ $mode == prepare || $mode == build ]]
python3 image/verify.py
cache=/src/cache/image
work=$(mktemp -d /src/image/work/run.XXXXXX)
root=$work/root
disk=$work/disk.img
mkdir "$root"
loops=()
mounts=()
stop_key_agents() {
  chroot "$root" gpgconf --homedir /etc/pacman.d/gnupg --kill all 2>/dev/null || true
  # An upgraded gpgconf may not reach agents started by the base image.
  python3 - "$root" <<'PY'
from pathlib import Path
import os, signal, sys, time
root=Path(sys.argv[1]).resolve()
pids=[]
for p in Path('/proc').glob('[0-9]*'):
    try:
        if (p/'root').resolve()==root and (p/'comm').read_text().strip() in ('gpg-agent','dirmngr','keyboxd'):
            os.kill(int(p.name), signal.SIGTERM)
            pids.append(p)
    except (FileNotFoundError, ProcessLookupError):
        pass
for _ in range(50):
    if not any(p.exists() for p in pids): break
    time.sleep(.1)
PY
}
cleanup() {
  local i
  stop_key_agents
  for ((i=${#mounts[@]}-1; i>=0; i--)); do umount "${mounts[$i]}" || true; done
  for ((i=${#loops[@]}-1; i>=0; i--)); do losetup -d "${loops[$i]}" || true; done
}
trap cleanup EXIT
# Always decompress authenticated input; a cached raw image is not trusted.
xz -dc "$cache/base.img.xz" > "$disk"
sfdisk --json "$disk" > "$work/partition-before.json"
python3 - "$work/partition-before.json" <<'PY'
import json, sys
t = json.load(open(sys.argv[1]))['partitiontable']
assert t['label'] == 'gpt' and t['sectorsize'] == 512
assert [(p['start'], p['size']) for p in t['partitions']] == [(2048, 249856), (251904, 5953536)]
PY
truncate -s 12G "$disk"
sgdisk -e "$disk"
printf ', +\n' | sfdisk --no-reread -N 2 "$disk"
sfdisk --json "$disk" > "$work/partition-after.json"
python3 - "$work" <<'PY'
import json, pathlib, sys
w=pathlib.Path(sys.argv[1])
a=json.loads((w/'partition-before.json').read_text())['partitiontable']
b=json.loads((w/'partition-after.json').read_text())['partitiontable']
assert a['id']==b['id'] and a['partitions'][0]==b['partitions'][0]
for key in ('start','type','uuid','name'):
    assert a['partitions'][1][key]==b['partitions'][1][key]
PY
bootloop=$(losetup --find --show --offset $((2048*512)) --sizelimit $((249856*512)) "$disk")
loops+=("$bootloop")
rootloop=$(losetup --find --show --offset $((251904*512)) \
  --sizelimit "$(jq '.partitiontable.partitions[1].size * 512' "$work/partition-after.json")" "$disk")
loops+=("$rootloop")
e2fsck -pf "$rootloop" || [[ $? == 1 ]]
resize2fs "$rootloop"
if [[ $mode == build ]]; then
  tune2fs -U 2d767a2c-b7d5-5680-b28c-ec8854a09fc1 "$rootloop"
  fatlabel --volume-id "$bootloop" 4f505050
fi
mount "$rootloop" "$root"; mounts+=("$root")
mount "$bootloop" "$root/boot"; mounts+=("$root/boot")
mount -t tmpfs tmpfs "$root/dev"; mounts+=("$root/dev")
for spec in 'null 1 3' 'zero 1 5' 'random 1 8' 'urandom 1 9' 'tty 5 0'; do
  read -r name major minor <<< "$spec"
  mknod -m666 "$root/dev/$name" c "$major" "$minor"
done
mkdir -p "$root/dev/pts" "$root/dev/shm" "$root/run"
ln -s /proc/self/fd "$root/dev/fd"
ln -s /proc/self/fd/0 "$root/dev/stdin"
ln -s /proc/self/fd/1 "$root/dev/stdout"
ln -s /proc/self/fd/2 "$root/dev/stderr"
mount -t devpts -o newinstance,ptmxmode=0666 devpts "$root/dev/pts"; mounts+=("$root/dev/pts")
ln -s pts/ptmx "$root/dev/ptmx"
mount -t proc proc "$root/proc"; mounts+=("$root/proc")
mount -t sysfs -o ro sysfs "$root/sys"; mounts+=("$root/sys")
mount -t tmpfs tmpfs "$root/run"; mounts+=("$root/run")
mkdir -p "$root/etc/pacman.d/gnupg"
mount -t tmpfs -o mode=0700 tmpfs "$root/etc/pacman.d/gnupg"; mounts+=("$root/etc/pacman.d/gnupg")
mkdir -p "$cache/packages"
mount --bind "$cache/packages" "$root/var/cache/pacman/pkg"; mounts+=("$root/var/cache/pacman/pkg")
install -m644 image/pacman.conf "$root/etc/pacman.conf"
rm -f "$root/etc/resolv.conf"
install -m644 /etc/resolv.conf "$root/etc/resolv.conf"
for file in "$cache/omarchy_pkgs/pkgbuilds/omarchy-keyring/omarchy"{.gpg,-trusted,-revoked} \
            "$cache/danctnix_pkgs/danctnix/danctnix-keyring/danctnix"{.gpg,-trusted,-revoked} \
            "$cache/danctnix_pkgs/danctnix/archports-keyring/archports"{.gpg,-trusted,-revoked}; do
  install -m644 "$file" "$root/usr/share/pacman/keyrings/"
done
chroot "$root" pacman-key --init
chroot "$root" pacman-key --populate archlinuxarm danctnix archports omarchy
if [[ $mode == prepare ]]; then
  chroot "$root" pacman -Sy --noconfirm
  mapfile -t packages < <(sed '/^#/d; /^$/d' image/packages.txt)
  chroot "$root" pacman -Spu --needed --noconfirm --print-format '%r|%n|%v|%a|%l' "${packages[@]}" > "$cache/transaction.txt"
  chroot "$root" pacman -Suw --needed --noconfirm "${packages[@]}"
  python3 image/lock.py "$root"
  cleanup
  trap - EXIT
  rm -f "$disk"
  echo 'PREPARED: inspect cache/image/review.txt before accepting the package lock.'
else
  python3 image/lock.py --verify "$root"
  mapfile -t archives < <(python3 -c 'import json; print("\n".join("/var/cache/pacman/pkg/"+p["filename"] for p in json.load(open("image/packages.lock.json"))["packages"]))')
  # Pacman's upgrade resolver handles declared replacements transactionally.
  # Build its only repository from the already verified package files.
  chroot "$root" repo-add --include-sigs /run/ppp-image.db.tar.gz "${archives[@]}"
  cp "$root/run/ppp-image.db.tar.gz" "$root/var/lib/pacman/sync/ppp-image.db"
  cat > "$root/etc/pacman-image.conf" <<'CONF'
[options]
Architecture = aarch64
SigLevel = Required DatabaseOptional
LocalFileSigLevel = Required
[ppp-image]
Server = file:///var/cache/pacman/pkg
CONF
  mapfile -t packages < <(python3 -c 'import json; print("\n".join(p["name"] for p in json.load(open("image/packages.lock.json"))["packages"]))')
  chroot "$root" pacman --config /etc/pacman-image.conf -Spu --needed --noconfirm \
    --print-format '%n|%v' "${packages[@]}" > "$work/offline-plan.txt"
  python3 - "$work/offline-plan.txt" <<'PY'
import json, pathlib, sys
expected={p['name']+'|'+p['version'] for p in json.load(open('image/packages.lock.json'))['packages']}
actual={l for l in pathlib.Path(sys.argv[1]).read_text().splitlines() if '|' in l}
assert actual == expected, (sorted(expected-actual),sorted(actual-expected))
PY
  # lock.py allows only the reviewed audio-profile/vi conflict transitions.
  # These temporary public trust files are now in pacman's key database;
  # let the signed omarchy-keyring package install its own tracked copies.
  rm -f "$root/usr/share/pacman/keyrings/omarchy"{.gpg,-trusted,-revoked}
  chroot "$root" pacman --config /etc/pacman-image.conf -Su --needed --noconfirm --ask 4 "${packages[@]}"
  rm -f "$root/etc/pacman-image.conf" "$root/var/lib/pacman/sync/ppp-image.db"
  bash image/stage.sh "$root"
  chroot "$root" pacman -Q > "$work/packages.txt"
  cp "$root/usr/share/omarchy-ppp/installed-packages.txt" "$work/installed-packages.txt"
  umount "$root/var/cache/pacman/pkg"
  # Drop this bind from cleanup, then remove only the base image's old cache.
  unset "mounts[$((${#mounts[@]}-1))]"
  find "$root/var/cache/pacman/pkg" -maxdepth 1 -type f -delete
  stop_key_agents
  umount "$root/etc/pacman.d/gnupg"
  unset "mounts[$((${#mounts[@]}-1))]"
  rmdir "$root/etc/pacman.d/gnupg"
  python3 image/audit.py "$root" --clean
  cleanup
  trap - EXIT
  rootloop=$(losetup --find --show --offset $((251904*512)) \
    --sizelimit "$(jq '.partitiontable.partitions[1].size * 512' "$work/partition-after.json")" "$disk")
  bootloop=$(losetup --find --show --offset $((2048*512)) --sizelimit $((249856*512)) "$disk")
  trap 'losetup -d "$rootloop" "$bootloop"' EXIT
  e2fsck -fn "$rootloop"
  fsck.fat -n "$bootloop"
  losetup -d "$rootloop" "$bootloop"
  trap - EXIT
  stamp=$(date -u +%Y%m%dT%H%M%SZ)
  output=/src/image/out/omarchy-on-ppp-$stamp.img.xz
  xz -T2 -3 -c "$disk" > "$output.partial"
  mv "$output.partial" "$output"
  (cd /src/image/out && sha256sum "${output##*/}") > "$output.sha256"
  cp "$work/installed-packages.txt" "$output.packages.txt"
  cp "$work/configuration.json" "$output.configuration.json"
  rm -f "$disk"
  echo "IMAGE_BUILT: $output (hardware untested)"
fi
