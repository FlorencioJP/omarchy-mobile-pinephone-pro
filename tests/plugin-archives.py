"""Reject unsafe archive paths and links before touching a plugin directory."""
import importlib.util
import io
from pathlib import Path
import tarfile
from tempfile import TemporaryDirectory

spec = importlib.util.spec_from_file_location('prepare_plugins', Path(__file__).resolve().parents[1] / 'plugins/prepare.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
with TemporaryDirectory() as directory:
    root = Path(directory)
    for index, (name, link) in enumerate([('root/manifest.json', False),
                                        ('root/../../escape', False), ('/absolute', False),
                                        ('root/link', True)]):
        archive = root / f'{index}.tgz'
        with tarfile.open(archive, 'w:gz') as stream:
            member = tarfile.TarInfo(name)
            if link:
                member.type = tarfile.SYMTYPE
                member.linkname = '/tmp/outside'
                stream.addfile(member)
            else:
                member.size = 2
                stream.addfile(member, io.BytesIO(b'{}'))
        try:
            module.extract(archive, root / f'output-{index}')
        except ValueError:
            assert index > 0
        else:
            assert index == 0
            assert (root / 'output-0/manifest.json').read_text() == '{}'
print('PLUGIN_ARCHIVE_CHECKS_OK')
