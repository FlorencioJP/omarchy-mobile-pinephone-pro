# Optional desktop, theme and cellular setup

These are narrowly scoped helpers for the tested, already-provisioned PinePhone
Pro base. Read them before use. They do not build or flash an image. No private
configuration or Hyprperks code is included.

## Batteries

From the repository root, `python3 power-status.py` prints the two batteries as
a table with five-block gauges, translated states, volts and milliamps, plus
the power-supply status. Values are an instantaneous kernel report; the sign
of current is driver-specific and not a measured runtime estimate.

For a menu action, use an absolute path to this checkout and launch it with
`omarchy-launch-terminal`. The tested phone has a **PinePhone > Batteries** menu
entry that waits for Enter before closing. The public tool is checked using
`python3 tests/power-status.py`.

## Themes

The tested phone initially had no current theme. These helpers connect the
generated Omarchy colours to Foot and the mobile border colours. They preserve
font size, touch, orientation and the mobile shell.

First review and install the optional user hook as root:

```sh
sudo bash extras/install-user-hook.sh
mkdir -p ~/.config/omarchy-ppp
touch ~/.config/omarchy-ppp/local.lua
export OMARCHY_PATH=/usr/share/omarchy
export XDG_RUNTIME_DIR=/run/user/$(id -u)
export DBUS_SESSION_BUS_ADDRESS="${DBUS_SESSION_BUS_ADDRESS:-unix:path=$XDG_RUNTIME_DIR/bus}"
# Only when initializing an account that has no theme yet:
OMARCHY_THEME_HEADLESS=1 OMARCHY_THEME_SKIP_BACKGROUND=1 omarchy-theme-set tokyo-night
python3 extras/configure-theme.py
# In the graphical session's terminal:
hyprctl reload
omarchy-theme-set-foot
omarchy-theme-set-gnome
```

The hook loads `~/.config/omarchy-ppp/local.lua` when present; it contains no
third-party customization itself. Backups are made by each helper. The owner
confirmed theme selection works on the test phone. A fresh replay of these
public helpers on another device remains untested.

For the wallpaper, use Omarchy's native **Style > Background** menu. The test
phone uses the Tokyo Night `backgrounds/omarchy.png` image. Menu access and a
touch-accessible Omarchy menu button are described in CURRENT-STATUS.md.

## Cellular editor and terminal autostart

```sh
python3 extras/prepare-4g.py
sudo bash extras/install-desktop.sh
```

The first command downloads libnma-common/libnma 1.10.6-3 and
nm-connection-editor 1.36.0-2, verifies signatures using the installed public ARM
keyring and checks the hashes pinned in `4g.packages.lock.json`, which also records
architectures and package-declared licences. The configured ARM mirror is HTTP; authenticity
comes from the signatures. The installer rechecks the recorded hashes, requires
local package signatures, refuses replacing different installed versions and
asks for pacman's confirmation. There were no `.INSTALL` scripts in these three
examined archives. Normal package-manager hooks still apply.

The desktop helper then removes only `hl.exec_cmd('foot')` from the mobile
profile's startup callback, with a backup and Lua syntax check. It does not close
an existing terminal. To install only the editor, run `extras/install-4g.sh` with
sudo instead. Open the editor with `uwsm-app -- nm-connection-editor`; use its
mobile-broadband assistant for a new GSM/APN profile.

The editor window was mapped on the phone, but there was no SIM: registration,
APN settings and 4G data are not validated. Never place a SIM PIN, VPN credentials,
SSH key or personal APN profile in a public checkout or image.
