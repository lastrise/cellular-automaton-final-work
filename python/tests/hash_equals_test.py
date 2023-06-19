import random


class HashEqualsTest:
    def __init__(self, first_hf, second_hf, count_tests: int = 100):
        self._first_hf = first_hf
        self._second_hf = second_hf
        self._count_tests = count_tests

    def test(self):
        for i in range(self._count_tests):
            msg_size = random.randint(1, 100)
            msg = random.randbytes(msg_size)

            self._first_hf.update(msg)
            self._second_hf.update(msg)
            assert self._first_hf.hexdigest() == self._second_hf.hexdigest()
