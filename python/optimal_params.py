import typing

from researches.hamming_research import HammingResearch
from researches.time_research import TimeResearch
from utils import CellularHash

time_test = TimeResearch(count_tests_per_size=3)
hamming_test = HammingResearch()


def define_optimal_params_crypto_resistance():
    """
    Повышение параметра count_compressions сильно сказывается на скорости при вычислении данных большого размера
    Поэтому стоит его минимизировать, но при этом уменьшение не должно быть в ущерб криптостойкости
    Сложность вычисления: O(count_compressions^count_blocks)

    HAMMING_DECLINE - максимальное отклонение для теста
    Если один hamming-тест превысил допустимое отклонение, то count_compressions увеличивается
    Если все тесты были пройдены, то было найдено оптимальное значение count_compressions для before_transform
    """

    MAX_HAMMING_DECLINE = 0.5
    digests = [(128, 5), (256, 5)]
    results = []
    for digest in digests:
        digest_size, min_compression = digest
        for before_transform in range(80, 250, 10):
            for count_compressions in range(min_compression, min_compression + 15, 1):
                hf = CellularHash(digest_size, before_transform, count_compressions)
                hamming_result = hamming_test.test(hf)

                min_hamming = min(hamming_result, key=lambda x: x[2])[2]
                if min_hamming >= digest_size // 2 - MAX_HAMMING_DECLINE:
                    print("[PASSED]", digest_size, before_transform, count_compressions, hamming_result)
                    results.append((digest_size, before_transform, count_compressions))
                    break
                else:
                    print("[NOT PASSED]", digest_size, before_transform, count_compressions, hamming_result)
    return results


def define_time_execution(params: typing.List[typing.Tuple[int, int, int]]):
    results = []
    for param in params:
        hf = CellularHash(*param)
        time_result = time_test.test(hf)
        results.append((param, time_result))
        print(time_result)
    return results


if __name__ == "__main__":
    # optimal_params = define_optimal_params_crypto_resistance()

    optimal_params = [(128, 20, 10), (128, 30, 6), (128, 80, 5),
                      (256, 30, 33), (256, 40, 31), (256, 50, 25),
                      (256, 80, 18), (256, 90, 14), (256, 100, 12),
                      (256, 110, 10), (256, 120, 8), (256, 130, 7)]

    define_time_execution(optimal_params)
