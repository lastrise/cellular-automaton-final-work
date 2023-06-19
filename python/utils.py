import typing as typing
import ctypes


class GoSlice(ctypes.Structure):
    _fields_ = [("data", ctypes.POINTER(ctypes.c_ubyte)), ("len", ctypes.c_longlong), ("cap", ctypes.c_longlong)]


class CellularHash:

    @staticmethod
    def __experimental_wrapper(block_size: int, before_transform: int, count_compression: int):
        def wrapper(message: GoSlice):
            return dll.ExperimentalAutomatonHash(ctypes.c_longlong(block_size),
                                                 ctypes.c_longlong(before_transform),
                                                 ctypes.c_longlong(count_compression),
                                                 message)
        return wrapper

    def __init__(self, hash_size: int, before_transform: int = 0, count_compression: int = 0, state: bytes = None):
        if not state:
            self._state = bytes([])
        else:
            self._state = state
        self._hash_function = None
        self._digest_size = hash_size // 8

        self._before_transform = before_transform
        self._count_compression = count_compression

        if not before_transform and not count_compression:
            if hash_size == 128:
                self._hash_function = dll.AutomatonHash128
            elif hash_size == 256:
                self._hash_function = dll.AutomatonHash256
            else:
                raise Exception("Unknown hash size")
        else:
            self._hash_function = self.__experimental_wrapper(self._digest_size, before_transform, count_compression)

        self._result = None

    @property
    def digest_size(self):
        return self._digest_size * 8

    @property
    def block_size(self):
        return self._digest_size

    def _sum(self):
        data = tuple(self._state)
        length = len(data)
        h = self._hash_function(GoSlice((ctypes.c_ubyte * length)(*data), length, length))
        arr = ctypes.cast(h, ctypes.POINTER(ctypes.c_ubyte))
        self._result = bytes(arr[:self._digest_size])

    def update(self, state: bytes, with_calcs=False, clear_data=False):
        if not clear_data:
            self._state += state
        else:
            self._state = state
        self._result = None
        if with_calcs:
            self._sum()

    def digest(self):
        if not self._result:
            self._sum()

        return self._result

    def hexdigest(self):
        if not self._result:
            self._sum()

        return self._result.hex()

    def copy(self):
        h = CellularHash(self.digest_size, self._before_transform, self._count_compression, self._state)
        return h

    def new(self, d):
        h = CellularHash(self.digest_size, self._before_transform, self._count_compression, d)
        return h


class Bits:
    def __init__(self, bits: typing.List[int]):
        self.bits = bits

    @classmethod
    def from_bytes(cls, data: bytes):
        bits = []
        for char in data:
            binary = list(map(int, bin(char).replace("0b", "")))
            binary = [0] * (8 - len(binary)) + binary
            bits += binary
        return cls(bits)

    @classmethod
    def from_int(cls, data: int, min_bits: int = 0):
        bits = list(map(int, bin(data).replace("0b", "")))
        diff = min_bits - len(bits)
        add = 0 if diff <= 0 else diff
        bits = [0] * add + bits
        return cls(bits)

    def __bytes__(self):
        result = b""
        for i in range(len(self.bits) // 8):
            bits = self.bits[i * 8:(i + 1) * 8]
            byte = int(''.join(map(str, bits)), 2)
            symbol = bytes([byte])
            result += symbol
        return result

    def __copy__(self):
        return Bits(self.bits[::])


dll = ctypes.cdll.LoadLibrary("./lib/darwin_arm64/cahashlib.so")
dll.ExperimentalAutomatonHash.argtypes = [ctypes.c_longlong, ctypes.c_longlong, ctypes.c_longlong, GoSlice]
dll.ExperimentalAutomatonHash.restype = ctypes.c_void_p
