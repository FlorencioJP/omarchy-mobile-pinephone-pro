-- SPDX-License-Identifier: MIT
dofile('/usr/share/omarchy-ppp/hypr/device-mode.lua')
hl.on('hyprland.start', function()
  hl.exec_cmd('/usr/bin/ppp-profile auto')
end)
