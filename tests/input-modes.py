"""Décision de profil, transformation couplée, échec sans écran et contrôle OSK."""
import importlib.machinery
import importlib.util
from pathlib import Path
from types import SimpleNamespace
import tempfile
import sys
from unittest.mock import patch

root = Path(__file__).resolve().parents[1]
loader = importlib.machinery.SourceFileLoader("profile", str(root / "overlay/usr/bin/ppp-profile"))
spec = importlib.util.spec_from_loader(loader.name, loader)
profile = importlib.util.module_from_spec(spec)
loader.exec_module(profile)

with tempfile.TemporaryDirectory() as directory:
    base = Path(directory)
    inputs = base / "class/input"
    inputs.mkdir(parents=True)
    assert profile.detect(inputs) == "portrait"
    device = base / "devices/5-0015/input/input3"
    device.mkdir(parents=True)
    (device / "name").write_text("PinePhone Keyboard\n")
    (inputs / "event3").mkdir()
    (inputs / "event3/device").symlink_to(device)
    assert profile.detect(inputs) == "landscape"
    (device / "name").write_text("Power Button\n")
    assert profile.detect(inputs) == "portrait"
    (device / "name").unlink()
    assert profile.detect(inputs) == "portrait"

for mode, transform in (("portrait", 0), ("landscape", 3), ("landscape-inverted", 1)):
    lua = profile.display_lua([{"name": "DSI-1"}, {"name": "DP-1"}], mode)
    assert lua.count(f"transform={transform}") == 2 and 'output="DSI-1"' in lua and "DP-1" not in lua
for mode, transform in (("portrait", "0"), ("landscape", "1")):
    with patch.object(sys, "argv", ["ppp-profile", "--console", "auto"]), \
         patch.object(profile, "detect", return_value=mode), patch.object(Path, "write_text") as write:
        profile.main()
        write.assert_called_once_with(transform)
for monitors in ([], [{"name": "DP-1"}], [{"name": "DSI-1"}, {"name": "eDP-1"}]):
    try:
        profile.display_lua(monitors, "portrait")
    except ValueError:
        pass
    else:
        raise AssertionError("Écran ambigu accepté")

for visible in (True, False):
    with patch("subprocess.run", return_value=SimpleNamespace(returncode=0)) as run:
        profile.keyboard(visible)
        assert run.call_args_list[0].args[0][-1] == str(visible).lower()
        assert run.call_args_list[-1].args[0][-1] == str(visible).lower()
with tempfile.TemporaryDirectory() as directory, patch.dict("os.environ", {"XDG_STATE_HOME": directory}), \
     patch("subprocess.run", side_effect=[SimpleNamespace(returncode=0), SimpleNamespace(returncode=1),
           SimpleNamespace(returncode=1), SimpleNamespace(returncode=0)]), \
     patch("subprocess.Popen") as launch, patch("time.sleep"):
    profile.keyboard(True)
    assert launch.call_args.args[0] == ["squeekboard"]
    assert (Path(directory) / "omarchy-ppp/keyboard.log").is_file()
with patch("subprocess.run", side_effect=[SimpleNamespace(returncode=0), SimpleNamespace(returncode=0)] +
           [SimpleNamespace(returncode=1, stderr=b"unavailable")] * 30), patch("time.sleep"):
    try:
        profile.keyboard(True)
    except RuntimeError:
        pass
    else:
        raise AssertionError("Échec OSK ignoré")
print("Profils : détection, orientation écran/tactile et erreurs OSK contrôlées.")
