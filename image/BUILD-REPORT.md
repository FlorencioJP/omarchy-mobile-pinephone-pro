<!-- SPDX-License-Identifier: MIT -->
# Software build report — 2026-10-26

Implementation: `967a089343c43ff22288d67e5dc5f6cb196b1ce3`.
Host: Apple Silicon macOS, Docker Desktop Linux ARM64 VM.
The PinePhone Pro was disconnected throughout these builds.

## Inputs and reproducibility

The signed base and three Git revisions are pinned in [inputs.json](inputs.json).
The base signature matched the fingerprint published on the
[DanctNIX release page](https://github.com/dreemurrs-embedded/Pine64-Arch/releases/tag/20251224).
All 578 archives in [packages.lock.json](packages.lock.json) passed SHA-256,
signature and signer checks before an offline transaction. The complete installed
system contains 629 packages, including unchanged packages from the signed base.

Two fresh base-image constructions produced identical package inventories and
configuration manifests:

| Evidence | Entries | SHA-256 |
| --- | ---: | --- |
| [Installed packages](evidence/installed-packages.txt) | 629 | `1b0a3ca763ec00c54855da6d57568f55ad5856206cdf8de30502252d50bee88f` |
| [Configuration manifest](evidence/configuration.json) | 169 | `8cbdcdbc153928484d3394c5023fc8b6c8cb8db03f2d1c8f7a813279832110d2` |

The comparison covers versions and the selected configuration files, symlinks,
permissions and ownership described in the builder README. It does not establish
byte-identical disk images. Filesystem metadata, caches, discarded blocks and
initramfs timestamps may differ. Development attempts preceding the final
profile/cache fixes are excluded from this comparison.

## Local image artifacts

Both images expand to **12,884,901,888 bytes (12 GiB)**. They are local build
outputs in `image/out/`, not GitHub release downloads. Use the later artifact
for the hardware protocol:

| File | Compressed bytes | SHA-256 |
| --- | ---: | --- |
| `omarchy-on-ppp-20261026T224915Z.img.xz` | 1690607312 | `f284b0b13a7e32327260f4e5118a0744f7fccf8522e23c2d3339b7e16f68c97c` |
| `omarchy-on-ppp-20261026T225224Z.img.xz` | 1658077644 | `ad1cbd9cb650bb9781af59518a1e1bf8c356f2527a33788e451518be68a689ed` |

Each has `.sha256`, `.packages.txt` and `.configuration.json` sidecars. Their
different compressed hashes are expected; the reproducibility claim above is
limited to the matching package and configuration manifests.

## Checks executed

- Authenticated base and pinned source trees. Verification refuses modified or
  ignored source files, unexpected package architectures, kernel/bootloader
  packages and unreviewed package conflicts.
- Installed the exact locked transaction with networking disabled; Pacman
  dependency/database checks passed.
- Preserved the base partition starts and boot partition. Expanded only the last
  partition within the new regular image file, to a total of 12 GiB.
- Confirmed `Image.gz`, module directory and initramfs use the same megi kernel;
  checked the PinePhone Pro DTB, boot script and root UUID references.
- Generated initramfs without builder-device autodetection or `resizerootfs`.
- Compiled the XKB map with libxkbcommon: 24 logical key cases passed.
- Loaded the real SDDM session model in offscreen test mode: session found. An
  empty `/dev/dri` directory was supplied because SDDM otherwise omits Wayland
  sessions. No graphics device was emulated or tested.
- `Hyprland --verify-config` returned `config ok`; Lua syntax and sudoers checks
  passed. This starts no compositor or GPU session.
- First-boot helper tests covered password validation, injection rejection,
  removal of one-time grants, repeat invocation and password-setting failure.
- Image audit found locked accounts, no factory user, no SSH host keys, no
  saved NetworkManager connections, no machine identity and no package-manager private keyring.
  Build-time key material lived in tmpfs; device keys are generated at first boot.
- Unmounted ext4 and FAT checks passed in both builds.
- Both compressed archives passed `xz -t` and their SHA-256 checks. The exported
  package/configuration sidecars also compared equal with `cmp`.
- ShellCheck, Python/shell syntax and the complete Linux host CI suite passed.
  The new tests add three download cases and seven security/manifest cases.
- [GitHub host CI](https://github.com/FlorencioJP/omarchy-mobile-pinephone-pro/actions/runs/40415563709)
  passed for the implementation commit. The suite requires GNU tools and a
  non-root user; direct macOS/root-container runs do not satisfy that environment.

## Versions

| Component | Version |
| --- | --- |
| linux-megi | `6.18.55-1` |
| Omarchy | `4.0.6-1` |
| Hyprland | `0.56.2-7` |
| Quickshell | `0.3.2.r7.g2b4501a-1` |
| Mesa | `1:26.2.5-1` |
| SDDM | `0.21.0-7` |
| Squeekboard | `1.43.1-6` |
| NetworkManager | `1.58.1-2` |
| BlueZ | `5.87-2` |
| ModemManager / eg25-manager | `1.24.2-2` / `0.5.2-1` |
| OpenSSH / tmux | `10.6p1-2` / `3.8-1` |

Builder image ID:
`sha256:d817576baf9611bdc768065d8306a4461dd413201a3f92620ca63a137b4848e9`.
The Dockerfile pins its Debian base digest and the `20261026T000000Z` package
snapshot. Relevant tools: Python `3.13.5-1`, e2fsprogs `1.47.2-3+b12`,
fdisk `2.41.5-0+deb13u1`, gdisk `1.0.10-2+b1`, dosfstools `4.2-1.2`,
xz `5.8.1-1+deb13u1`, GnuPG `2.4.7-21+deb13u1`, libarchive-tools
`3.7.4-4+deb13u1`, ShellCheck `0.10.0-1`.

## Remaining validation

None of these checks validates phone boot, GPU acceleration, touch alignment,
physical keys, first-boot interaction, radios, charging, shutdown or suspend.
Use the [microSD protocol](README.md#short-hardware-test) and
[validation matrix](VALIDATION.md). No eMMC or bootloader write was performed.

The kernel's initramfs build warned about a missing optional privacy-screen
symbol and an unspecified console font; generation and filesystem checks still
passed. Their relevance to the display must be assessed during the hardware test.
Pacman warned that the normal Omarchy sync database was absent; installation used
the verified temporary local repository, which is deliberately removed afterward.

No public binary release is offered. The source, locks and build evidence are
public; corresponding-source and binary redistribution requirements remain to
be checked before distributing an image release.
