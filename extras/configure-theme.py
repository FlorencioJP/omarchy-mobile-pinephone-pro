#!/usr/bin/env python3
"""Raccorder le thème Omarchy existant au profil mobile et à Foot."""
import os
from pathlib import Path
import shutil
import subprocess

home = Path.home()
config = Path(os.environ.get('XDG_CONFIG_HOME', home / '.config'))
theme = home / '.local/state/omarchy/current/theme'
assert (theme / 'foot.ini').is_file() and (theme / 'hyprland.lua').is_file()
source = Path(__file__).with_name('theme.lua')
subprocess.run(['luac5.4', '-p', str(source)], check=True)
target = config / 'omarchy-ppp/theme.lua'
shutil.copyfile(source, target)
target.chmod(0o600)

def replace_checked(path, text, validator):
    backup = path.with_name(path.name + '.before-mobile-theme')
    if not backup.exists():
        shutil.copy2(path, backup)
    temporary = path.with_name(path.name + '.mobile-theme-new')
    try:
        temporary.write_text(text)
        temporary.chmod(0o600)
        subprocess.run([*validator, str(temporary)], check=True)
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)

foot = config / 'foot/foot.ini'
text = foot.read_text()
include = 'include=' + str(theme / 'foot.ini')
if include not in text.splitlines():
    assert text.count('[main]') == 1
    text = text.replace('[main]', '[main]\n' + include, 1)
    replace_checked(foot, text, ['foot', '--check-config', '--config'])

local = config / 'omarchy-ppp/local.lua'
text = local.read_text()
line = "dofile((os.getenv('XDG_CONFIG_HOME') or os.getenv('HOME') .. '/.config') .. '/omarchy-ppp/theme.lua')"
if line not in text.splitlines():
    replace_checked(local, text + '\n' + line + '\n', ['luac5.4', '-p'])
print('MOBILE_THEME_CONFIGURED')
