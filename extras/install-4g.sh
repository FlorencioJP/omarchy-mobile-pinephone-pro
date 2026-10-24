#!/bin/bash
set -euo pipefail
[[ $EUID == 0 && $(uname -m) == aarch64 ]]
root=$(cd -- "$(dirname -- "$0")" && pwd)/4g-packages
python3 - "$root" <<'PY'
import hashlib,json,pathlib,subprocess,sys
root=pathlib.Path(sys.argv[1])
packages=json.loads((root/'packages.lock.json').read_text())
assert {p['name'] for p in packages} == {'libnma-common','libnma','nm-connection-editor'}
assert len(packages)==3
for p in packages:
    assert p['file']==f"{p['name']}-{p['version']}-aarch64.pkg.tar.xz"
    assert hashlib.sha256((root/p['file']).read_bytes()).hexdigest()==p['sha256']
    installed=subprocess.run(['pacman','-Q',p['name']],capture_output=True,text=True)
    assert installed.returncode or installed.stdout.strip()==p['name']+' '+p['version']
print('LOCK_OK')
PY
temporary=$(mktemp)
trap 'rm -f "$temporary"' EXIT
awk '/^[[:space:]]*LocalFileSigLevel[[:space:]]*=/ {next}
     {print}
     /^\[options\]$/ {print "LocalFileSigLevel = Required"}' /etc/pacman.conf > "$temporary"
pacman-conf --config "$temporary" LocalFileSigLevel | grep -qx PackageRequired
pacman --config "$temporary" -U --needed "$root"/*.pkg.tar.xz
pacman -Q libnma-common libnma nm-connection-editor
