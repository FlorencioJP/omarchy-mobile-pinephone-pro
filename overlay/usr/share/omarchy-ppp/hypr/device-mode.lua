-- SPDX-License-Identifier: MIT
local detector = assert(io.popen('/usr/bin/ppp-profile detect'))
local mode = detector:read('*l')
detector:close()
local transform = mode == 'landscape' and 3 or 0
hl.monitor({ output = 'DSI-1', mode = 'preferred', position = 'auto', scale = 1.5, transform = transform })
hl.config({ input = {
  kb_file = '/usr/share/omarchy-ppp/keyboard.xkb',
  touchdevice = { transform = transform, output = 'DSI-1' },
} })
