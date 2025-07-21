# SPDX-FileCopyrightText: 2025 Cooper Dalrymple
#
# SPDX-License-Identifier: GPLv3

import adafruit_ble
from adafruit_ble.advertising import Advertisement
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.standard.hid import HIDService
from adafruit_ble.services.standard.device_info import DeviceInfoService

from keyboard import Keyboard

class BLEKeyboard(Keyboard):
    
    def __init__(self, layout=None, debug:bool=False):
        self._hid = HIDService()
        self._device_info = DeviceInfoService(software_revision=adafruit_ble.__version__, manufacturer="relic-se")
        self._advertisement = ProvideServicesAdvertisement(self._hid)
        self._advertisement.appearance = 0x03C1  # Keyboard (https://www.bluetooth.com/specifications/assigned-numbers/)

        self._scan_response = Advertisement()
        self._scan_response.complete_name = "CircuitPython PS2 Adapter"

        self._ble = adafruit_ble.BLERadio()
        if not self._ble.connected:
            if debug:
                print('advertising')
            self._ble.start_advertising(self._advertisement, self._scan_response)
        else:
            if debug:
                print('already connected')
                print(self._ble.connections)

        super().__init__(self._hid.devices, layout=layout, debug=debug)

    def press(self, value:str|int|tuple[int]) -> None:
        if self._ble.connected:
            super().press(value)
            
    def release(self, value:str|int|tuple[int]) -> None:
        if self._ble.connected:
            super().release(value)
    
    def flush(self) -> None:
        if self._ble.connected:
            super().flush()

    def get_leds(self) -> tuple[bool]:
        if self._ble.connected:
            return super().get_leds()
        else:
            return (False, False, False)
