"""Exercer les déplacements réels dans un dossier jetable, jamais sur un disque."""
from pathlib import Path
import subprocess
import tempfile

repository = Path(__file__).resolve().parents[1]
migration = (repository / 'migrate-emmc.sh').read_text()
forward = migration.split("echo 'PHASE=COMMIT_ROOT'\n", 1)[1].split('chmod --reference=/', 1)[0]
restore = (repository / 'restore-sailfish.sh').read_text()
backward = restore.split('mkdir -m700 "$backup/omarchy-root-before-restore"\n', 1)[1].split('chown "$owner:$group"', 1)[0]
backward = 'mkdir -m700 "$backup/omarchy-root-before-restore"\n' + backward
with tempfile.TemporaryDirectory() as temporary:
    root = Path(temporary)
    backup = root / '.omarchy-migration'
    stage = root / '.omarchy-root-stage'
    backup.mkdir()
    (root / 'defaultuser').mkdir()
    (root / 'defaultuser/private.txt').write_text('old home')
    (root / '.system').mkdir()
    (root / '.system/settings').write_text('old settings')
    (root / 'lost+found').mkdir()
    (backup / 'boot-before.img').write_text('backup unchanged')
    (stage / 'usr/bin').mkdir(parents=True)
    (stage / 'usr/bin/terminal').write_text('new system')
    arguments = ['bash', '-eu', '-c', 'root=$1; backup=$2; stage=$3;\n' + forward,
                 'test', str(root), str(backup), str(stage)]
    subprocess.run(arguments, check=True)
    assert not (root / 'defaultuser').exists()
    assert (backup / 'sailfish-home/defaultuser/private.txt').read_text() == 'old home'
    assert (backup / 'sailfish-home/.system/settings').read_text() == 'old settings'
    assert (root / 'usr/bin/terminal').read_text() == 'new system'
    subprocess.run(['bash', '-eu', '-c', 'work=$1; backup=$2;\n' + backward,
                    'test', str(root), str(backup)], check=True)
    assert (root / 'defaultuser/private.txt').read_text() == 'old home'
    assert (root / '.system/settings').read_text() == 'old settings'
    assert (backup / 'omarchy-root-before-restore/usr/bin/terminal').read_text() == 'new system'
    assert (backup / 'boot-before.img').read_text() == 'backup unchanged'
    assert (root / 'lost+found').is_dir()
print('eMMC : bascule et retour des dossiers testés, anciennes et nouvelles données conservées.')
