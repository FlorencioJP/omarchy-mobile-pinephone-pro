import json
from pathlib import Path
import re

root = Path(__file__).resolve().parents[1]
packages = json.loads((root / 'extras/4g.packages.lock.json').read_text())
assert len(packages) == 3
assert {p['name'] for p in packages} == {'libnma-common', 'libnma', 'nm-connection-editor'}
for package in packages:
    assert package['arch'] == 'aarch64'
    assert package['licenses'] and re.fullmatch('[a-f0-9]{64}', package['sha256'])
    assert package['file'] == f"{package['name']}-{package['version']}-aarch64.pkg.tar.xz"
    assert package['url'] == 'http://mirror.archlinuxarm.org/aarch64/extra/' + package['file']
assert 'LocalFileSigLevel = Required' in (root / 'extras/install-4g.sh').read_text()
print('CELLULAR_LOCK_OK')
