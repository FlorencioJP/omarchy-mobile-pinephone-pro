"""Refuser les racines ambiguës et retirer toute dépendance de démarrage à la SD."""
import importlib.util
from pathlib import Path
import tempfile

path = Path(__file__).resolve().parents[1] / "emmc-config.py"
spec = importlib.util.spec_from_file_location("emmc_config", path)
config = importlib.util.module_from_spec(spec)
spec.loader.exec_module(config)
root_uuid = "11111111-1111-4111-8111-111111111111"
boot_uuid = "22222222-2222-4222-8222-222222222222"
fstab = '# comment\nPARTUUID=old-root / ext4 rw,relatime 0 1\nPARTUUID=old-boot /boot vfat rw,fmask=0022 0 2\n'
new = config.fstab(fstab, root_uuid, boot_uuid)
assert "PARTUUID=" not in new and "vfat" not in new and "fmask" not in new
assert "UUID=" + root_uuid in new and "UUID=" + boot_uuid in new
script = '''setenv rootpart 2
if test -e mmc ${devnum}:1 encrypted.scr; then
  load mmc ${devnum}:1 ${loadaddr} encrypted.scr
  source ${loadaddr}
else
  setenv bootargs ${bootargs} root=PARTUUID=old-root
fi
booti ${kernel_addr_r} ${ramdisk_addr_r}:0x${ramdisk_size} ${fdt_addr_r}
'''
new = config.boot(script, root_uuid)
assert "encrypted.scr" not in new and "old-root" not in new
assert "setenv rootpart 3" in new and "root=UUID=" + root_uuid in new
assert script.splitlines()[-1] == new.splitlines()[-1]
for invalid in (fstab.replace('/ ext4', '/other ext4'), fstab + fstab):
    try:
        config.fstab(invalid, root_uuid, boot_uuid)
    except ValueError:
        pass
    else:
        raise AssertionError('fstab ambigu accepté')
for invalid in (script.replace('root=PARTUUID=old-root', 'quiet'), script + script):
    try:
        config.boot(invalid, root_uuid)
    except ValueError:
        pass
    else:
        raise AssertionError('boot ambigu accepté')
try:
    config.boot(script, 'bad; command')
except ValueError:
    pass
else:
    raise AssertionError('UUID non valide accepté')
with tempfile.TemporaryDirectory() as directory:
    target = Path(directory) / 'target'
    (target / 'etc').mkdir(parents=True)
    (target / 'boot').mkdir()
    outside = Path(directory) / 'outside-fstab'
    outside.write_text(fstab)
    (target / 'etc/fstab').symlink_to(outside)
    (target / 'boot/boot.txt').write_text(script)
    try:
        config.configure(target, root_uuid, boot_uuid)
    except ValueError:
        pass
    else:
        raise AssertionError('Lien sortant accepté')
    assert outside.read_text() == fstab
print('eMMC : références uniques, ext4, suppression du branchement chiffré et validation UUID vérifiées.')
