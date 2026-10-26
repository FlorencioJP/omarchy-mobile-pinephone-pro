# Omarchy on the PinePhone Pro

**Experimental, unofficial, microSD-first integration for the PinePhone Pro and the official PinePhone Keyboard.**

[Documentation française](README.fr.md)

The goal is a small Linux terminal for SSH access to AI agents running on remote machines, with persistent tmux sessions on those machines. No local AI agent runtime or private credentials are included.

This repository contains integration work tested on one device: console and keyboard boot fixes, landscape configuration, access to the native Omarchy menu, and a version-locked ARM64 application bundle. It preserves the PinePhone Pro hardware stack rather than using Pixel boot or partitioning procedures.

**Independent experimental integration; not an officially supported Omarchy Mobile target.**
The [microSD image builder](image/README.md) starts from a signed public base
and a complete locked package transaction. Its hardware validation is separate
from the historical installation below. The older application installers still
require that specific installation; do not run them on an arbitrary Arch system.

## Current status

Updated 2026-10-26: see the [clean-image validation](image/VALIDATION.md).
The following table records the historical installation (2026-10-24), not a
hardware test of the new image. See also [project status](CURRENT-STATUS.md),
[optional community plugin panels](plugins/README.md) and
[desktop/theme/cellular helpers](extras/README.md). Later user-level integrations
were deployed privately first; only redistributable code and dependency locks
are published here. Hyprperks adaptations and personal device data are excluded.

| Component | Evidence / limitation |
|---|---|
| microSD boot and local login | Tested by the device owner |
| Official physical keyboard | Typing tested; exhaustive modifier and symbol tests remain open |
| Landscape console and Hyprland | Tested on the device |
| Graphics | Compositor reports Mali-T860 MC4 / Panfrost; no benchmark or endurance test |
| Wi-Fi | Connection confirmed by the device owner; resume/reconnection untested |
| Omarchy menu and app catalogue | Opened and inspected using screenshots from the device |
| Additional applications | 203 packages installed; Chromium, Nautilus and GNOME Text Editor windows inspected |
| Terminal complement | 37 signed packages added; software smoke tests passed in SD chroot under Sailfish; graphical session after these additions untested |
| Keyboard / touch profiles and graphical login | Touch login/typing confirmed on SD; later cold boot with official keyboard selected landscape on eMMC; exhaustive keys/symbols remain untested |
| Touchscreen accuracy | Not fully validated |
| Keyboard-to-phone charging | Earlier discharge observed under both OSes; latest kernel readings show both batteries Full/100%; controlled charge cycle remains unvalidated |
| Bluetooth and mobile data | Support retained, not validated on hardware |
| Suspend and battery life | Not validated |
| Themes and desktop | Tokyo Night initialized; owner confirmed theme selection; automatic Foot startup removed |
| Touch menu and battery tables | Owner confirmed tactile menu access and the battery table |
| Community plugins | Six adapted panels mapped on the phone; Vitals collector and network throughput checked; VPN/remote sessions unconfigured; two plugins disabled |
| Cellular editor | Signed ARM64 editor installed and window mapped; no SIM inserted, data untested |
| eMMC installation | Boot on eMMC confirmed, GUI/Wi-Fi/SSH working, ~94 GiB free; SD was still inserted but unmounted, so boot with card physically absent remains untested |

The recovery microSD is 512 GB with an approximately 8 GiB root partition. The current eMMC root partition is 107.6 GiB. SD storage expansion is not implemented here. A 512 GB card image must not be written wholesale to the smaller eMMC.

[eMMC migration](EMMC-MIGRATION.md) reuses the existing 107.6 GiB ext4 partition, preserves Sailfish recovery files privately, and adapts boot references without formatting or repartitioning. The copy and subsequent eMMC boots completed successfully on the device, with package checks, matching kernel/initramfs files and an unchanged partition table. The phone runs from eMMC; booting with the SD physically removed remains untested.

## Tested software

