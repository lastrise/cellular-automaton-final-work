from utils import CellularHash
from researches.time_research import BaseTimeResearch


def encrypt(data: bytes, key: bytes, hf):
    iv = b"0" * hf.block_size

    len_padding = hf.block_size - (len(data) % hf.block_size)
    if len_padding == 0:
        len_padding = hf.block_size

    data += bytes([len_padding] * len_padding)
    last_c = iv
    cipher_text = bytes([])
    for i in range(len(data) // hf.block_size):
        block = data[i*hf.block_size:(i+1)*hf.block_size]
        block_integer = int.from_bytes(block, "big")
        hf.update(key + last_c, clear_data=True, with_calcs=True)

        last_c = (block_integer ^ int.from_bytes(hf.digest(), "big")).to_bytes(hf.block_size, "big")
        cipher_text += last_c
    return cipher_text


def decrypt(data: bytes, key: bytes, hf):
    iv = b"0" * hf.block_size

    last_c = iv
    plain_text = bytes([])
    for i in range(len(data) // hf.block_size):
        block = data[i * hf.block_size:(i + 1) * hf.block_size]
        block_integer = int.from_bytes(block, "big")
        hf.update(key + last_c, clear_data=True, with_calcs=True)

        last_c = block
        plain_text += (block_integer ^ int.from_bytes(hf.digest(), "big")).to_bytes(hf.block_size, "big")

    plain_text = plain_text.replace(bytes([plain_text[-1]]) * plain_text[-1], bytes([]))
    return plain_text


if __name__ == "__main__":
    """time_research = BaseTimeResearch(100)
    result = time_research.test(encrypt, bytes([1] * 100000), bytes([1, 2, 1]), hf=CellularHash(128, 30, 6))
    print(result)"""

    d = encrypt(bytes([1] * 1000), bytes([1, 2, 1]), hf=CellularHash(256, 130, 7))
    e = decrypt(d, bytes([1, 2, 1]), hf=CellularHash(256, 130, 7))
    print(e.hex())
