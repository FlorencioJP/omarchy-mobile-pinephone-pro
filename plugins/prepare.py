#!/usr/bin/env python3
"""Download pinned sources and apply the mobile panel adaptations, without installing."""
import hashlib
import json
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import tarfile
from tempfile import TemporaryDirectory
from urllib.request import urlopen


def extract(archive, destination):
    with tarfile.open(archive) as stream:
        for member in stream.getmembers():
            parts = PurePosixPath(member.name).parts
            if member.name.startswith('/') or '..' in parts or not (member.isfile() or member.isdir()):
                raise ValueError('Unsafe archive entry: ' + member.name)
            if len(parts) < 2:
                continue
            path = destination.joinpath(*parts[1:])
            if member.isdir():
                path.mkdir(parents=True, exist_ok=True)
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(stream.extractfile(member).read())
                path.chmod(member.mode & 0o755)


def main():
    root = Path(__file__).resolve().parent
    target = root / 'selected-plugins'
    if target.exists():
        raise SystemExit('selected-plugins already exists; preserve any local changes before rebuilding.')
    if not shutil.which('patch'):
        raise SystemExit('The patch command is required.')
    cache = root / 'cache'
    cache.mkdir(exist_ok=True)
    plugins = json.loads((root / 'plugins.lock.json').read_text())
    with TemporaryDirectory(dir=root) as directory:
        build = Path(directory) / 'selected-plugins'
        build.mkdir()
        for plugin in plugins:
            archive = cache / (plugin['id'] + '.tgz')
            if not archive.exists():
                repo = plugin['repository'].removeprefix('https://github.com/')
                url = f'https://codeload.github.com/{repo}/tar.gz/{plugin["commit"]}'
                with urlopen(url, timeout=60) as response:
                    archive.write_bytes(response.read())
            if hashlib.sha256(archive.read_bytes()).hexdigest() != plugin['archive_sha256']:
                raise ValueError('Archive checksum mismatch: ' + plugin['id'])
            destination = build / plugin['id']
            extract(archive, destination)
            manifest = json.loads((destination / 'manifest.json').read_text())
            if manifest['id'] != plugin['id'] or manifest['version'] != plugin['version']:
                raise ValueError('Manifest mismatch: ' + plugin['id'])
        subprocess.run(['patch', '--batch', '-p1', '-d', str(build),
                        '-i', str(root / 'adaptations.patch')], check=True)
        build.replace(target)
    print('PINNED_MOBILE_PLUGINS_PREPARED')


if __name__ == '__main__':
    main()
