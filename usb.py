# SPDX-FileCopyrightText: 2025 Cooper Dalrymple
#
# SPDX-License-Identifier: GPLv3

try:
    import usb_hid
except:
    raise ImportError("Native USB not supported")

from keyboard import Keyboard

class USBKeyboard(Keyboard):
    
    def __init__(self, layout=None, debug:bool=False):
        super().__init__(usb_hid.devices, layout=layout, debug=debug)
