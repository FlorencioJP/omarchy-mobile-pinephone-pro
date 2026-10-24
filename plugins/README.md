# Optional community plugin panels

These eight snapshots were examined and deposited on the test PinePhone Pro.
Six were adapted to open from the mobile menu without replacing its bar.
They are third-party code running in the shell, not a sandboxed extension API.

| Plugin | Device result |
|---|---|
| OmaSSH | Panel mapped; five upstream parser tests passed; SSH aliases not configured |
| Remote tmux | Panel mapped; host empty; no remote session tested |
| Network Speed | Panel mapped; real throughput observed |
| Vitals | Panel mapped; CPU collector received data; other tabs/actions not exhaustively tested |
| Tailscale | Panel mapped; Tailscale client absent; no VPN tested |
| WireGuard | Panel mapped; no profile or tunnel; import/connection untested |
| Battery Usage | Sources only, disabled: collector searches `BAT*`, unlike the PinePhone battery names |
| Caffeine | Sources only, disabled pending suspend/wake validation |

Pinned repositories, commits, versions and original archive hashes are in
[plugins.lock.json](plugins.lock.json). Original licences are retained in each
download and mirrored in [LICENSES/plugins](../LICENSES/plugins). The adapters
are [adaptations.patch](adaptations.patch); Hyprperks code is not included.

## Prepare, review, install

This is optional work for the already-provisioned experimental base described
in the main README, not an image builder or a general Omarchy installer.
Requires Python 3 and `patch`. As the normal session user:

```sh
python3 plugins/prepare.py
# Review downloaded sources, manifests and the adaptations before activation.
python3 plugins/install.py
export OMARCHY_PATH=/usr/share/omarchy
export XDG_RUNTIME_DIR=/run/user/$(id -u)
omarchy-shell shell rescanPlugins
omarchy-shell shell reloadConfig
omarchy-menu refresh
# From a graphical terminal, if the old QML remains cached:
omarchy-restart-shell
python3 plugins/test-runtime.py
```

Keep this checkout in place: plugin links refer to `plugins/selected-plugins`.
The installer refuses to replace a plugin already provided at a different path.
It merges the menu and shell config and saves adjacent `.before-selected-plugins`
backups. It requires no root privilege. No upstream installer, generic system
upgrade, VPN login, tunnel import, kernel change or boot operation is executed.
Do not replace these snapshots with mutable HEAD without reviewing the new code
and replaying the mobile adaptations.

The tested device used equivalent private copies. The public preparation path
is checked on a host; a clean installation of the public checkout on another
phone remains untested. Six live panels and their Wayland surfaces were checked,
with no selected QML errors in the final device logs. This is not complete touch
or application validation. Public `test-runtime.py` briefly opens and closes the
six panels and writes local diagnostic JSON; run it with the owner present.

## Configuration and limitations

Open **Omarchy menu > PinePhone > Extensions**. OmaSSH reads `~/.ssh/config`.
For Remote tmux, edit `selected-plugins/andreconde.tmux/MobilePanel.qml`, set
`host` to a previously configured SSH alias, then reload the shell. No example
host is contacted while the field is empty. Remote tmux reads pane tails to
classify Claude Code activity; it is not a universal agent status protocol.

The tmux polling timer runs only while its panel is open, every 60 seconds.
Vitals and Network Speed use a five-second interval. Panel windows are tied to
the first screen (the tested phone has one); multi-monitor use is not validated.
The network panel's choices work within the session; persistence through the
desktop bar settings bridge is unavailable in the standalone mobile panel.

Runtime logs: `plugins-runtime.json`, `plugins-test-start.epoch` and the user
journal (`journalctl --user -b`). Preserve private SSH config and VPN profiles
outside this repository. No credentials are embedded in the snapshots.

## Recovery

Remove these six IDs from `~/.config/omarchy/shell.json` and their entries under
`pinephone.extensions` in the menu, then restart the shell. Alternatively restore
the two `.before-selected-plugins` backups, accounting for subsequent user edits.
Remove only the eight corresponding links in `~/.config/omarchy/plugins`.
Downloaded sources and personal SSH/VPN settings are not deleted automatically.
