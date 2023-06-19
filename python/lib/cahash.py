import typing
from utils import Bits


class CellularHash:
    def __init__(self, hash_size: int, before_transform: int = 0, count_compression: int = 0):
        self._state = bytes([])
        self._digest_size = hash_size // 8
        self._before_transform = before_transform
        self._count_compression = count_compression
        self._result = None

    @staticmethod
    def padding(length: int, size: int):
        if length % size < size - 8:
            t = size - 8 - length % size
        else:
            t = size + size - 8 - length % size

        b = bytes([0x80] + [0x00] * (t - 1))
        b += (length << 3).to_bytes(8, "big", signed=False)
        return b

    @property
    def digest_size(self):
        return self._digest_size * 8

    def update(self, state: bytes):
        self._state = state

        block_size = self._digest_size
        bit_block_size = self.digest_size

        data = self._state
        data += self.padding(len(data), block_size)

        cellar = CellarContainer.from_bytes(data)
        automate = CellarAutomate([WolframRule(30), WolframRule(105)])

        history = []
        blocks = [[0] * bit_block_size for _ in range(len(data) // block_size)]
        iterations_before_transform = self._before_transform

        for i in range(bit_block_size + iterations_before_transform):
            cellar = automate.evaluate(cellar)
            if i >= iterations_before_transform:
                history.append(str(cellar))

        for index_evaluation, evaluation in enumerate(history):
            for i in range(len(evaluation) // bit_block_size):
                blocks[i][bit_block_size - index_evaluation - 1] = int(
                    evaluation[i * bit_block_size + bit_block_size - index_evaluation - 1])

        result = []
        for block in blocks:
            result += block

        automate = CellarContainer(result)
        transform = bytes(automate)

        state = transform[0:block_size] * 2
        for i in range(len(data) // block_size):
            block = data[i * block_size:i * block_size + block_size]

            container = CellarContainer.from_bytes(block)
            transform_data = CellarContainer.from_bytes(transform[i * block_size:i * block_size + block_size])

            for j in range(self._count_compression):
                compress = CellarAutomate.evaluate_compress(container, CellarContainer.from_bytes(state).bits)
                container = compress

            state = bytes(CellarContainer([transform_data.bits[i] ^ container.bits[i] for i in range(bit_block_size)]))
            state += state

        self._result = state[:self._digest_size]

    def digest(self):
        return self._result

    def hexdigest(self):
        return self._result.hex()

    def copy(self):
        return self


class WolframRule:
    def __init__(self, number: int):
        self._number = number
        self._table = bin(self._number).replace("0b", "")[::-1]
        self._table += "0" * (8 - len(self._table))
        self._table = list(map(int, self._table))

    def produce(self, number: int) -> int:
        return self._table[number]


class CellarIterator:
    def __init__(self, bits: typing.List[int]):
        self._bits = bits
        self._current = [self._bits[len(self._bits) - 1], self._bits[0], self._bits[1]]
        self._index = 2

        self._start = True

    def __next__(self):
        if self._start:
            self._start = False
        elif self._index == 2:
            raise StopIteration

        result = self._current[0] * 4 + self._current[1] * 2 + self._current[2]
        self._current = self._current[1:] + [self._bits[self._index]]
        self._index = (self._index + 1) % len(self._bits)

        return result


class CellarContainer(Bits):
    def __iter__(self):
        return CellarIterator(self.bits)

    def __str__(self):
        return ''.join(map(str, self.bits))


class CellarAutomate:
    def __init__(self, rules: typing.List[WolframRule]):
        self._rules = rules

    def evaluate(self, data: CellarContainer):
        evaluation = []
        current_rule = 0
        for cell in data:
            rule = self._rules[current_rule]
            evaluation.append(rule.produce(cell))
            current_rule = (current_rule + 1) % len(self._rules)
        return CellarContainer(evaluation)

    @staticmethod
    def evaluate_compress(data: CellarContainer, state: typing.List[int]):
        evaluation = []
        rules = [WolframRule(30), WolframRule(90), WolframRule(105), WolframRule(150)]
        table = [[rules[0], rules[1], rules[2], rules[3]],
                 [rules[1], rules[0], rules[3], rules[2]],
                 [rules[2], rules[3], rules[0], rules[1]],
                 [rules[3], rules[2], rules[1], rules[0]]]

        for i, cell in enumerate(data):
            rule = state[i * 2:(i+1) * 2]
            rule_sequence = table[rule[0] << 1 | rule[1]]
            rule = rule_sequence[i % 4]
            evaluation.append(rule.produce(cell))
        return CellarContainer(evaluation)
