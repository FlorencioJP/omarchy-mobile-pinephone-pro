import importlib.util
from pathlib import Path
from tempfile import TemporaryDirectory

spec = importlib.util.spec_from_file_location('power_status', Path(__file__).resolve().parents[1] / 'power-status.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
with TemporaryDirectory() as directory:
    root = Path(directory)
    for name, capacity in [('rk818-battery', '60'), ('ip5xxx-battery', '85')]:
        battery = root / name
        battery.mkdir()
        (battery / 'type').write_text('Battery\n')
        (battery / 'capacity').write_text(capacity + '\n')
    data = module.supplies(root)
    assert data['rk818-battery']['capacity'] == '60'
    assert data['ip5xxx-battery']['capacity'] == '85'
    assert 'status' not in data['rk818-battery']
    output = module.display(data)
    assert 'Téléphone' in output and 'Clavier' in output
    assert '60 %' in output and '85 %' in output
    assert 'Aucune source' in module.display({})
    assert '███░░ 60 %' in output
    assert '┌' in output and 'Batterie' in output
assert module.charge('100') == '█████ 100 %'
assert module.charge('0') == '░░░░░ 0 %'
for value in (None, 'invalid', '-1', '101'):
    assert module.charge(value) == '—'
assert module.measurement('4186325', 1_000_000, 2) == '4.19'
assert module.measurement('-7460', 1_000, 1) == '-7.5'
assert module.measurement(None, 1_000, 1) == '—'
assert 'Pleine' in module.display({'rk818-battery': {'type': 'Battery', 'status': 'Full'}})
assert 'Non' in module.display({'rk818-usb': {'type': 'USB', 'online': '0'}})
print('POWER_STATUS_OK')
