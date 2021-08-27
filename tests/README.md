# End-to-end tests

These tests are implemented in Python and can be executed either using the [Speculos](https://github.com/LedgerHQ/speculos) emulator or a Ledger Nano S/X.
Python dependencies are listed in [requirements.txt](requirements.txt), install them using [pip](https://pypi.org/project/pip/)

```
pip install -r requirements.txt
```

### Launch with Speculos

First start your application with Speculos

```
./path/to/speculos.py /path/to/app.elf --ontop --sdk 2.0
```

If you do not want to launch the http button api, use the tcp instead:

```
python /speculos/speculos.py bin/app.elf --apdu-port 9999 --button-port 42000 --automation-port 43000 --ontop --sdk 2.0
```

### Run tests

First go to the `tests` folder.

For automated tests run:

```
pytest --headless
```

For manual tests the command is `pytest`.

And if using the TCP interface (only for automated):
```
pytest --headless --tcp
```

### Launch with your Nano S/X

To run the tests on your Ledger Nano S/X you also need to install an optional dependency

```
pip install ledgercomm[hid]
```

Be sure to have you device connected through USB (without any other software interacting with it) and run

```
pytest --hid
```
