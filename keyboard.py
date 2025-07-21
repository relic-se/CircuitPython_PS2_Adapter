# SPDX-FileCopyrightText: 2025 Cooper Dalrymple
#
# SPDX-License-Identifier: GPLv3

from adafruit_hid.keyboard import Keyboard as HIDKeyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS

class Keyboard:
    
    def __init__(self, devices, layout=None, debug:bool=False):
        self._kbd = HIDKeyboard(devices)
        if layout is None:
            layout = KeyboardLayoutUS
        self._layout = layout(self._kbd)
        self._debug = debug

        self.flush()

    def _sanitize(self, value:str|int|tuple[int]) -> tuple[int]:
        if isinstance(value, str):
            return self._layout.keycodes(value)
        elif isinstance(value, int):
            return (value,)
        return value

    def press(self, value:str|int|tuple[int]) -> None:
        self._kbd.press(*self._sanitize(value))
    
    def release(self, value:str|int|tuple[int]) -> None:
        self._kbd.release(*self._sanitize(value))
    
    def send(self, value:str|int|tuple[int], release:bool=False) -> None:
        if not release:
            self.press(value)
        else:
            self.release(value)
    
    def flush(self) -> None:
        self._kbd.release_all()

    def get_leds(self) -> tuple[bool]:
        status = self._kbd.led_status
        scroll_lock = bool(status & Keyboard.LED_SCROLL_LOCK)
        num_lock = bool(status & Keyboard.LED_NUM_LOCK)
        caps_lock = bool(status & Keyboard.LED_CAPS_LOCK)
        return (scroll_lock, num_lock, caps_lock)
