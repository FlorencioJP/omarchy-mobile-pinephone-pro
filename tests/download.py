"""Les paquets hors cible et les contenus altérés doivent échouer avant GPG."""
import importlib.util
import io
from pathlib import Path
import tempfile
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("download", Path(__file__).resolve().parents[1] / "download.py")
download = importlib.util.module_from_spec(spec)
spec.loader.exec_module(download)
package = {"name": "test", "arch": "aarch64", "url": "http://mirror.archlinuxarm.org/aarch64/extra/test.pkg.tar.xz", "size": 3, "sha256": "0" * 64}
for change in ({"arch": "x86_64"}, {"url": "https://example.invalid/test.pkg.tar.xz"}):
    with patch.object(download, "urlopen", side_effect=AssertionError("Accès réseau interdit")):
        try:
            download.fetch(dict(package, **change))
        except ValueError:
            pass
        else:
            raise AssertionError("Un paquet hors cible a été accepté")
with tempfile.TemporaryDirectory() as directory:
    download.CACHE = Path(directory)
    with patch.object(download, "urlopen", return_value=io.BytesIO(b"bad")):
        try:
            download.fetch(package)
        except ValueError:
            pass
        else:
            raise AssertionError("Une empreinte incorrecte a été acceptée")
    assert not (Path(directory) / "test.pkg.tar.xz").exists()
print("Téléchargement : architecture, source et intégrité contrôlées.")
