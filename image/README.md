<!-- SPDX-License-Identifier: MIT -->
# Experimental microSD image builder

[Instructions en français](README.fr.md)

This builds **Omarchy on the PinePhone Pro**, an independent integration of
Omarchy and selected Omarchy Mobile UI components on Arch Linux ARM with the
`linux-megi` kernel. It is not an installer target supported by the Omarchy
Mobile project. The existing repository URL is retained for published links.

The builder starts from the public, signed PinePhone Pro barebone image listed
in [inputs.json](inputs.json), not from the owner's installed system. It keeps
the hardware packages and their U-Boot script, supplies the Omarchy session and
creates a new 12 GiB disk image. Only newly created regular files are mounted;
there is no command to flash a phone, SD card, eMMC or SPI bootloader.

## Build

Requirements: Git, Python 3.11+, Docker with a Linux ARM64 engine, at least
24 GiB free space and 4 GiB RAM. On Apple Silicon, Docker Desktop provides the
Linux VM. The container needs privileged mode to mount its own image files;
this grants access to the Docker engine's devices. Use a dedicated Linux VM or
Docker Desktop, not a native Docker daemon on a production host. The scripts
select only their newly created image files. On an x86 machine, ARM64 emulation
must already work; that path has not been tested.

From this checkout:

```sh
bash image/build.sh prepare
bash image/build.sh build
```

`prepare` downloads the exact base, Git revisions, package archives and
signatures from the committed locks. It builds the tools container from a
pinned Debian digest and dated package snapshot, then verifies the base's
signature. It does not install software on the host or phone.

`build` runs with **network disabled**. It rechecks input hashes, Git revisions
and every package signature, creates a local repository solely from the locked
archives, compares the resolved transaction to the lock, and installs it in a
fresh copy of the base. Package scriptlets and hooks were examined in
[REVIEW.md](REVIEW.md). It emits an `.img.xz`, SHA-256, installed inventory and
configuration manifest in
`image/out/`. An interrupted output retains the `.partial` suffix.

The package archives are precompiled upstream; this is not a recompilation of
Linux, Mesa, Hyprland or Qt. The lock aims to reproduce the package set and
configuration, not byte-identical ext4 images. Filesystem metadata, generated
caches and initramfs timestamps can differ.

Compare the `.packages.txt` and `.configuration.json` outputs from two clean
builds with `cmp`. The latter records content hashes, links, ownership and modes
for the PinePhone profile, login configuration, boot script source and generated
user configuration; it is not a checksum of every filesystem byte.

The upstream servers may eventually remove pinned archives. Keep the verified
`cache/image/` alongside your source revision for later offline builds. A local
image does not imply that binary redistribution or source-offer requirements
for every dependency have been audited for a public release.

To deliberately review a new package transaction:

```sh
bash image/build.sh resolve
```

This writes `cache/image/packages.candidate.json` and `cache/image/review.txt`.
It does **not** replace the committed lock. Inspect new versions, licences,
scriptlets, hooks and conflicts before adopting a candidate. Do not use this
command for an ordinary reproduction of the committed image.

## First boot and access

Use a dedicated microSD of at least 16 GB in an external reader. Verify the
compressed file's SHA-256 before writing it with an image writer, and require
the writer's verification pass to succeed. Confirm the selected card's capacity
and identity; writing it erases that card. Never select the Mac's disk or the
phone's internal storage. Reject a flash that reports an error.

Power the phone off, insert the card and use its existing bootloader's microSD
selection. If Tow-Boot is already installed, use its Volume Down microSD boot
path. If the existing loader cannot boot the card, stop and record what appears;
do not install or update a bootloader as part of this procedure.

The first graphical session logs in locally as `terminal` solely to create a
password. A GTK dialog accepts a new password twice. The physical keyboard
selects landscape; without it the portrait profile starts Squeekboard.
Autologin and the password-setup sudo grant are removed after success. The root
account remains locked. There is no shipped password, SSH identity or Wi-Fi
configuration. The first-boot interaction still needs a phone test.

Use the launcher for applications and the Omarchy menu. `Ctrl+Alt+Return` opens
Foot; `Ctrl+Alt+M` opens the Omarchy menu; `Ctrl+Alt+W` opens `nmtui`.
Wi-Fi, Bluetooth and mobile-data settings are present but are not validated
by an image build. APN/SIM and pairing are configured on the device.

For SSH, copy `~/.ssh/config.example` to `~/.ssh/config`, replace its placeholders
locally and run `ppp-connect agents`. It connects with OpenSSH and attaches to
`tmux new-session -A -s agents` on the **remote** machine. Install tmux there.
The SSH server on the phone is disabled by default; enabling it later is a
separate local action after password/key configuration.

## Recovery and storage

Power off, remove the microSD and boot the previous internal system. The builder
does not migrate anything to eMMC. Existing recovery backups stay private.

The output uses new, fixed filesystem UUIDs rather than those of the base image.
Do not boot with another copy of this same image simultaneously installed on
internal storage: duplicated UUIDs make device selection ambiguous. Keep the
new image on microSD during validation. Extra SD capacity is left unused;
automatic partition growth is deliberately not enabled in this first image.

With the official keyboard attached, charge through the keyboard's USB-C port
and do not connect a charger to the phone simultaneously. Battery percentages
alone do not validate the charge path or shutdown behavior.

## Short hardware test

1. Cold boot from the dedicated card **without the keyboard**. Photograph any
   error. Check portrait first-boot password creation, touch typing and login.
2. In a terminal, run `findmnt /`, `findmnt /boot`,
   `lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINTS` and
   `grep . /sys/class/block/mmcblk*/device/type`. Confirm both mounted
   filesystems belong to the SD before doing anything else. Stop if ambiguous.
3. Join Wi-Fi, open the Omarchy menu, then connect to a remote tmux session.
4. Shut down, attach the keyboard and cold boot. Check landscape and touch
   alignment, then Ctrl/Alt/Esc/Tab/arrows and `| ~ / \\ { } [ ] - _` in Foot.
5. Record `hyprctl configerrors`, the renderer in `hyprctl systeminfo` and the
   result of `ppp-batteries`. Record charging and shutdown separately; do not
   infer them from working keyboard input.

Do not test automatic suspend until those gates pass and recovery is available.
Then test screen off/on, one suspend/resume, Wi-Fi reconnection, repeated cycles
and a timed battery run, first without and then with the keyboard.

Useful private diagnostics: `journalctl -b -u sddm`,
`journalctl -b -t omarchy-shell`, `journalctl --user -b`,
`journalctl -b -u NetworkManager`, `hyprctl devices`, `hyprctl monitors`,
`hyprctl configerrors`, and `~/.local/state/omarchy-ppp/keyboard.log`.
Review logs before sharing: they can contain account names, network identifiers
and host addresses. Build logs are under `image/work/` and are gitignored.
