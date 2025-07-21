# SPDX-FileCopyrightText: 2025 Cooper Dalrymple @relic-se
# SPDX-FileCopyrightText: 2021 Tod Kurt @todbot
#
# SPDX-License-Identifier: GPLv3

import ps2io
import time
import microcontroller

TIMEOUT = 0.01

# helpful: https://www.avrfreaks.net/sites/default/files/PS2%20Keyboard.pdf
# helpful: https://wiki.osdev.org/PS/2_Keyboard
SCANSET2_US = {
    'code': [
        0, 'F9', 0, 'F5', 'F3', 'F1','F2', 'F12', 0, 'F10', 'F8', 'F6', 'F4', 'TAB', '`', 0, # 00-0F
        0, 'LALT', 'LSHIFT', 0, 'LCTRL', 'q', '1', 0, 0, 0, 'z', 's', 'a', 'w', '2', 0, #10-1F
        0, 'c', 'x', 'd', 'e', '4', '3', 0, 0, ' ', 'v', 'f', 't', 'r', '5', 0, #20-2F
        0, 'n', 'b', 'h', 'g', 'y', '6', 0, 0, 0, 'm', 'j', 'u', '7', '8', 0, #30-3F
        0, ',', 'k', 'i', 'o', '0', '9', 0, 0, '.', '/', 'l', ';', 'p', '-', 0, #40-4F
        0, 0, '\'', 0, '[', '=', 0, 0, 'CAPSLOCK', 'RSHIFT', 'ENTER', ']', 0, '\\', 0, 0, # 50-5F
        0, 0, 0, 0, 0, 0, 'BKSP', 0, 0, '1', 0, '4', '7', 0, 0, 0, # 60-6F
        '0', '.', '2', '5', '6', '8', 'ESC', 0, 'F11', '+', '3', '-', '*', '9', 0, 0, # 70-7F
        0, 0, 0, 'F7', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 # 80-8F
    ],
    'ext': {
        0x11: 'RALT',
        0x14: 'RCTRL',
        0x1f: 'LGUI',
        0x27: 'RGUI',
        0x2F: 'APPS',
        0x4a: 'KP/',
        0x5a: 'KPENTER',
        0x6b: 'LEFT',
        0x74: 'RIGHT',
        0x75: 'UP',
        0x72: 'DOWN',
        0x69: 'END',
        0x6c: 'HOME',
        0x70: 'INSERT',
        0x71: 'DELETE',
        0x7a: 'PGDN',
        0x7d: 'PGUP',
        0x7e: 'SCROLLLOCK',
        0x77: 'NUMLOCK',
    }
}

class PS2Keyboard:
    
    def __init__(self, data_pin:microcontroller.Pin, clk_pin:microcontroller.Pin, scanset:dict=SCANSET2_US, debug:bool=False):
        self._kbd = ps2io.Ps2(data_pin, clk_pin)
        self.flush()
        self._scanset = scanset
        self._debug = debug
        self._leds = -1

    def flush(self) -> None:
        # clear any buffered data
        for i in range(len(self._kbd)):
            self._kbd.popleft()
    
    def sendcmd(self, value:int) -> int|None:
        try:
            rc = self._kbd.sendcmd(value)  # should return 0xFA (ACK)
            if self._debug:
                print("cmd:{:x} rc:{:x}".format(value, rc))
            return rc
        except RuntimeError:
            if self._debug:
                print("Failed to send cmd, cmd:{:x} err:{:x}".format(value, self._kbd.clear_errors()))
    
    def read(self, timeout:int=TIMEOUT) -> int|None:
        now = time.monotonic()
        while len(self._kbd) is 0:
            if time.monotonic() - now > timeout:
                return
        value = self._kbd.popleft()
        if self._debug:
            print("code:{:x}".format(value))
        return value

    def set_leds(self, scroll_lock:bool=False, num_lock:bool=False, caps_lock:bool=False):
        value = (caps_lock << 2) | (num_lock << 1) | (scroll_lock)
        if value != self._leds:
            self.sendcmd(value)
            self._leds = value

    def clear_leds(self):
        self.set_leds()

    def fill_leds(self):
        self.set_leds(True, True, True)

    def get_scancodeset_id(self, timeout=TIMEOUT) -> int|None:
        # get scancode set in use by keyboard
        self.sendcmd(0xF0)  # get/set scancode set
        self.sendcmd(0x00)  # get scancode subcmd
        return self.read(timeout)  # get codeset
    
    def key_translate(self, code, code_ext, code_release):
        if code_ext:  # extended scancode
            key = self._scanset['ext'].get(code)
        else:         # normal
            key = self._scanset['code'][code]
        return (key, code_release==0xF0)

    def read_key(self, timeout=TIMEOUT):
        code_ext = 0  # is this an extended keycode or not (normally 0xE0)
        code_release = 0 # is this a key-up, rather than a keydown (normally 0xF0)
        while True:
            code = self.read(timeout)
            if code is None:  # timeout
                return
            elif code == 0xE0:   # extended scancode
                code_ext = code
            elif code == 0xF0: # release scancode
                code_release = code
            #elif code == 
            elif code < len(self._scanset['code']):
                (key, release) = self.key_translate(code, code_ext, code_release)
                return (key, release, code, code_ext)
            else:
                if self._debug:
                    print("UNKNOWN code {:x}".format(code))
                return
