from tests.hash_equals_test import HashEqualsTest
from utils import CellularHash as GolangCellularHash
from lib.cahash import CellularHash as PythonCellularHash

if __name__ == "__main__":
    gch = GolangCellularHash(256, 130, 7)
    pch = PythonCellularHash(256, 130, 7)
    HashEqualsTest(gch, pch, count_tests=1000).test()
