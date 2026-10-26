#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
import hashlib
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import io

spec = importlib.util.spec_from_file_location("image_fetch", Path(__file__).resolve().parents[1] / "image/fetch.py")
fetch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fetch)


class Downloads(unittest.TestCase):
    def test_download_and_cache(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "input"
            sha = hashlib.sha256(b"verified").hexdigest()
            with patch.object(fetch, "urlopen", return_value=io.BytesIO(b"verified")):
                fetch.fetch("https://example.invalid/input", path, sha, 8)
            with patch.object(fetch, "urlopen", side_effect=AssertionError("cache should be reused")):
                fetch.fetch("https://example.invalid/input", path, sha, 8)
            self.assertEqual(path.read_bytes(), b"verified")

    def test_bad_hash_does_not_replace_existing_file(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "input"
            path.write_bytes(b"previous")
            with patch.object(fetch, "urlopen", return_value=io.BytesIO(b"damaged")):
                with self.assertRaises(ValueError):
                    fetch.fetch("https://example.invalid/input", path, "0" * 64)
            self.assertEqual(path.read_bytes(), b"previous")
            self.assertFalse(path.with_suffix(".partial").exists())

    def test_symlink_and_incomplete_download_are_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "input"
            path.symlink_to("missing")
            with self.assertRaises(ValueError):
                fetch.fetch("https://example.invalid/input", path, "0" * 64)
            path.unlink()
            path.with_suffix(".partial").write_bytes(b"keep")
            with self.assertRaises(ValueError):
                fetch.fetch("https://example.invalid/input", path, "0" * 64)
            self.assertEqual(path.with_suffix(".partial").read_bytes(), b"keep")


if __name__ == "__main__":
    unittest.main()
