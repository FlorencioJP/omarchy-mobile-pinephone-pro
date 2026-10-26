#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Fetch immutable public image inputs; never execute downloaded code."""
import hashlib
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import subprocess
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "cache/image"


def digest(path):
    with path.open("rb") as source:
        return hashlib.file_digest(source, "sha256").hexdigest()


def fetch(url, path, sha256, size=None):
    if path.is_symlink():
        raise ValueError(f"Refusing a symlink: {path}")
    if path.is_file() and digest(path) == sha256:
        return
    partial = path.with_name(path.name + ".partial")
    if partial.exists() or partial.is_symlink():
        raise ValueError(f"Remove the incomplete download before retrying: {partial}")
    try:
        with urlopen(url, timeout=60) as source, partial.open("xb") as target:
            while chunk := source.read(1024 * 1024):
                target.write(chunk)
        if (size is not None and partial.stat().st_size != size) or digest(partial) != sha256:
            raise ValueError(f"Hash or size mismatch: {url}")
        partial.replace(path)
    finally:
        partial.unlink(missing_ok=True)


def checkout(spec, destination):
    if not destination.exists():
        subprocess.run(["git", "init", "--quiet", str(destination)], check=True)
        subprocess.run(["git", "-C", str(destination), "remote", "add", "origin", spec["url"]], check=True)
    actual = subprocess.check_output(["git", "-C", str(destination), "remote", "get-url", "origin"], text=True).strip()
    if actual != spec["url"]:
        raise ValueError(f"Unexpected source remote: {destination}")
    if subprocess.check_output(["git", "-C", str(destination), "status", "--porcelain"], text=True).strip():
        raise ValueError(f"Source checkout has local changes: {destination}")
    head = subprocess.run(["git", "-C", str(destination), "rev-parse", "HEAD"], capture_output=True, text=True)
    if head.returncode == 0 and head.stdout.strip() == spec["commit"]:
        return
    subprocess.run(["git", "-C", str(destination), "fetch", "--depth=1", "origin", spec["commit"]], check=True)
    subprocess.run(["git", "-C", str(destination), "checkout", "--quiet", "--detach", spec["commit"]], check=True)
    actual = subprocess.check_output(["git", "-C", str(destination), "rev-parse", "HEAD"], text=True).strip()
    if actual != spec["commit"]:
        raise ValueError(f"Source revision mismatch: {destination}")


def main():
    spec = json.loads((ROOT / "image/inputs.json").read_text())
    CACHE.mkdir(parents=True, exist_ok=True)
    base = spec["base"]
    fetch(base["url"], CACHE / "base.img.xz", base["sha256"], base["size"])
    fetch(base["url"] + ".sig", CACHE / "base.img.xz.sig", base["signature_sha256"])
    fetch(base["key_url"], CACHE / "base-signing-key.asc", base["key_sha256"])
    for name in ("mobile", "omarchy_pkgs", "danctnix_pkgs"):
        checkout(spec[name], CACHE / name)
    lock = ROOT / "image/packages.lock.json"
    if lock.exists():
        from lock import package_row
        packages = json.loads(lock.read_text())["packages"]
        (CACHE / "packages").mkdir(exist_ok=True)
        def download(p):
            row = package_row("|".join(p[k] for k in ("repo", "name", "version", "arch", "url")))
            if row["filename"] != p["filename"]:
                raise ValueError("Package filename differs from its URL")
            path = CACHE / "packages" / p["filename"]
            fetch(p["url"], path, p["sha256"], p["size"])
            fetch(p["url"] + ".sig", Path(str(path) + ".sig"), p["signature_sha256"])
        with ThreadPoolExecutor(max_workers=4) as pool:
            list(pool.map(download, packages))
        print(f"{len(packages)} locked package archives and signatures verified.", flush=True)
    print("Public inputs fetched and pinned; image signature verification is required before preparation.")


if __name__ == "__main__":
    main()
