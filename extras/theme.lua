local theme = os.getenv('HOME') .. '/.local/state/omarchy/current/theme/hyprland.lua'
local file = io.open(theme, 'r')
if file then
  file:close()
  dofile(theme)
end
