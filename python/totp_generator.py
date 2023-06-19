import onetimepass
from utils import CellularHash
from researches.time_research import BaseTimeResearch


if __name__ == "__main__":
    digest_method = CellularHash(256, 130, 7)

    # Метод вызывается для инициализации библиотеки
    digest_method.new(b"").update(b"init", with_calcs=True)

    research = BaseTimeResearch(count_tests=5000)
    result = research.test(onetimepass.get_totp, secret="MFRGGZDFMZTWQ2LK", digest_method=digest_method)
    print(result)
