# SPDX-FileCopyrightText: 2025 Cooper Dalrymple
#
# SPDX-License-Identifier: GPLv3

from adafruit_hid.keycode import Keycode

PS2_MAP = {
    'code': [
        0, Keycode.F9, 0, Keycode.F5, Keycode.F3, Keycode.F1, Keycode.F2, Keycode.F12, 0, Keycode.F10, Keycode.F8, Keycode.F6, Keycode.F4, Keycode.TAB, Keycode.GRAVE_ACCENT, 0, # 00-0F
        0, Keycode.LEFT_ALT, Keycode.LEFT_SHIFT, 0, Keycode.LEFT_CONTROL, Keycode.Q, Keycode.ONE, 0, 0, 0, Keycode.Z, Keycode.S, Keycode.A, Keycode.W, Keycode.TWO, 0, #10-1F
        0, Keycode.C, Keycode.X, Keycode.D, Keycode.E, Keycode.FOUR, Keycode.THREE, 0, 0, Keycode.SPACE, Keycode.V, Keycode.F, Keycode.T, Keycode.R, Keycode.FIVE, 0, #20-2F
        0, Keycode.N, Keycode.B, Keycode.H, Keycode.G, Keycode.Y, Keycode.SIX, 0, 0, 0, Keycode.M, Keycode.J, Keycode.U, Keycode.SEVEN, Keycode.EIGHT, 0, #30-3F
        0, Keycode.COMMA, Keycode.K, Keycode.I, Keycode.O, Keycode.ZERO, Keycode.NINE, 0, 0, Keycode.PERIOD, Keycode.FORWARD_SLASH, Keycode.L, Keycode.SEMICOLON, Keycode.P, Keycode.MINUS, 0, #40-4F
        0, 0, Keycode.QUOTE, 0, Keycode.LEFT_BRACKET, Keycode.EQUALS, 0, 0, Keycode.CAPS_LOCK, Keycode.RIGHT_SHIFT, Keycode.ENTER, Keycode.RIGHT_BRACKET, 0, Keycode.BACKSLASH, 0, 0, # 50-5F
        0, 0, 0, 0, 0, 0, Keycode.BACKSPACE, 0, 0, Keycode.KEYPAD_ONE, 0, Keycode.KEYPAD_FOUR, Keycode.KEYPAD_SEVEN, 0, 0, 0, # 60-6F
        Keycode.KEYPAD_ZERO, Keycode.KEYPAD_PERIOD, Keycode.KEYPAD_TWO, Keycode.KEYPAD_FIVE, Keycode.KEYPAD_SIX, Keycode.KEYPAD_EIGHT, Keycode.ESCAPE, 0, Keycode.F11, Keycode.KEYPAD_PLUS, Keycode.KEYPAD_THREE, Keycode.KEYPAD_MINUS, Keycode.KEYPAD_ASTERISK, Keycode.KEYPAD_NINE, 0, 0, # 70-7F
        0, 0, 0, Keycode.F7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 # 80-8F
    ],
    'ext': {
        0x11: Keycode.RIGHT_ALT,
        0x14: Keycode.RIGHT_CONTROL,
        0x1f: Keycode.LEFT_GUI,
        0x27: Keycode.RIGHT_GUI,
        0x2F: Keycode.APPLICATION,
        0x4a: Keycode.KEYPAD_FORWARD_SLASH,
        0x5a: Keycode.KEYPAD_ENTER,
        0x6b: Keycode.LEFT_ARROW,
        0x74: Keycode.RIGHT_ARROW,
        0x75: Keycode.UP_ARROW,
        0x72: Keycode.DOWN_ARROW,
        0x69: Keycode.END,
        0x6c: Keycode.HOME,
        0x70: Keycode.INSERT,
        0x71: Keycode.DELETE,
        0x7a: Keycode.PAGE_DOWN,
        0x7d: Keycode.PAGE_UP,
        0x7e: Keycode.SCROLL_LOCK,
        0x77: Keycode.KEYPAD_NUMLOCK,
    }
}

def get_keycode(code:int, code_ext:int) -> int:
    if code_ext:  # extended scancode
        return PS2_MAP['ext'].get(code)
    else:         # normal
        return PS2_MAP['code'][code]
