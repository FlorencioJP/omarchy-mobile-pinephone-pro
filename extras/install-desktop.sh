#!/bin/bash
set -euo pipefail
[[ $EUID == 0 && $(uname -m) == aarch64 ]]
source_dir=$(cd -- "$(dirname -- "$0")" && pwd)
bash "$source_dir/install-4g.sh"
python3 - <<'PY'
from pathlib import Path
import shutil,subprocess
profile=Path('/usr/share/omarchy-ppp/hypr/hyprland.lua')
text=profile.read_text()
line="  hl.exec_cmd('foot')\n"
assert text.count(line) in (0,1)
if line in text:
    backup=profile.with_name('hyprland.lua.before-desktop')
    if not backup.exists(): shutil.copy2(profile,backup)
    temporary=profile.with_name('hyprland.lua.desktop-new')
    try:
        temporary.write_text(text.replace(line,''))
        temporary.chmod(0o644)
        subprocess.run(['luac5.4','-p',str(temporary)],check=True)
        temporary.replace(profile)
    finally:
        temporary.unlink(missing_ok=True)
print('DESKTOP_AUTOSTART_READY')
PY
