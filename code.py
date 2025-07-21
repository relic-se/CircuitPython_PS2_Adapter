# SPDX-FileCopyrightText: 2025 Cooper Dalrymple
#
# SPDX-License-Identifier: GPLv3

import board
from ps2 import PS2Keyboard
from keycode import get_keycode
import time

DEBUG       = True

DATA_PIN    = board.D9
CLOCK_PIN   = board.D10

time.sleep(1)
print("PS2 to USB/Bluetooth Keyboard")

kbd_ps2 = PS2Keyboard(DATA_PIN, CLOCK_PIN, debug=DEBUG)

codeset_id = kbd_ps2.get_scancodeset_id()
if codeset_id is not None:
    print("keyboard is reporting scancode set: {:x}".format(codeset_id))

kbd_ps2.fill_leds()

try:
    from usb import USBKeyboard
    kbd_usb = USBKeyboard(debug=DEBUG)
except ImportError:
    kbd_usb = None

try:
    from ble import BLEKeyboard
    kbd_ble = BLEKeyboard(debug=DEBUG)
except ImportError:
    kbd_ble = None

kbd_ps2.clear_leds()

while True:

    # Read keys from PS2 and translate to HID
    rc = kbd_ps2.read_key()
    if rc is not None:
        (key, release, code, code_ext) = rc
        if DEBUG:
            print("key:{:s} code:{:x}/{:x}: release:{:x}".format(str(key), code, code_ext, release))
        
        keycode = get_keycode(code, code_ext)

        if kbd_usb is not None:
            kbd_usb.send(keycode, release)
        elif kbd_ble is not None:
            kbd_ble.send(keycode, release)

    if kbd_usb is not None:
        # update leds
        kbd_ps2.set_leds(*kbd_usb.get_leds())
    # ReportOut + ReportIn not currently working (https://github.com/adafruit/Adafruit_CircuitPython_BLE/issues/207)
    #elif kbd_ble is not None:
    #    kbd_ps2.set_leds(*kbd_ble.get_leds())
