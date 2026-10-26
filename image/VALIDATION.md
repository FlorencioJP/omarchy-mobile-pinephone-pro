<!-- SPDX-License-Identifier: MIT -->
# Clean-image validation

This report concerns the new builder, not the owner's historical installation.
The phone was disconnected during this work. No new hardware result is claimed.

| Area | Implemented | Software evidence | Hardware |
| --- | --- | --- | --- |
| Public base | Exact URL, SHA-256 and release signing key | Base PGP signature verified | Not tested for the new image |
| Package transaction | 578 package archives, signatures, licences and versions locked | All package signatures and metadata checked | Not tested |
| Offline build | Regular image only; no network during installation | Two compressed images built; 629-package inventory and 169-entry configuration manifest identical | Not tested |
| Portrait/landscape | Existing profile reused; same display/touch transform | Existing profile logic tests pass | Historical evidence only; new image untested |
| Physical keyboard | XKB symbol layer and terminal shortcuts | libxkbcommon compilation and 24 logical translations passed | Full physical matrix not tested |
| First-boot password | Local GTK dialog; one-time helper; SSH server disabled | Validation, injection, repeat-use and failure tests pass | Touch/keyboard interaction not tested |
| Omarchy desktop | Mobile bar, launcher/switcher, menu and Tokyo Night | Hyprland configuration accepted; real SDDM session model recognized the session offscreen | Not tested |
| Wi-Fi, Bluetooth, 4G | NetworkManager, BlueZ, ModemManager and eg25-manager | Package/service configuration only | No new test; no SIM test |
| SSH / remote tmux | OpenSSH client, configuration example and fixed remote command | Script syntax checked | Remote sessions not tested |
| Charge / shutdown | Existing read-only battery table included | Reporting tests pass | Charging and keyboard-powered shutdown unresolved |
| Suspend / reconnect / autonomy | No new policy enabled | Deferred until first-boot gates pass | Not tested |

The packages are compiled by their upstream maintainers; this build assembles
them. A generated image and passing software tests do not prove boot, GPU,
touch, input, radios, charging or suspend on the phone.

Exact versions, manifest hashes and test boundaries are in the
[software build report](BUILD-REPORT.md).

## Scope and remaining limits

- The image is a terminal-focused baseline, not the full Omarchy application
  catalogue. It includes Foot, SSH/tmux, Nautilus, GNOME Text Editor and radio
  editors. A browser and the historical larger application bundle are not
  installed; the corresponding browser shortcut is omitted from this image.
- The upstream Omarchy menu is available, but every application/service installer
  it exposes has not been validated on ARM64 or on this phone. Menu visibility
  is not a compatibility verdict for those optional applications.
- Selected upstream mobile components are used with an explicit PinePhone
  profile. Pixel hardware services and unsupported quick-setting tiles are
  excluded. Community plugin snapshots remain available separately in
  `plugins/`; they are not silently enabled in the fresh image.
- Keyboard detection is intended for cold boot. It is not guaranteed to detect
  live attachment/removal. All physical key combinations still need a matrix.
- The first-boot dialog, SDDM authentication and touch keyboard must be exercised
  on the phone, including failed/repeated password entry and a subsequent reboot.
- No card expansion, internal-storage migration or bootloader update is provided
  by this builder. The old eMMC migration instructions are historical and must
  not be applied blindly to this new image.
- No public binary release has been made. Binary redistribution and corresponding
  source availability must be checked before publishing an image release.

See [the build and recovery instructions](README.md) for the short hardware
protocol and diagnostic logs. Keep personal phone logs and recovery images out
of Git.
