#!/usr/bin/python3
# SPDX-License-Identifier: MIT
"""Adapter uniquement la racine et /boot d'une copie SD vers l'eMMC ext4."""
from pathlib import Path
import re
import sys
from uuid import UUID


def fstab(text, root_uuid, boot_uuid):
    identities = {"/": str(UUID(root_uuid)), "/boot": str(UUID(boot_uuid))}
    if identities["/"] == identities["/boot"]:
        raise ValueError("Racine et /boot doivent être distincts")
    found = []
    output = []
    for line in text.splitlines():
        fields = line.split()
        if fields and not fields[0].startswith("#") and len(fields) >= 2 and fields[1] in identities:
            if len(fields) != 6:
                raise ValueError("Entrée fstab inattendue")
            mount = fields[1]
            found.append(mount)
            fields[0] = "UUID=" + identities[mount]
            fields[2:4] = ["ext4", "rw,relatime"]
            line = "\t".join(fields)
        output.append(line)
    if sorted(found) != ["/", "/boot"]:
        raise ValueError("Racine et /boot doivent apparaître une seule fois")
    return "\n".join(output) + "\n"


def boot(text, root_uuid):
    root_uuid = str(UUID(root_uuid))
    if "encrypted.scr" in text:
        # La SD examinée n'est pas chiffrée ; ne pas lancer un ancien script Sailfish.
        pattern = r'if test -e mmc \$\{devnum\}:1 encrypted\.scr; then\n.*?\nelse\n(\s*setenv bootargs[^\n]+)\nfi'
        text, count = re.subn(pattern, lambda match: match[1], text, flags=re.S)
        if count != 1 or "encrypted.scr" in text:
            raise ValueError("Branche de chiffrement inconnue")
    text, count = re.subn(r'(?<!\S)root=(?:PARTUUID|UUID)=[^\s]+', "root=UUID=" + root_uuid, text)
    if count != 1:
        raise ValueError("Référence de racine ambiguë")
    text, count = re.subn(r'(?m)^(\s*setenv rootpart )2$', r'\g<1>3', text)
    if count != 1:
        raise ValueError("Sélection de partition inattendue")
    return text


def configure(root, root_uuid, boot_uuid):
    root = Path(root).resolve()
    for name in ("etc/fstab", "boot/boot.txt"):
        if not (root / name).resolve().is_relative_to(root):
            raise ValueError("Lien sortant de la copie cible")
    new_fstab = fstab((root / "etc/fstab").read_text(), root_uuid, boot_uuid)
    new_boot = boot((root / "boot/boot.txt").read_text(), root_uuid)
    (root / "etc/fstab").write_text(new_fstab)
    (root / "boot/boot.txt").write_text(new_boot)


if __name__ == "__main__":
    configure(sys.argv[1], sys.argv[2], sys.argv[3])
