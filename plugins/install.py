#!/usr/bin/env python3
"""Activer six panneaux locaux ; conserver deux widgets en attente."""
import json
from pathlib import Path
import shutil

root = Path(__file__).resolve().parent
lock = json.loads((root / 'plugins.lock.json').read_text())
assert len(lock) == 8 and len({p['id'] for p in lock}) == 8
directory = Path.home() / '.config/omarchy/plugins'
shell = Path.home() / '.config/omarchy/shell.json'
menu = Path.home() / '.config/omarchy/extensions/omarchy-menu.jsonc'
config = json.loads(shell.read_text())
items = json.loads(menu.read_text())
enabled = {p['id'] for p in config['plugins']}
titles = {'io.github.sahzudin.omassh': 'SSH · machines distantes',
          'andreconde.tmux': 'tmux distant · à configurer',
          'network-speed': 'Débit réseau', 'io.github.woogy7.vitals': 'Moniteur système',
          'nino.tailscale': 'Tailscale · client requis', 'remco.wireguard': 'WireGuard'}
for entry in lock:
    identifier = entry['id']
    source = root / 'selected-plugins' / identifier
    manifest = json.loads((source / 'manifest.json').read_text())
    assert manifest['id'] == identifier
    target = directory / identifier
    assert not target.exists() or target.resolve() == source.resolve(), identifier
for path in (shell, menu):
    backup = path.with_name(path.name + '.before-selected-plugins')
    if not backup.exists():
        shutil.copy2(path, backup)
items.setdefault('pinephone', {'icon': '', 'label': 'PinePhone'})
items['pinephone.extensions'] = {'icon': '󰏗', 'label': 'Extensions'}
for entry in lock:
    identifier = entry['id']
    target = directory / identifier
    if not target.exists():
        target.symlink_to(root / 'selected-plugins' / identifier)
    if entry['mobile_panel']:
        if identifier not in enabled:
            config['plugins'].append({'id': identifier})
        items['pinephone.extensions.' + identifier.replace('.', '-')] = {
            'label': titles[identifier],
            'action': 'omarchy-shell shell summon ' + identifier}
for path, data in ((shell, config), (menu, items)):
    temporary = path.with_name(path.name + '.selected-plugins-new')
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
    temporary.chmod(0o600)
    temporary.replace(path)
print('LOCAL_PLUGIN_LINKS_AND_MENU_READY')
