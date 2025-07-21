# SPDX-FileCopyrightText: 2025 Cooper Dalrymple
#
# SPDX-License-Identifier: GPLv3

try:
    import usb_hid, usb_midi, storage
    usb_hid.enable((usb_hid.Device.KEYBOARD,), boot_device=1)
    usb_midi.disable()
    storage.disable_usb_drive()
except ImportError:
    print("Native USB not supported")
