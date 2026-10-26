<!-- SPDX-License-Identifier: MIT -->
# Package transaction review — 2026-10-26

578 signed ARM64/architecture-independent packages were resolved from the
repositories in `pacman.conf`. Their versions, licences, dependencies, sizes,
SHA-256 hashes and signing fingerprints are in `packages.lock.json`.

The generated scriptlet/hook report has SHA-256
`4bef8a8d74c4e56784f0b2af5af6132e103d783591b2f74b2fa4837178b89578`.
All 31 `.INSTALL` files and the hook commands were examined before installation.
The 77 entries also include three Omarchy user-onboarding hooks, which this
profile does not launch. The remaining actions update caches, locales, trust
databases, account/service definitions, kernel modules and initramfs files.

Specific adaptations:

- The new signed `alsa-ucm-conf` package contains the PinePhone Pro profiles
  and provides/conflicts with `alsa-ucm-pinephonepro`. Approve this transition
  within Pacman's transaction, together with `vi` to `ex-vi-compat`.
  Verification rejects any other conflict with an installed base package;
  dependency checking and signature enforcement remain enabled.
- `omarchy-settings` changes `/etc/os-release` and initramfs hooks for a desktop
  system. Restore the Arch Linux ARM identity and set the PinePhone hooks in the
  main config (the kernel preset's `-c` bypasses drop-ins), plus a matching
  drop-in for default invocations. Omit host-device autodetection, encryption and
  overlay-root hooks from this plain ext4 microSD image.
- `device-pine64-pinephonepro` regenerates `/boot/boot.scr` from `boot.txt`.
  Keep this boot path, the DTB and `linux-megi` modules. Give the output new
  filesystem identifiers and select its root by UUID, avoiding identifiers
  inherited from the official base or an older installation.
- All boot changes apply to a newly created regular file in the builder.
  There is no SPI/eMMC writer or Pixel flash command.
- Package hooks run with a private `/run`, no physical devices in the chroot,
  and read-only sysfs. Their service activation cannot reach the host systemd.
- Remove factory credentials, SSH host keys, package-manager private keys,
  password backups, network connections, logs and machine identity before
  export. OpenSSH client remains available; its server is disabled.
- First-boot password creation is restricted to the `terminal` account through
  a root-owned, one-time helper. It accepts the password only on standard input.
  Autologin and the helper's sudo grant are removed after successful setup.

This is a source and package review, not hardware validation. Graphical first
boot and the inherited keyboard detection still need tests on the phone.
