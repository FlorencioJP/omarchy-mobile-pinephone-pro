#!/usr/bin/python3
"""Télécharger le lot figé et vérifier ses empreintes et signatures, sans sudo."""
from concurrent.futures import ThreadPoolExecutor
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
from urllib.parse import urlsplit
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parent
CACHE = ROOT / "cache"
KEYRING = CACHE / "archlinuxarm.gpg"


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def fetch(package):
    url = urlsplit(package["url"])
    if url.hostname not in ("mirror.archlinuxarm.org", "archmobile.mirror.danctnix.org"):
        raise ValueError("Source de paquet inattendue")
    if package["arch"] not in ("aarch64", "any"):
        raise ValueError("Architecture incompatible")
    CACHE.mkdir(exist_ok=True)
    archive = CACHE / Path(url.path).name
    if not archive.exists() or digest(archive) != package["sha256"]:
        partial = archive.with_name(archive.name + ".partial")
        with urlopen(package["url"], timeout=60) as source, partial.open("wb") as target:
            while chunk := source.read(1024 * 1024):
                target.write(chunk)
        if partial.stat().st_size != package["size"] or digest(partial) != package["sha256"]:
            raise ValueError("Empreinte ou taille incorrecte : " + package["name"])
        partial.replace(archive)
    signature = archive.with_name(archive.name + ".sig")
    with urlopen(package["url"] + ".sig", timeout=60) as source:
        signature.write_bytes(source.read())
    result = subprocess.run(
        ["gpgv", "--keyring", str(KEYRING), str(signature), str(archive)],
        stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
    )
    if result.returncode:
        raise RuntimeError(result.stderr.decode(errors="replace"))
    return package["name"]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--terminal", action="store_true", help="Télécharger le complément terminal")
    args = parser.parse_args()
    manifest = "terminal.packages.lock.json" if args.terminal else "packages.lock.json"
    packages = json.loads((ROOT / manifest).read_text())["packages"]
    CACHE.mkdir(exist_ok=True)
    subprocess.run(["gpg", "--batch", "--yes", "--dearmor", "--output", str(KEYRING),
                    "/usr/share/pacman/keyrings/archlinuxarm.gpg"], check=True)
    with ThreadPoolExecutor(max_workers=4) as pool:
        for count, name in enumerate(pool.map(fetch, packages), 1):
            if count % 20 == 0 or count == len(packages):
                print(f"{count}/{len(packages)} paquets vérifiés ({name})", flush=True)
    print("DOWNLOAD_COMPLETE", flush=True)
