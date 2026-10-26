#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Compile the actual XKB file and check symbols, without a physical keyboard."""
import ctypes as c
from pathlib import Path
import sys

path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1] / 'image/profile/usr/share/omarchy-ppp/keyboard.xkb'
xkb = c.CDLL('libxkbcommon.so.0')
for name, args, result in [
    ('xkb_context_new', [c.c_int], c.c_void_p),
    ('xkb_keymap_new_from_string', [c.c_void_p, c.c_char_p, c.c_int, c.c_int], c.c_void_p),
    ('xkb_state_new', [c.c_void_p], c.c_void_p),
    ('xkb_state_update_key', [c.c_void_p, c.c_uint32, c.c_int], c.c_int),
    ('xkb_state_key_get_utf8', [c.c_void_p, c.c_uint32, c.c_char_p, c.c_size_t], c.c_int),
    ('xkb_state_key_get_one_sym', [c.c_void_p, c.c_uint32], c.c_uint32),
    ('xkb_state_unref', [c.c_void_p], None),
    ('xkb_keymap_unref', [c.c_void_p], None),
    ('xkb_context_unref', [c.c_void_p], None),
]:
    function = getattr(xkb, name)
    function.argtypes, function.restype = args, result
context = xkb.xkb_context_new(0)
keymap = xkb.xkb_keymap_new_from_string(context, path.read_bytes(), 1, 0)
assert keymap, 'XKB compilation failed'
count = 0
for key, modifiers, expected in [
    (2, [], '1'), (2, [42], '!'), (2, [100], '|'), (3, [100], '\\'),
    (4, [100], '~'), (5, [100], '`'), (6, [100], '{'), (7, [100], '}'),
    (8, [100], '['), (9, [100], ']'), (10, [100], '-'), (10, [100,42], '_'),
    (11, [100], '='), (11, [100,42], '+'), (53, [], '/'), (51, [], ','),
]:
    state = xkb.xkb_state_new(keymap)
    for modifier in modifiers: xkb.xkb_state_update_key(state, modifier+8, 1)
    buffer = c.create_string_buffer(16)
    xkb.xkb_state_key_get_utf8(state, key+8, buffer, len(buffer))
    assert buffer.value.decode() == expected, (key, modifiers, buffer.value, expected)
    xkb.xkb_state_unref(state)
    count += 1
state = xkb.xkb_state_new(keymap)
for key, symbol in [(1,0xff1b), (15,0xff09), (29,0xffe3), (56,0xffe9),
                    (105,0xff51), (103,0xff52), (106,0xff53), (108,0xff54)]:
    assert xkb.xkb_state_key_get_one_sym(state,key+8) == symbol
    count += 1
xkb.xkb_state_unref(state)
xkb.xkb_keymap_unref(keymap)
xkb.xkb_context_unref(context)
print(f'XKB_COMPILED: {count} logical key cases passed; physical keyboard untested')
