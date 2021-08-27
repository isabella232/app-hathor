#!/usr/bin/env python3
"""
    Speculos raises an ApduException if any command returns something other than SW_OK (0x9000)
    This is to prevent unintended execution, but is also bad for testing

    This script simply relaunches the speculos emulator on any ApduException
"""
from speculos.main import main
from speculos.client import ApduException


if __name__ == "__main__":
    while True:
        try:
            main()
            break
        except ApduException as ex:
            print(ex)
