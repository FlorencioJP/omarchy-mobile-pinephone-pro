"""Install twice in an isolated home; preserve unrelated settings and backups."""
import json
import os
from pathlib import Path
import shutil
import subprocess
from tempfile import TemporaryDirectory

repository = Path(__file__).resolve().parents[1]
with TemporaryDirectory() as directory:
    root = Path(directory)
    home = root / 'home'
    config = home / '.config/omarchy'
    (config / 'plugins').mkdir(parents=True)
    (config / 'extensions').mkdir()
    shell = {'bar': {'id': 'omamobile.bar'}, 'plugins': [{'id': 'omarchy.menu'}],
             'idle': {'screensaver': 0, 'lock': 0}}
    menu = {'personal': {'label': 'Keep me'}}
    (config / 'shell.json').write_text(json.dumps(shell))
    (config / 'extensions/omarchy-menu.jsonc').write_text(json.dumps(menu))
    shutil.copyfile(repository / 'plugins/install.py', root / 'install.py')
    shutil.copyfile(repository / 'plugins/plugins.lock.json', root / 'plugins.lock.json')
    lock = json.loads((root / 'plugins.lock.json').read_text())
    for entry in lock:
        source = root / 'selected-plugins' / entry['id']
        source.mkdir(parents=True)
        (source / 'manifest.json').write_text(json.dumps({'id': entry['id']}))
    for _ in range(2):
        subprocess.run(['python3', str(root / 'install.py')], env=os.environ | {'HOME': str(home)}, check=True)
    installed = json.loads((config / 'shell.json').read_text())
    assert installed['bar'] == shell['bar'] and installed['idle'] == shell['idle']
    assert len(installed['plugins']) == 7
    items = json.loads((config / 'extensions/omarchy-menu.jsonc').read_text())
    assert items['personal'] == menu['personal'] and 'pinephone' in items
    assert len(list((config / 'plugins').iterdir())) == 8
    assert json.loads((config / 'shell.json.before-selected-plugins').read_text()) == shell
print('PLUGIN_INSTALL_CHECKS_OK')