- DanctNIX PinePhone Pro kernel: `6.18.55-1-megi-danctnix`
- Omarchy: `4.0.6-1`
- Hyprland: `0.56.2-7`
- Quickshell: `0.3.2.r7.g2b4501a-1`
- Upstream Omarchy reference examined: `f643adc38ad65c4900609c5c1b0b5c359fef147a`

The reference commit is an audit reference, not an instruction to replace the installed runtime with the current upstream branch. See [upstream.lock.json](upstream.lock.json), [the previous installed package inventory](installed-before.txt), and [the additional package lock](packages.lock.json).

The original compressed experimental base was identified by SHA-256 `d54028c4eac86a225c1899f5d691f7409388962ecfa444c8cf0013c86380efc4`. It is not distributed here or used as a build input. The new [builder](image/README.md) and [validation report](image/VALIDATION.md) describe a separate clean build from public inputs; successful host checks do not validate it on a PinePhone Pro.

## Repository contents

- `image/`: public base and dependency locks, offline microSD builder, first-boot provisioning and recovery/test instructions.
- `overlay/etc/systemd/system/`: late keyboard probe and landscape console preparation, with a first-boot ordering drop-in.
- `patches/graphical-landscape.patch`: change display and touch rotation together, from transform 1 to 3.
- `configure-user.sh`: preserve mobile shell configuration and add native Omarchy panels and a menu launcher entry.
- `overlay/usr/share/omarchy-ppp/hypr/desktop.lua`: accessible keyboard shortcuts for menus and applications.
- `download.py`, `packages.lock.json`, `install.sh`: download, authenticate and install the additional package bundle.
- `packages.licenses.tsv`: package-declared licences, matched against locked archive hashes.
- `upstream-defaults.packages`, `upstream-coverage.tsv`: comparison with upstream packages, not a claim that all of Omarchy is installed or usable.
- `tests/`: host-side logic checks. Passing them does not validate phone hardware.

The console overlay and display patch are separate from the application installer. They were applied to the tested SD before local login was usable. The application installer alone does not provision a stock DanctNIX card.

[Input modes and graphical login](INPUT-MODES.md) add portrait with Squeekboard when the official keyboard is absent, landscape when it is detected at session startup, and a touch-oriented SDDM login. On the already-provisioned SD, run `sudo bash install-input-modes.sh` after reviewing it. It preserves password authentication, the Omarchy Mobile session and existing bootloader. Detection is intended for cold boot, not live keyboard removal. After fixing SDDM session selection, the owner confirmed touch login; remote checks confirmed a local session on SD, portrait display/touch transforms, and running Hyprland, Squeekboard and Foot. The owner also confirmed touch typing of `echo test`, Enter and the expected output in Foot. The new automatic physical-keyboard path remains untested. A fresh image's initial password setup still requires separate provisioning.

## Additional application bundle

The bundle adds Chromium, Nautilus, GNOME Text Editor, Evince, imv, mpv, LibreOffice, pavucontrol, Blueman and terminal utilities with their dependencies. At the tested baseline it added 203 packages without changing an existing package: approximately 391 MiB downloaded and 1,616.5 MiB installed. This is a first bundle, not the complete upstream default package set.

On the already-working experimental SD, review the scripts, place this repository under `/home/terminal/portage`, and run as `terminal`:

```sh
python3 download.py
bash configure-user.sh
sudo bash install.sh
```

The downloader checks hashes and signatures using the system's public Arch Linux ARM keyring. The installer rechecks hashes, requires signatures for local package files, checks that the active root resides on an SD, and rejects kernel/bootloader packages. It does not repartition, run a general system upgrade, flash firmware, or write an OS to eMMC. Package-manager hooks still run normally; review their effects before reusing the bundle on a different baseline.

The mirrors are live services: exact versions are pinned, but long-term archive availability is not guaranteed. This project hosts no package archive mirror.

Backups and the install log are under `/var/lib/omarchy-ppp/desktop`; the original user configuration is saved as `shell.json.before-portage`. No passwords, private SSH keys or personal Wi-Fi configuration belong in this repository or a redistributable image.

