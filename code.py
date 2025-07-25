# SPDX-FileCopyrightText: 2025 Cooper Dalrymple
#
# SPDX-License-Identifier: GPLv3

import board
import microcontroller
import ps2io
import time

from adafruit_hid.keycode import Keycode
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS

import adafruit_ble
from adafruit_ble.advertising import Advertisement
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.standard.hid import HIDService
from adafruit_ble.services.standard.device_info import DeviceInfoService

## Configuration

DATA_PIN    = board.D9
CLOCK_PIN   = board.D10

TIMEOUT     = 0.01
DEBUG       = 1  # 0 = off, 1 = on, 2 = verbose

## Keycode Mapping

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

## PS/2 Keyboard

class PS2Keyboard:
    
    def __init__(self, data_pin:microcontroller.Pin, clk_pin:microcontroller.Pin, debug:bool=False):
        self._kbd = ps2io.Ps2(data_pin, clk_pin)
        self.flush()
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
            elif code <= 0x8F:
                return (code_release == 0xF0, code, code_ext)
            else:
                if self._debug:
                    print("UNKNOWN code {:x}".format(code))
                return

ps2 = PS2Keyboard(DATA_PIN, CLOCK_PIN, DEBUG > 1)

codeset_id = ps2.get_scancodeset_id()
if codeset_id is not None and DEBUG:
    print("keyboard is reporting scancode set: {:x}".format(codeset_id))

ps2.fill_leds()
time.sleep(0.5)
ps2.clear_leds()

## BLE

hid = HIDService()
device_info = DeviceInfoService(
    software_revision=adafruit_ble.__version__,
    manufacturer="Adafruit Industries"
)
advertisement = ProvideServicesAdvertisement(hid)
advertisement.appearance = 961
scan_response = Advertisement()

radio = adafruit_ble.BLERadio()
if radio.connected:
    for c in radio.connections:
        c.disconnect()

## HID

keyboard = Keyboard(hid.devices)
layout = KeyboardLayoutUS(keyboard)

## Loop

while True:

    # Connect via ble
    if DEBUG:
        print('advertising')
    radio.start_advertising(advertisement, scan_response)
    while not radio.connected:
        pass
    if DEBUG:
        print('connected')

    while radio.connected:
        try:
            # Read key from PS2
            rc = ps2.read_key()
        except:
            rc = None
        if rc is not None:
            (release, code, code_ext) = rc
            if DEBUG:
                print("ps2 code:{:x}/{:x} release:{:x}".format(code, code_ext, release))
            
            # Translate PS2 codes to HID keycode
            keycode = get_keycode(code, code_ext)
            if DEBUG:
                print("hid keycode:{:x} release:{:x}".format(keycode, release))
            
            # Send HID keycode
            if release:
                keyboard.release(keycode)
            else:
                keyboard.press(keycode)
    if DEBUG:
        print('disconnected')
