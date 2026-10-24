"""Le complément terminal doit rester ARM64, borné et sans remplacement du socle."""
import json
import contextlib
import hashlib
import io
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
from unittest.mock import patch
from urllib.parse import urlsplit

root = Path(__file__).resolve().parents[1]
packages = json.loads((root / "terminal.packages.lock.json").read_text())["packages"]
names = {p["name"] for p in packages}
existing = {line.split()[0] for line in (root / "installed-before.txt").read_text().splitlines()}
existing.update(p["name"] for p in json.loads((root / "packages.lock.json").read_text())["packages"])
assert len(names) == len(packages) and not names.intersection(existing)
assert {"tmux", "neovim", "rsync", "ripgrep", "fzf", "less"} <= names
assert sum(p["installed_size"] for p in packages) < 200 * 1024**2
for package in packages:
    assert package["arch"] in ("aarch64", "any")
    assert urlsplit(package["url"]).hostname == "mirror.archlinuxarm.org"
    assert len(package["sha256"]) == 64 and int(package["sha256"], 16) >= 0
    assert package["size"] > 0 and package["installed_size"] > 0
    assert package["licenses"]
    assert not package["name"].startswith(("linux", "u-boot", "tow-boot", "mkinitcpio"))
print(f"Complément terminal : {len(packages)} paquets, architectures et périmètre contrôlés.")

# Exécuter le validateur réel de l'installateur sans transaction pacman.
validator = (root / "install.sh").read_text().split("<<'PY'\n", 1)[1].split("\nPY\n", 1)[0]
with tempfile.TemporaryDirectory() as directory:
    temporary = Path(directory)
    (temporary / "cache").mkdir()
    package = dict(packages[0], name="test", version="1-1", size=3,
                   sha256=hashlib.sha256(b"abc").hexdigest(),
                   url="http://mirror.archlinuxarm.org/aarch64/extra/test.pkg.tar.xz")
    (temporary / "cache/test.pkg.tar.xz").write_bytes(b"abc")
    (temporary / "cache/test.pkg.tar.xz.sig").write_bytes(b"test")
    (temporary / "terminal.packages.lock.json").write_text(json.dumps({"packages": [package]}))
    for installed, allowed in (("", True), ("test 1-1\n", True), ("test 2-1\n", False)):
        result = SimpleNamespace(returncode=0 if installed else 1, stdout=installed)
        with patch.object(sys, "argv", ["install", directory, "terminal.packages.lock.json"]), \
             patch("subprocess.run", return_value=result), contextlib.redirect_stdout(io.StringIO()):
            try:
                exec(compile(validator, "install.sh:validator", "exec"), {})
            except SystemExit as error:
                assert not allowed and "Refus de remplacer" in str(error)
            else:
                assert allowed
print("Installateur : ajout, réexécution et refus de remplacement contrôlés.")