The optional terminal complement adds Neovim, tmux, bash completion, bat, eza, fd, fzf, lazygit, less, manual pages, ripgrep, rsync, starship, unzip, wget, zip, zoxide and the `xdg-terminal-exec` integration used by Omarchy. Its 37 packages are pinned in `terminal.packages.lock.json`, including declared licences: 30.7 MiB downloaded, 124.4 MiB installed. It refuses to replace installed packages with other versions and leaves kernel, bootloader and compositor packages unchanged.

```sh
python3 download.py --terminal
sudo bash install.sh --terminal
bash tests/terminal-smoke.sh
```

The actual installation added 37 packages to the existing 673, without replacing or removing any. Neovim, an isolated tmux session, fzf/ripgrep filtering and Foot command selection passed on the phone's CPU in an SD chroot while Sailfish remained booted. This is not validation of the additions in the DanctNIX graphical session. Logs and package inventories are under `/var/lib/omarchy-ppp/terminal`; the private configuration backup created during maintenance must not be published. Kernel, initramfs and boot-script hashes were unchanged. There are now 56 installed package matches or identified providers out of the 164 upstream requests; this remains an incomplete port.

## Keyboard shortcuts

| Action | Shortcut |
|---|---|
| Omarchy menu | Ctrl + Alt + M |
| Mobile app switcher | Ctrl + Alt + Tab |
| Clipboard | Ctrl + Alt + C |
| Browser | Ctrl + Alt + B |
| File manager | Ctrl + Alt + F |
| Text editor | Ctrl + Alt + E |

The original mobile launcher and keyboard profile stay in place. The graphical XKB profile uses Right Alt + 9 for `-`; the Linux console has a separate keymap and has not been exhaustively tested.

## Charging

Follow the [PINE64 keyboard documentation](https://pine64.org/documentation/Phone_Accessories/Keyboard/). With the keyboard mounted, charge through its USB-C port. Do not connect charging power to both ports; unplugging the keyboard's charging cable does not disconnect its internal battery output.

On earlier tests the keyboard charged while the phone continued discharging, including under Sailfish. The latest kernel report shows both batteries Full/100%, but the physical charging arrangement and a complete charge cycle still need confirmation. This must not be represented as a validated fix. Direct phone charging was observed after the owner reported removing the keyboard. Kernel input-device registration alone does not prove physical attachment after hot removal.

## Checks and contributions

```sh
python3 tests/download.py
python3 tests/check_console.py
python3 tests/terminal-lock.py
python3 tests/input-modes.py
python3 tests/power-status.py
python3 tests/plugin-archives.py
python3 tests/plugin-install.py
bash tests/user-configure.sh
bash -n install.sh configure-user.sh
```

The shell test requires Linux, Bash, jq and coreutils, running as a non-root user. Python checks require Python 3.11 or later. See [CONTRIBUTING.md](CONTRIBUTING.md) and [SECURITY.md](SECURITY.md).

## Credits and licensing

- [Omarchy](https://github.com/omacom/omarchy): native desktop, shell and tools. MIT; its notice is retained in [LICENSES/Omarchy.txt](LICENSES/Omarchy.txt).
- [Omarchy Mobile](https://github.com/derekross/omarchy-mobile): mobile shell and starting point for this integration. This repository does not replace its upstream hardware support matrix.
- [Pine64-Arch / DanctNIX](https://github.com/dreemurrs-embedded/Pine64-Arch): distribution and hardware stack.
- [PINE64](https://pine64.org/documentation/PinePhone_Pro/) and [Tow-Boot](https://tow-boot.org/devices/pine64-pinephonePro.html): hardware and boot documentation.

Integration code is MIT-licensed. Downloaded packages retain their own licences; see [LICENSE](LICENSE) and [packages.licenses.tsv](packages.licenses.tsv). This project is not endorsed by Omarchy, Omarchy Mobile or PINE64.
