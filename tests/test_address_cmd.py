import pytest

from app_client.exception import BOLOSPathPrefixError, WrongDataLengthError

def test_address(cmd, button):
    cmd.get_address(button=button, bip32_path="m/44'/280'/0'/0")
    cmd.get_address(button=button, bip32_path="m/44'/280'/0'/0/0")
    cmd.get_address(button=button, bip32_path="m/44'/280'/0'/0/1")

def test_address_limits(cmd, button, headless):

    # only test this when on hardware
    # speculos does not have this protection
    if not headless:
        with pytest.raises(BOLOSPathPrefixError):
            cmd.get_address_with_error(button=button, bip32_path="m/44'/28'")
        with pytest.raises(BOLOSPathPrefixError):
            cmd.get_address_with_error(button=button, bip32_path="m/44'/280'/1")

    with pytest.raises(WrongDataLengthError):
        # more than 5 indexes
        cmd.get_address_with_error(button=button, bip32_path="m/44'/280'/0'/0/1/0")

    with pytest.raises(WrongDataLengthError):
        # Over the MAX_DERIVATION_LIMIT on the 5th index
        cmd.get_address_with_error(button=button, bip32_path="m/44'/280'/0'/0/{}".format(1+(1<<20)))

    with pytest.raises(WrongDataLengthError):
        # More than 1 on the 4th index
        cmd.get_address_with_error(button=button, bip32_path="m/44'/280'/0'/2/0")
