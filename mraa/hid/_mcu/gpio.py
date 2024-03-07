# ========================================================================== #
#                                                                            #
#    Customized version from gpio.py for the serial UART driver for mraa     #
#                                                                            #
# ========================================================================== #


import types
import time

import mraa

from ....logging import get_logger


# =====
class Gpio:  # pylint: disable=too-many-instance-attributes
    def __init__(
        self,
        device_path: str,
        power_detect_pin: int,
        power_detect_pull_down: bool,
        reset_pin: int,
        reset_inverted: bool,
        reset_delay: float,
    ) -> None:

        self.__device_path = device_path
        self.__power_detect_pin = power_detect_pin
        self.__power_detect_pull_down = power_detect_pull_down
        self.__reset_pin = reset_pin
        self.__reset_inverted = reset_inverted
        self.__reset_delay = reset_delay

        self.__power_detect_gpio: (mraa.Gpio | None) = None
        self.__reset_gpio: (mraa.Gpio | None) = None

        self.__last_power: (bool | None) = None

    def __enter__(self) -> None:
        if self.__power_detect_pin >= 0 or self.__reset_pin >= 0:
            assert self.__power_detect_gpio is None
            assert self.__reset_gpio is None
            if self.__power_detect_pin >= 0:
                self.__power_detect_gpio = mraa.Gpio(self.__power_detect_pin)
                self.__power_detect_gpio.dir(mraa.DIR_IN)
                if self.__power_detect_pull_down:
                    self.__power_detect_gpio.mode(mraa.MODE_PULLDOWN)
            if self.__reset_pin >= 0:
                self.__reset_gpio = mraa.Gpio(self.__reset_pin)
                self.__reset_gpio.dir(mraa.DIR_OUT)
                self.__reset_gpio.write(int(self.__reset_inverted))

    def __exit__(
        self,
        _exc_type: type[BaseException],
        _exc: BaseException,
        _tb: types.TracebackType,
    ) -> None:

        if self.__power_detect_gpio or self.__reset_gpio:
            self.__last_power = None
            self.__power_detect_gpio = None
            self.__reset_gpio = None

    def is_powered(self) -> bool:
        if self.__power_detect_gpio is not None:
            power = bool(self.__power_detect_gpio.read())
            if power != self.__last_power:
                get_logger(0).info("HID power state changed: %s -> %s", self.__last_power, power)
                self.__last_power = power
            return power
        return True

    def reset(self) -> None:
        if self.__reset_gpio is not None:
            try:
                self.__reset_gpio.write(int(not self.__reset_inverted))
                time.sleep(self.__reset_delay)
            finally:
                self.__reset_gpio.write(int(self.__reset_inverted))
                time.sleep(1)
            get_logger(0).info("Reset HID performed")