-- SPDX-License-Identifier: MIT
hl.config({
  misc = { disable_hyprland_logo = true, disable_splash_rendering = true, force_default_wallpaper = 0 },
  animations = { enabled = false },
})
dofile('/usr/share/omarchy-ppp/hypr/device-mode.lua')
hl.on('hyprland.start', function()
  hl.exec_cmd('/usr/bin/ppp-profile auto')
end)
