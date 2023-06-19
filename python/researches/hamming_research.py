import copy
import random

from utils import Bits


class HammingResearch:

    def __init__(self):
        """
        Данный тест направлен на оценку криптостойкости хеш-функции

        message_size: int - длина сообщения в бит
        count_tests: int - количество тестов
        """

        self._message_size = 10192
        self._count_tests = 5

    def test(self, hf):
        bits = hf.digest_size
        tests = []
        for test in range(self._count_tests):

            msg = Bits.from_int(random.getrandbits(self._message_size), self._message_size)
            hf.update(bytes(msg))
            a = hf.hexdigest()

            results = []
            for i in range(self._message_size):
                modified_message = copy.copy(msg)
                modified_message.bits[i] = msg.bits[i] ^ 1

                hf.update(bytes(modified_message))
                b = hf.hexdigest()

                a_binary = bin(int(a, 16)).replace("0b", "")
                b_binary = bin(int(b, 16)).replace("0b", "")

                a_binary = (bits - len(a_binary)) * '0' + a_binary
                b_binary = (bits - len(b_binary)) * '0' + b_binary

                counter = 0
                for j in range(bits):
                    if a_binary[j] != b_binary[j]:
                        counter += 1

                results.append(counter)
            tests.append((min(results), max(results), sum(results) / len(results)))

        return tests
