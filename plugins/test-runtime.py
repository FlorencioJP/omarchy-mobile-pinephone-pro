#!/usr/bin/env python3
"""Ouvrir/fermer les panneaux sans déclencher leurs actions réseau."""
import json
import os
from pathlib import Path
import subprocess
import time

root = Path(__file__).resolve().parent
os.environ.update(OMARCHY_PATH='/usr/share/omarchy',
                  XDG_RUNTIME_DIR=f'/run/user/{os.getuid()}', LANG='C.UTF-8')
instances = json.loads(subprocess.check_output(['hyprctl', '-j', 'instances']))
assert len(instances) == 1
os.environ['HYPRLAND_INSTANCE_SIGNATURE'] = instances[0]['instance']

def mapped(identifier):
    monitors = json.loads(subprocess.check_output(['hyprctl', '-j', 'layers']))
    return any(layer.get('namespace') == 'ppp-plugin-' + identifier
               for monitor in monitors.values() for group in monitor['levels'].values()
               for layer in group)

def call(*args):
    result = subprocess.run(['omarchy-shell', 'shell', *args],
                            capture_output=True, text=True, timeout=6)
    return result.stdout.strip()

results = []
(root / 'plugins-test-start.epoch').write_text(str(int(time.time())))
for plugin in json.loads((root / 'plugins.lock.json').read_text()):
    if not plugin['mobile_panel']:
        continue
    identifier = plugin['id']
    state = {}
    try:
        call('summon', identifier)
        for _ in range(16):
            time.sleep(0.25)
            try:
                state = json.loads(call('call', identifier, 'mobileState', ''))
            except json.JSONDecodeError:
                continue
            if state.get('opened') and mapped(identifier) and (identifier != 'io.github.woogy7.vitals' or state.get('collected')):
                break
        result = {'id': identifier, 'opened': state.get('opened') is True, 'state': state}
        result['mapped'] = mapped(identifier)
        if identifier == 'io.github.woogy7.vitals':
            result['collector_ready'] = state.get('collected') is True
    finally:
        call('hide', identifier)
    results.append(result)
    print(json.dumps(result), flush=True)
(root / 'plugins-runtime.json').write_text(json.dumps(results, indent=2) + '\n')
assert all(result['opened'] for result in results), 'Panneau non chargé : consulter les journaux.'
assert all(result['mapped'] for result in results), 'Surface Wayland absente.'
assert all(result.get('collector_ready', True) for result in results), 'Collecteur Vitals indisponible.'
