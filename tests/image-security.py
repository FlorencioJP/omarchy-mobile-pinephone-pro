#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
import importlib.machinery
import importlib.util
import io
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'image'))
import lock
from verify import check_file
from audit import configuration_manifest

loader = importlib.machinery.SourceFileLoader('password_setup', str(ROOT / 'image/profile/usr/lib/omarchy-ppp/set-password'))
spec = importlib.util.spec_from_loader(loader.name, loader)
password_setup = importlib.util.module_from_spec(spec)
loader.exec_module(password_setup)


class ImageSecurity(unittest.TestCase):
    def test_configuration_manifest_detects_content_and_preserves_links(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            (root/'etc').mkdir()
            p=root/'etc/fstab'
            p.write_text('first')
            a=configuration_manifest(root)
            p.write_text('second')
            self.assertNotEqual(a, configuration_manifest(root))
            p.unlink()
            p.symlink_to('/not-followed')
            self.assertEqual(configuration_manifest(root)['etc/fstab']['link'], '/not-followed')

    def test_conflicts_use_versions_after_the_locked_upgrade(self):
        compare=lambda a,b: (int(a)>int(b))-(int(a)<int(b))
        self.assertFalse(lock.conflict_applies('mkinitcpio<38', {'mkinitcpio':'42'}, compare))
        self.assertTrue(lock.conflict_applies('mkinitcpio<38', {'mkinitcpio':'37'}, compare))
        self.assertTrue(lock.conflict_applies('legacy-audio', {'legacy-audio':'1'}, compare))
        self.assertFalse(lock.conflict_applies('missing', {}, compare))

    def test_package_architecture_url_and_bootloader_guards(self):
        valid = 'core|test|1-1|aarch64|https://de3.mirror.archlinuxarm.org/aarch64/core/test-1-1-aarch64.pkg.tar.xz'
        self.assertEqual(lock.package_row(valid)['name'], 'test')
        for row in [valid.replace('|aarch64|','|x86_64|'), valid.replace('https:', 'http:'),
                    valid.replace('de3.mirror.archlinuxarm.org', 'example.invalid'),
                    valid.replace('|test|','|tow-boot|'), valid.replace('|test|','|linux-aarch64|')]:
            with self.assertRaises(ValueError): lock.package_row(row)

    def test_hash_guard_rejects_modified_and_symlink_inputs(self):
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/'input'
            p.write_text('changed')
            with self.assertRaises(ValueError): check_file(p, '0'*64)
            p.unlink()
            p.symlink_to('/etc/passwd')
            with self.assertRaises(ValueError): check_file(p, '0'*64)

    def test_password_rejects_injection_and_invalid_lengths(self):
        for password in ['', 'short', 'longpassword\nroot:changed', 'longpassword\r', 'longpassword\0', 'a'*257]:
            with self.assertRaises(ValueError): password_setup.validate(password)
        self.assertEqual(password_setup.validate('valid-test-password'), 'valid-test-password')

    def test_password_helper_removes_only_its_one_time_grants(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            state=root/'provisioned'
            grant=root/'etc/sudoers.d/omarchy-ppp-firstboot'
            autologin=root/'etc/sddm.conf.d/95-omarchy-ppp-firstboot.conf'
            for p in (grant,autologin):
                p.parent.mkdir(parents=True,exist_ok=True)
                p.write_text('one time')
            with patch.object(password_setup,'STATE',state), \
                 patch.object(password_setup,'Path',side_effect=lambda p: root/str(p).lstrip('/')), \
                 patch.object(password_setup.os,'geteuid',return_value=0), \
                 patch.dict(os.environ,{'SUDO_USER':'terminal'}), \
                 patch.object(password_setup.sys,'stdin',io.StringIO('valid-test-password')), \
                 patch.object(password_setup.subprocess,'run') as run:
                password_setup.main()
                run.assert_called_once_with(['/usr/bin/chpasswd'],input='terminal:valid-test-password\n',text=True,check=True)
                self.assertTrue(state.exists())
                self.assertFalse(grant.exists() or autologin.exists())
                with self.assertRaises(SystemExit): password_setup.main()

    def test_password_failure_preserves_setup_access(self):
        with tempfile.TemporaryDirectory() as directory:
            state=Path(directory)/'provisioned'
            with patch.object(password_setup,'STATE',state), \
                 patch.object(password_setup.os,'geteuid',return_value=0), \
                 patch.dict(os.environ,{'SUDO_USER':'terminal'}), \
                 patch.object(password_setup.sys,'stdin',io.StringIO('valid-test-password')), \
                 patch.object(password_setup.subprocess,'run',side_effect=RuntimeError('failed')):
                with self.assertRaises(RuntimeError): password_setup.main()
                self.assertFalse(state.exists())


if __name__=='__main__': unittest.main()
