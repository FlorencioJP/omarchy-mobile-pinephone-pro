"""Vérifie le correctif sans écrire dans le sysfs réel ni accéder au téléphone."""
from pathlib import Path
import subprocess
import tempfile

unit = Path(__file__).resolve().parents[1] / "overlay/etc/systemd/system/omarchy-ppp-console.service"
commands = [
    line.split(" -c '", 1)[1][:-1]
    for line in unit.read_text().splitlines()
    if line.startswith("ExecStart=-/usr/bin/sh -c ")
]
assert len(commands) == 2
for command in commands:
    subprocess.run(["sh", "-n", "-c", command], check=True)

with tempfile.TemporaryDirectory() as temporary:
    root = Path(temporary)
    device = root / "sys/bus/i2c/devices/5-0015"
    driver = root / "sys/bus/i2c/drivers/pinephone-keyboard"
    driver.mkdir(parents=True)
    bind = driver / "bind"
    bind.write_text("")
    command = commands[0].replace("/sys/", temporary + "/sys/")
    subprocess.run(["sh", "-c", command], check=True)
    assert bind.read_text() == ""  # Aucun périphérique : ne pas demander de liaison.
    device.mkdir(parents=True)
    subprocess.run(["sh", "-c", command], check=True)
    assert bind.read_text() == "5-0015\n"
    bind.write_text("")
    (device / "driver").symlink_to(driver)
    subprocess.run(["sh", "-c", command], check=True)
    assert bind.read_text() == ""  # Ne pas toucher à un clavier déjà lié.
    rotation = root / "sys/class/graphics/fbcon/rotate_all"
    rotation.parent.mkdir(parents=True)
    rotation.write_text("0")
    subprocess.run(["sh", "-c", commands[1].replace("/sys/", temporary + "/sys/")], check=True)
    assert rotation.read_text() == "1\n"

print("Console : syntaxe shell et quatre cas simulés réussis.")
