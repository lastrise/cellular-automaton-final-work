import time
import random


class BaseTimeResearch:
    def __init__(self, count_tests: int = 3):
        self._count_tests = count_tests

    def test(self, func, *args, **kwargs):
        tests = []
        for i in range(self._count_tests):
            start = time.time()
            func(*args, **kwargs)
            end = time.time()
            tests.append(end - start)
        return min(tests), max(tests), sum(tests) / len(tests)


class TimeResearch(BaseTimeResearch):

    SMALL_SIZE = 10
    MEDIUM_SIZE = 50
    BIG_SIZE = 100

    MB = 1024 * 1024

    def __init__(self, count_tests_per_size: int = 3):
        """
        Данный тест вычисляет время выполнения хеш-функции для данных разных размеров
        count_tests_per_size: int - количество выполнений хеш-функции на размер
        """
        super().__init__(count_tests_per_size)
        self._count_tests_per_size = count_tests_per_size

    def test(self, func, *args, **kwargs):
        """
        hf - хеш-функция
        Возвращает список кортежей с минимальным, максимальным, средним временем выполнения на каждый размер
        """
        tests = []

        sizes = [TimeResearch.SMALL_SIZE * TimeResearch.MB,
                 TimeResearch.MEDIUM_SIZE * TimeResearch.MB,
                 TimeResearch.BIG_SIZE * TimeResearch.MB]

        for size in sizes:
            tests.append(super().test(func.update, random.randbytes(size), True, **kwargs))
        return tests
