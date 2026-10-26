#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Record a resolved package transaction and verify it before offline use."""
import json
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import urlsplit

from fetch import ROOT, CACHE, digest
from verify import check_file

ALLOWED_HOSTS = {"archmobile.mirror.danctnix.org", "de3.mirror.archlinuxarm.org", "pkgs.omarchy.org"}


def package_row(line):
    repo, name, version, arch, url = line.strip().split("|")
    parts = urlsplit(url)
    filename = Path(parts.path).name
    if parts.scheme != "https" or parts.hostname not in ALLOWED_HOSTS or parts.query or parts.fragment:
        raise ValueError(f"Unexpected package URL: {url}")
    if not re.fullmatch(r"[a-zA-Z0-9@._+:-]+\.pkg\.tar\.(xz|zst|gz)", filename):
        raise ValueError(f"Invalid package filename: {filename}")
    if arch not in ("aarch64", "any"):
        raise ValueError(f"Wrong architecture: {name}: {arch}")
    if name in ("linux", "linux-aarch64", "linux-asahi", "linux-lts", "grub", "limine", "m1n1") or name.startswith(("u-boot", "tow-boot", "omamobile-device-")):
        raise ValueError(f"Unexpected kernel/bootloader package: {name}")
    return dict(repo=repo, name=name, version=version, arch=arch, url=url, filename=filename)


def signature(package, keyring):
    archive = CACHE / "packages" / package["filename"]
    result = subprocess.run(["gpgv", "--status-fd", "1", "--keyring", str(keyring),
                             str(archive) + ".sig", str(archive)], check=True, capture_output=True, text=True)
    signatures = [line.split() for line in result.stdout.splitlines() if line.startswith("[GNUPG:] VALIDSIG ")]
    if len(signatures) != 1:
        raise ValueError(f"Missing unique valid package signature: {archive.name}")
    return signatures[0][-1]


def metadata(archive):
    text = subprocess.check_output(["bsdtar", "-xOf", str(archive), ".PKGINFO"], text=True)
    result = {}
    for line in text.splitlines():
        if " = " in line:
            key, value = line.split(" = ", 1)
            result.setdefault(key, []).append(value)
    return result


def conflict_applies(expression, versions, compare):
    name, operator, version = re.fullmatch(r"([^<>=]+)([<>=]+)?(.*)", expression).groups()
    if name not in versions:
        return False
    if not operator:
        return True
    result = compare(versions[name], version)
    return {"<": result < 0, "<=": result <= 0, "=": result == 0,
            ">=": result >= 0, ">": result > 0}[operator]


def main():
    verify = sys.argv[1] == "--verify"
    root = Path(sys.argv[2] if verify else sys.argv[1])
    keyring = root / "etc/pacman.d/gnupg/pubring.gpg"
    inputs = {name: digest(ROOT / "image" / name) for name in ("inputs.json", "packages.txt", "pacman.conf")}
    if verify:
        lock = json.loads((ROOT / "image/packages.lock.json").read_text())
        if lock["inputs"] != inputs:
            raise ValueError("Package lock inputs have changed; prepare and review a new transaction")
        installed = dict(line.rsplit(" ", 1) for line in subprocess.check_output(
            ["chroot", str(root), "pacman", "-Q"], text=True).splitlines())
        final_versions = installed | {p["name"]: p["version"] for p in lock["packages"]}
        def compare(a, b):
            return int(subprocess.check_output(["chroot", str(root), "vercmp", a, b], text=True))
        conflicts = set()
        for p in lock["packages"]:
            parsed = package_row("|".join(p[k] for k in ("repo", "name", "version", "arch", "url")))
            if parsed["filename"] != p["filename"]:
                raise ValueError("Package filename does not match URL")
            check_file(CACHE / "packages" / p["filename"], p["sha256"])
            check_file(CACHE / "packages" / (p["filename"] + ".sig"), p["signature_sha256"])
            if signature(p, keyring) != p["signer"]:
                raise ValueError("Package signer changed")
            for conflict in metadata(CACHE / "packages" / p["filename"]).get("conflict", []):
                name = re.split(r"[<>=]", conflict, maxsplit=1)[0]
                if name in installed and name != p["name"] and conflict_applies(conflict, final_versions, compare):
                    conflicts.add((p["name"], name))
        allowed = {("alsa-ucm-conf", "alsa-ucm-pinephonepro"), ("ex-vi-compat", "vi")}
        if not conflicts <= allowed:
            raise ValueError(f"Unreviewed package conflicts: {sorted(conflicts - allowed)}")
        print(f"Reviewed conflict transitions: {sorted(conflicts)}", flush=True)
        print(f"VERIFIED: {len(lock['packages'])} locked signed packages", flush=True)
        return
    packages = [package_row(line) for line in (CACHE / "transaction.txt").read_text().splitlines() if "|" in line]
    if not packages or len({p['name'] for p in packages}) != len(packages):
        raise ValueError("Empty or duplicate package transaction")
    reviews = []
    for p in packages:
        archive = CACHE / "packages" / p["filename"]
        p["sha256"], p["size"] = digest(archive), archive.stat().st_size
        p["signature_sha256"] = digest(Path(str(archive) + ".sig"))
        p["signer"] = signature(p, keyring)
        meta = metadata(archive)
        if any(meta[k] != [p[field]] for k, field in (("pkgname", "name"), ("pkgver", "version"), ("arch", "arch"))):
            raise ValueError(f"Package metadata mismatch: {archive.name}")
        p["licenses"] = meta.get("license", [])
        p["depends"] = meta.get("depend", [])
        members = subprocess.check_output(["bsdtar", "-tf", str(archive)], text=True).splitlines()
        for member in members:
            if member == ".INSTALL" or member.endswith(".hook"):
                body = subprocess.check_output(["bsdtar", "-xOf", str(archive), member], text=True)
                reviews.append(f"\n## {p['name']} {p['version']}: {member}\n{body}")
    review = CACHE / "review.txt"
    review.write_text("# Package scriptlets and hooks for review\n" + "".join(reviews))
    lock = {"schema": 1, "inputs": inputs, "review_sha256": digest(review), "packages": packages}
    (CACHE / "packages.candidate.json").write_text(json.dumps(lock, indent=2) + "\n")
    print(f"CANDIDATE: {len(packages)} signed packages, {len(reviews)} scriptlets/hooks", flush=True)


if __name__ == "__main__":
    main()
