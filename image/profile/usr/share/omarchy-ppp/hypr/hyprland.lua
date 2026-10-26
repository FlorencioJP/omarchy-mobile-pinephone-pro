-- SPDX-License-Identifier: MIT
dofile('/usr/share/omarchy/default/hypr/bootstrap.lua')
require('default.hypr.helpers')
require('default.hypr.envs')
require('default.hypr.looknfeel')
require('default.hypr.input')
require('omarchy.current.theme.hyprland')
hl.config({
  general = { gaps_in = 2, gaps_out = 2, border_size = 1 },
  decoration = { rounding = 3 },
  animations = { enabled = false },
  cursor = { hide_on_touch = true },
})
dofile('/usr/share/omarchy-ppp/hypr/input-modes.lua')
dofile('/usr/share/omarchy-ppp/hypr/desktop.lua')
o.bind('CTRL + ALT + RETURN', 'Terminal', 'foot')
o.bind('CTRL + ALT + S', 'SSH', 'foot ppp-connect')
o.bind('CTRL + ALT + L', 'Landscape', 'ppp-profile landscape')
o.bind('CTRL + ALT + P', 'Portrait', 'ppp-profile portrait')
o.bind('CTRL + ALT + SPACE', 'Applications', 'omarchy-shell shell toggle omamobile.launcher')
o.bind('CTRL + ALT + W', 'Wi-Fi', 'foot nmtui')
o.bind('CTRL + ALT + K', 'Keyboard', 'omarchy-shell omamobile.keyboard toggleKeyboard')
o.bind('CTRL + ALT + Q', 'Close', hl.dsp.window.close())
hl.on('hyprland.start', function()
  hl.exec_cmd('dbus-update-activation-environment --systemd WAYLAND_DISPLAY XDG_CURRENT_DESKTOP')
  hl.exec_cmd('omarchy-launch-shell')
  hl.exec_cmd('/usr/lib/omarchy-ppp/welcome')
end)
