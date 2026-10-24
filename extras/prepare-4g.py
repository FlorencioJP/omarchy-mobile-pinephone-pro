#!/usr/bin/env python3
"""Préparer trois paquets ARM64 signés ; aucune installation ni activation radio."""
import hashlib
import json
from pathlib import Path
import subprocess
from urllib.request import urlopen

root = Path(__file__).resolve().parent / '4g-packages'
root.mkdir(mode=0o700, exist_ok=True)
keyring = root / 'archlinuxarm.gpg'
subprocess.run(['gpg', '--batch', '--yes', '--dearmor', '--output', str(keyring),
                '/usr/share/pacman/keyrings/archlinuxarm.gpg'], check=True)
packages = json.loads(Path(__file__).with_name('4g.packages.lock.json').read_text())
for package in packages:
    filename = package['file']
    archive = root / filename
    for suffix in ('', '.sig'):
        with urlopen(package['url'] + suffix,
                     timeout=60) as response:
            (root / (filename + suffix)).write_bytes(response.read())
    if hashlib.sha256(archive.read_bytes()).hexdigest() != package['sha256']:
        raise ValueError('Archive checksum mismatch: ' + package['name'])
    subprocess.run(['gpgv', '--keyring', str(keyring), str(archive) + '.sig',
                    str(archive)], check=True)
(root / 'packages.lock.json').write_text(json.dumps(packages, indent=2) + '\n')
print('SIGNED_4G_PACKAGES_READY')
