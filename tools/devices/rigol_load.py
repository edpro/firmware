import time
from typing import Optional

import usbtmc

from tools.common.logger import LoggedError, Logger

logger = Logger("ri_load")


# noinspection PyPep8Naming
class RigolLoad:
    """
    handles communication with RIGOL DC load
    Python USB lib: https://github.com/python-ivi/python-usbtmc
    Windows driver installation:
     1. install Ultra Sigma from www.rigol.eu
     3. use Zadig (https://zadig.akeo.ie) to repalce driver with libusb-win32
    Manual: https://www.batronix.com/files/Rigol/Elektronische-Lasten/DL3000/DL3000_ProgrammingManual_EN.pdf
    """

    def __init__(self):
        self._device: Optional[usbtmc.Instrument] = None

    def connect(self):
        logger.info("connect")
        try:
            self._device = usbtmc.Instrument(0x1AB1, 0x0E11)
        except Exception as e:
            logger.throw(str(e))
        self._ask("*IDN?")

    def reset(self):
        self._write("*RST")
        self.wait()

    def wait(self):
        self._write("*WAI")

    def close(self):
        logger.info("disconnect")
        if self._device:
            self._device.close()

    def _write(self, cmd: str):
        logger.trace(f"<- {cmd}")
        try:
            self._device.write(cmd)
        except Exception as e:
            logger.throw(e)

    def _ask(self, cmd: str) -> str:
        logger.trace(f"<- {cmd}")
        response = ""
        try:
            response = self._device.ask(cmd)
            logger.trace(f"-> {response}")
        except Exception as e:
            logger.throw(e)

        return response

    def measure_voltage(self) -> float:
        response = self._ask(":MEASure:VOLTage?")
        return float(response)

    def measure_current(self) -> float:
        response = self._ask(":MEASure:CURRent?")
        return float(response)

    def measure_current_max(self) -> float:
        response = self._ask(":MEASure:CURRent:MAX?")
        return float(response)

    def set_pulse_current(self, value: float, width_ms: float):
        self._write(f":SOURce:CURRent:TRANsient:MODE PULSe")
        self._write(f":SOURce:CURRent:TRANsient:ALEVel {value}")
        self._write(f":SOURce:CURRent:TRANsient:BLEVel {0.0}")
        self._write(f":SOURce:CURRent:TRANsient:AWIDth {width_ms}")
        self._write(f":SOURce:CURRent:TRANsient:BWIDth {width_ms}")
        self._write(f":SOURce:CURRent:SLEW {1.0}")
        self._write(":TRIGger:SOURce BUS")
        self.wait()

    def trigger(self):
        self._write(":TRIGger")
        self.wait()

    def set_const_current(self, value: float):
        self._write(f":SOURce:FUNCtion CURRent")
        self._write(f":SOURce:CURRent {value}")

    def get_func(self) -> str:
        return self._ask(":SOURce:FUNCtion?")

    def set_input(self, isOn: int):
        self._write(f":SOURce:INPut {isOn}")
        self.wait()


def test():
    device = RigolLoad()
    try:
        device.connect()
        device.reset()

        # device.measure_voltage()
        # device.measure_current()

        # device.set_const_current(0.1)
        # device.get_func()
        # device.set_input(1)
        # time.sleep(1.0)
        # device.measure_voltage()
        # device.measure_current()
        # device.set_input(0)

        # device.set_pulse_current(value=5, width_ms=0.03)
        device.set_pulse_current(value=1, width_ms=5)
        device.trigger()
        time.sleep(0.1)
        device.set_input(isOn=0)

    except LoggedError:
        pass
    except Exception:
        raise
    finally:
        device.close()


if __name__ == "__main__":
    test()
