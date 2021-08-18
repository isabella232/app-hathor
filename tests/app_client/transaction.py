from io import BytesIO
from typing import Union, List, Iterator, Tuple

from app_client.utils import read, read_uint, UINT64_MAX


class TransactionError(Exception):
    pass

class TxInput:
    def __init__(self, tx_id: bytes, index: int, bip32_path: List[int]=None):
        assert len(tx_id) == 32
        self.tx_id = tx_id
        self.index = index
        self.bip32_path = bip32_path

    def serialize(self) -> bytes:
        return b''.join([
            self.tx_id,
            self.index.to_bytes(1, byteorder='big'),
            b'\x00\x00'
        ])

    def validate_address(self, bip32_path: List[int]) -> bool:
        if self.bip32_path is None:
            raise TransactionError('Input: no self.bip32_path')

        if len(bip32_path) != len(self.bip32_path):
            return False

        for i in range(len(bip32_path)):
            if self.bip32_path[i] != bip32_path[i]:
                return False
        return True

    @classmethod
    def from_bytes(cls, hexa: Union[bytes, BytesIO]):
        buf: BytesIO = BytesIO(hexa) if isinstance(hexa, bytes) else hexa

        tx_id: bytes = read(buf, 32)
        index: int = read_uint(buf, 8, byteorder='big')
        data_len: int = read_uint(buf, 16, byteorder='big')
        if data_len != 0:
            raise TransactionError('Input: data length MUST be 0')

        return cls(tx_id, index)

class TxOutput:
    def __init__(self, value: int, script: bytes):
        self.value = value
        self.script = script

    def serialize_value(self) -> bytes:
        if self.value & 0x80000000:
            # value will use 8 bytes
            return (-self.value).to_bytes(8, byteorder='big', signed=True)
        return self.value.to_bytes(4, byteorder='big')

    def serialize(self) -> bytes:
        script_len = len(self.script)

        return b''.join([
            self.serialize_value(),
            b'\x00', # token data
            script_len.to_bytes(2, byteorder='big'),
            self.script,
        ])

    @classmethod
    def from_bytes(cls, hexa: Union[bytes, BytesIO]):
        buf: BytesIO = BytesIO(hexa) if isinstance(hexa, bytes) else hexa

        b = buf.read(1)
        buf.seek(-1, 1)

        value: int = 0
        if b & 0x80:
            value = -read_int(buf, 64, byteorder='big')
        else:
            value = read_uint(buf, 32, byteorder='big')

        token_data: bytes = read(buf, 1)
        script_len, script = read_var(buf)

        return cls(value, script)


class Transaction:
    def __init__(self, tx_version, tokens: List[bytes], inputs: List[TxInput], outputs: List[TxOutput]) -> None:
        self.tx_version = tx_version
        self.tokens = tokens
        self.inputs = inputs
        self.outputs = outputs

    def serialize(self, prefix: bytes, max_len: int) -> Iterator[Tuple[int, bytes]]:
        ''' This serialize returns the number of complete outputs on each chunk
            this is imperative for testing, we need to know how many outputs to confirm
        '''
        cdata = b''.join([
            prefix,
            self.tx_version.to_bytes(2, byteorder='big'),
            len(self.tokens).to_bytes(1, byteorder='big'),
            len(self.inputs).to_bytes(1, byteorder='big'),
            len(self.outputs).to_bytes(1, byteorder='big'),
        ])
        if len(cdata) > max_len:
            yield 0, cdata[:max_len]
            cdata = cdata[max_len:]

        for token in self.tokens:
            cdata = b''.join([cdata, token])
            if len(cdata) > max_len:
                yield 0, cdata[:max_len]
                cdata = cdata[max_len:]

        for tx_input in self.inputs:
            input_bytes = tx_input.serialize()
            cdata = b''.join([cdata, input_bytes])
            if len(cdata) > max_len:
                yield 0, cdata[:max_len]
                cdata = cdata[max_len:]

        output_num = 0
        for tx_output in self.outputs:
            output_bytes = tx_output.serialize()
            cdata = b''.join([cdata, output_bytes])
            if len(cdata) > max_len:
                yield output_num, cdata[:max_len]
                cdata = cdata[max_len:]
                output_num = 0
            output_num += 1

        if len(cdata) != 0:
            yield output_num, cdata

    @classmethod
    def from_bytes(cls, hexa: Union[bytes, BytesIO]):
        buf: BytesIO = BytesIO(hex) if isinstance(hexa, bytes) else hexa

        tx_version: int = read_uint(buf, 16, byteorder="big")
        num_tokens: int = read_uint(buf, 8, byteorder="big")
        num_inputs: int = read_uint(buf, 8, byteorder="big")
        num_outputs: int = read_uint(buf, 8, byteorder="big")

        tokens = []
        for _ in range(num_tokens):
            tokens.append(read(buf, 32))

        inputs = []
        for _ in range(num_inputs):
            input_bytes = read(buf, 32)
            tx_input = TxInput.from_bytes(input_bytes)
            inputs.append(tx_input)

        outputs = []
        for _ in range(num_outputs):
            output_bytes = read(buf, 32)
            tx_output = TxOutput.from_bytes(output_bytes)
            outputs.append(tx_output)

        return cls(tx_version, tokens, inputs, outputs)