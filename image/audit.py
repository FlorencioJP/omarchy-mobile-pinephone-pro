#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Software gates for a staged image; these do not replace a phone test."""
from pathlib import Path
import gzip
import hashlib
import json
import shutil
import subprocess
import sys


def configuration_manifest(root):
    paths = set()
    for pattern in ('usr/share/omarchy-ppp', 'usr/share/sddm/themes/omarchy-ppp',
                    'usr/lib/omarchy-ppp', 'usr/bin/ppp-*', 'usr/bin/start-omarchy-ppp',
                    'etc/sddm.conf.d', 'etc/sudoers.d', 'etc/mkinitcpio.conf*',
                    'etc/fstab', 'etc/systemd/system', 'boot/boot.txt',
                    'home/terminal/.config', 'home/terminal/.local/state/omarchy/current'):
        for path in root.glob(pattern):
            paths.add(path)
            if path.is_dir() and not path.is_symlink():
                paths.update(path.rglob('*'))
    result = {}
    for path in sorted(paths):
        stat = path.lstat()
        row = {'mode': oct(stat.st_mode & 0o7777), 'uid': stat.st_uid, 'gid': stat.st_gid}
        if path.is_symlink(): row['link'] = str(path.readlink())
        elif path.is_file(): row['sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
        result[str(path.relative_to(root))] = row
    return result


def audit(root):
    def run(*args):
        result = subprocess.run(['chroot', str(root), *args], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if result.returncode:
            print(result.stdout, flush=True)
            result.check_returncode()
        return result.stdout

    packages = run('pacman', '-Q')
    assert 'linux-megi ' in packages and 'device-pine64-pinephonepro ' in packages
    assert 'omarchy ' in packages and 'hyprland ' in packages and 'quickshell ' in packages
    kernels = list((root / 'usr/lib/modules').iterdir())
    assert len(kernels) == 1 and 'megi' in kernels[0].name
    assert kernels[0].name.encode() in gzip.decompress((root / 'boot/Image.gz').read_bytes())
    assert kernels[0].name in run('lsinitcpio', '-l', '/boot/initramfs-linux.img')
    for file in ('boot/Image.gz', 'boot/initramfs-linux.img', 'boot/boot.scr',
                 'boot/dtbs/rockchip/rk3399-pinephone-pro.dtb'):
        assert (root / file).is_file(), file
    boot = (root / 'boot/boot.txt').read_text()
    assert 'root=UUID=2d767a2c-b7d5-5680-b28c-ec8854a09fc1' in boot
    assert 'root=/dev/mmcblk' not in boot
    shadow = dict(line.split(':', 2)[:2] for line in (root / 'etc/shadow').read_text().splitlines())
    assert shadow['root'] == shadow['terminal'] == '!'
    assert 'alarm' not in shadow
    assert not (root / 'var/lib/omarchy-ppp/provisioned').exists()
    helper = (root / 'usr/lib/omarchy-ppp/set-password').stat()
    assert helper.st_uid == 0 and helper.st_mode & 0o022 == 0
    for file in (root / 'usr/share/omarchy-ppp/hypr').glob('*.lua'):
        run('luac5.4', '-p', '/' + str(file.relative_to(root)))
    run('visudo', '-c')
    run('pacman', '-Dk')
    temporary = root / 'tmp/ppp-build-tests'
    shutil.copytree('/src/tests', temporary / 'tests')
    shutil.copytree('/src/overlay', temporary / 'overlay')
    print(run('python3', '/tmp/ppp-build-tests/tests/image-keymap.py', '/usr/share/omarchy-ppp/keyboard.xkb'))
    # SDDM 0.21 enumerates Wayland sessions only when this directory exists.
    # An empty test fixture exercises its model; it does not emulate a GPU.
    (root / 'dev/dri').mkdir(exist_ok=True)
    print(run('bash', '/tmp/ppp-build-tests/tests/sddm-session.sh'))
    (root / 'dev/dri').rmdir()
    runtime = '/run/ppp-config-check'
    run('install', '-d', '-m700', '-o', 'terminal', '-g', 'terminal', runtime)
    print(run('runuser', '-u', 'terminal', '--', 'env', 'OMARCHY_PATH=/usr/share/omarchy',
              'XDG_RUNTIME_DIR=' + runtime,
              'Hyprland', '--verify-config', '--config', '/usr/share/omarchy-ppp/hypr/hyprland.lua'))
    shutil.rmtree(root / runtime.lstrip('/'))
    shutil.rmtree(temporary)
    print('STAGED_SOFTWARE_AUDIT_PASSED (hardware untested)', flush=True)


def clean_audit(root):
    assert not list((root/'usr/lib/omarchy-ppp').rglob('__pycache__'))
    assert not (root/'etc/pacman.d/gnupg').exists()
    assert not list((root/'etc/ssh').glob('ssh_host_*'))
    assert not list((root/'etc/NetworkManager/system-connections').glob('*'))
    assert not (root/'etc/machine-id').read_text().strip()
    assert not (root/'etc/shadow-').exists()
    for line in (root/'etc/shadow').read_text().splitlines():
        assert line.split(':')[1] in ('!', '!!', '*', '!*'), 'Unexpected credential in image'
    for path in (root/'etc/systemd/system').rglob('*'):
        assert not (path.is_symlink() and path.name in ('sshd.service','sshd.socket') and path.readlink()!=Path('/dev/null'))
    (root.parent/'configuration.json').write_text(json.dumps(configuration_manifest(root), indent=2, sort_keys=True)+'\n')
    print('CLEAN_IMAGE_AUDIT_PASSED', flush=True)


if __name__ == '__main__':
    if len(sys.argv) == 3 and sys.argv[2] == '--clean':
        clean_audit(Path(sys.argv[1]))
    else:
        audit(Path(sys.argv[1]))
