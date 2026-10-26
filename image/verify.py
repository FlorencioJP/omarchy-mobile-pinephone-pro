#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Authenticate public build inputs before executing any target code."""
import json
from pathlib import Path
import subprocess
import tempfile

from fetch import ROOT, CACHE, digest


def check_file(path, expected):
    if path.is_symlink() or not path.is_file() or digest(path) != expected:
        raise ValueError(f"Missing or modified input: {path}")


def verify_base():
    base = json.loads((ROOT / "image/inputs.json").read_text())["base"]
    for name, field in (("base.img.xz", "sha256"), ("base.img.xz.sig", "signature_sha256"),
                        ("base-signing-key.asc", "key_sha256")):
        check_file(CACHE / name, base[field])
    with tempfile.TemporaryDirectory() as home:
        subprocess.run(["gpg", "--homedir", home, "--batch", "--import",
                        str(CACHE / "base-signing-key.asc")], check=True, capture_output=True)
        result = subprocess.run(["gpg", "--homedir", home, "--batch", "--status-fd", "1",
                                 "--verify", str(CACHE / "base.img.xz.sig"),
                                 str(CACHE / "base.img.xz")], check=True, capture_output=True, text=True)
        signatures = [line.split() for line in result.stdout.splitlines()
                      if line.startswith("[GNUPG:] VALIDSIG ")]
        if len(signatures) != 1 or signatures[0][-1] != base["signer"]:
            raise ValueError("Base signature does not match the published release key")
    spec = json.loads((ROOT / "image/inputs.json").read_text())
    for name in ("mobile", "omarchy_pkgs", "danctnix_pkgs"):
        head = subprocess.check_output(["git", "-C", str(CACHE / name), "rev-parse", "HEAD"], text=True).strip()
        status = subprocess.check_output(["git", "-C", str(CACHE / name), "status", "--porcelain", "--ignored"], text=True)
        if head != spec[name]["commit"] or status.strip():
            raise ValueError(f"Changed pinned source: {name}")
    print("BASE_SIGNATURE_AND_SOURCES_VERIFIED", flush=True)


if __name__ == "__main__":
    verify_base()
