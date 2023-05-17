import random
import pytest
import base64
from typing import Callable


def create_secret(length: int = 50) -> bytes:
    return random.randbytes(length)


def create_door_share_from_a_byte(door_name_byte: int) -> bytearray:
    res = bytearray(4)
    for i in range(8):
        bit = (door_name_byte >> i) & 1
        color = "0011" if bit == 0 else "0111"
        shuffled = "".join(random.sample(color, len(color)))
        door_share_4bit = int(shuffled, 2)
        res[i // 2] |= door_share_4bit << (i % 2) * 4
    return res


def test_create_door_share_from_a_byte():
    tmp = decode(create_door_share_from_a_byte(48), decode_share_byte, 1)
    assert tmp == b"0"
    assert get_share_name(tmp) == "0"


def create_door_share(door_name: str, length: int = 50) -> bytes:
    door_name_bytes = door_name.encode().ljust(length, b"\0")
    door_share = bytearray(length)
    for i in range(length):
        door_share_4byte = create_door_share_from_a_byte(door_name_bytes[i])
        door_share[i * 4 : (i + 1) * 4] = door_share_4byte
    return bytes(door_share)


def create_user_share_from_a_byte(
    user_name_byte: int,
    secret_byte: int,
    door_share_slice: bytes,
) -> bytearray:
    table = [
        [
            {
                # secret white, user white
                3: [5, 6, 9, 10],
                5: [3, 6, 9, 12],
                6: [3, 5, 10, 12],
                7: [3, 5, 6],
                9: [3, 5, 10, 12],
                10: [3, 6, 9, 12],
                11: [3, 9, 10],
                12: [5, 6, 9, 10],
                13: [5, 9, 12],
                14: [6, 10, 12],
            },
            {
                # secret white, user black
                3: [7, 11],
                5: [7, 13],
                6: [7, 14],
                7: [7],
                9: [11, 13],
                10: [11, 14],
                11: [11],
                12: [13, 14],
                13: [13],
                14: [14],
            },
        ],
        [
            {
                # secret black, user white
                3: [12],
                5: [10],
                6: [9],
                7: [9, 10, 12],
                9: [6],
                10: [5],
                11: [5, 6, 12],
                12: [3],
                13: [3, 6, 10],
                14: [3, 5, 9],
            },
            {
                # secret black, user black
                3: [13, 14],
                5: [11, 14],
                6: [11, 13],
                7: [11, 13, 14],
                9: [7, 14],
                10: [7, 13],
                11: [7, 13, 14],
                12: [7, 11],
                13: [7, 11, 14],
                14: [7, 11, 13],
            },
        ],
    ]
    res = bytearray(4)
    for i in range(8):
        secret_color = (secret_byte >> i) & 1
        user_color = (user_name_byte >> i) & 1
        door_share_4bit = (door_share_slice[i // 2] >> (i % 2) * 4) & 0xF

        choices = table[secret_color][user_color][door_share_4bit]
        user_share_4bit = random.choice(choices)

        res[i // 2] |= user_share_4bit << (i % 2) * 4
    return res


def test_create_user_share_from_a_byte():
    user_name_byte = 49
    secret_byte = 28
    door_share_slice = b"\xe5\xbeu\x9d"
    user_share_4byte = create_user_share_from_a_byte(
        user_name_byte, secret_byte, door_share_slice
    )

    decoded = decode(user_share_4byte, decode_share_byte, 1)
    assert decoded == b"1"

    tmp1 = 0
    for i in range(4):
        tmp2 = door_share_slice[i] | user_share_4byte[i]
        if (tmp2 & 0xF).bit_count() == 3:
            assert (secret_byte >> i * 2) & 1 == 0
        else:
            tmp1 |= 1 << i * 2
            assert (secret_byte >> i * 2) & 1 == 1
        if (tmp2 >> 4).bit_count() == 3:
            assert (secret_byte >> i * 2 + 1) & 1 == 0
        else:
            tmp1 |= 1 << i * 2 + 1
            assert (secret_byte >> i * 2 + 1) & 1 == 1
    assert tmp1.to_bytes(1, "big") == secret_byte.to_bytes(1, "big")


def create_user_share(
    user_name: str,
    secret: bytes,
    door_share: bytes,
    length: int = 50,
) -> bytes:
    user_name_bytes = user_name.encode().ljust(length, b"\0")
    user_share = bytearray(length * 4)
    for i in range(length):
        user_share_4byte = create_user_share_from_a_byte(
            user_name_bytes[i],
            secret[i],
            door_share[i * 4 : (i + 1) * 4],
        )
        user_share[i * 4 : (i + 1) * 4] = user_share_4byte

    return bytes(user_share)


def test_create_user_share():
    length = 1
    user_name = "1"
    secret = int.to_bytes(28)
    door_share = b"\xe5\xbeu\x9d"
    decoded_door_share = decode(door_share, decode_share_byte, length)
    user_share = create_user_share(user_name, secret, door_share, length)
    decoded_user_share = decode(user_share, decode_share_byte, length)
    assert get_share_name(decoded_user_share) == user_name

    secret_byte = secret[0]
    for i in range(4):
        tmp = user_share[i] | door_share[i]
        assert (secret_byte >> i * 2) & 1 == (0 if (tmp & 0xF).bit_count() == 3 else 1)
        assert (secret_byte >> i * 2 + 1) & 1 == (
            0 if (tmp >> 4).bit_count() == 3 else 1
        )

    overlapped = overlap(door_share, user_share, length * 4)
    assert decode(overlapped, decode_overlapped_byte, length) == secret


def decode_share_byte(byte: int) -> int:
    lower_byte_cnt = (byte & 0xF).bit_count()
    higher_byte_cnt = ((byte >> 4) & 0xF).bit_count()

    if lower_byte_cnt == 2 and higher_byte_cnt == 2:
        return 0b00
    elif lower_byte_cnt == 2 and higher_byte_cnt == 3:
        return 0b10
    elif lower_byte_cnt == 3 and higher_byte_cnt == 2:
        return 0b01
    elif lower_byte_cnt == 3 and higher_byte_cnt == 3:
        return 0b11
    else:
        raise Exception("byte count == 0, 1, or 4")


def test_decode_share_byte():
    assert decode_share_byte(0b01010101) == 0b00
    assert decode_share_byte(0b01011100) == 0b00
    assert decode_share_byte(0b11000110) == 0b00

    assert decode_share_byte(0b01010111) == 0b01
    assert decode_share_byte(0b10011011) == 0b01

    assert decode_share_byte(0b11010011) == 0b10
    assert decode_share_byte(0b10111001) == 0b10

    assert decode_share_byte(0b11101101) == 0b11
    assert decode_share_byte(0b11010111) == 0b11

    with pytest.raises(Exception):
        decode_share_byte(0b10010000)
    with pytest.raises(Exception):
        decode_share_byte(0b10010010)
    with pytest.raises(Exception):
        decode_share_byte(0b10011111)
    with pytest.raises(Exception):
        decode_share_byte(0b00000101)
    with pytest.raises(Exception):
        decode_share_byte(0b01000101)
    with pytest.raises(Exception):
        decode_share_byte(0b11110101)


def decode_overlapped_byte(byte: int) -> int:
    lower_byte_cnt = (byte & 0xF).bit_count()
    higher_byte_cnt = ((byte >> 4) & 0xF).bit_count()

    if lower_byte_cnt == 3 and higher_byte_cnt == 3:
        return 0b00
    elif lower_byte_cnt == 3 and higher_byte_cnt == 4:
        return 0b10
    elif lower_byte_cnt == 4 and higher_byte_cnt == 3:
        return 0b01
    elif lower_byte_cnt == 4 and higher_byte_cnt == 4:
        return 0b11
    else:
        raise Exception("byte count == 0, 1 or 2")


def test_decode_overlapped_byte() -> int:
    assert decode_overlapped_byte(0b01111110) == 0b00
    assert decode_overlapped_byte(0b11010111) == 0b00
    assert decode_overlapped_byte(0b11101111) == 0b01
    assert decode_overlapped_byte(0b01111111) == 0b01
    assert decode_overlapped_byte(0b11111011) == 0b10
    assert decode_overlapped_byte(0b11111110) == 0b10
    assert decode_overlapped_byte(0b11111111) == 0b11

    with pytest.raises(Exception):
        decode_share_byte(0b11110000)
    with pytest.raises(Exception):
        decode_share_byte(0b11110001)
    with pytest.raises(Exception):
        decode_share_byte(0b11110011)
    with pytest.raises(Exception):
        decode_share_byte(0b00000111)
    with pytest.raises(Exception):
        decode_share_byte(0b01001111)


def decode(share: bytes, method: Callable[[int], int], length: int = 50) -> bytes:
    decoded = bytearray(length)
    for i in range(length):
        for j in range(4):
            decoded[i] |= method(share[i * 4 + j]) << 2 * j
    return bytes(decoded)


def test_byte():
    assert 0b11100101101111100111010110011101.to_bytes(4, "big") == b"\xe5\xbeu\x9d"
    assert 0b11100101101111100111010110011101.to_bytes(4, "big")[0] == int.from_bytes(
        b"\xe5", "big"
    )


def test_decode():
    assert decode(
        0b11100101101111100111010110011101.to_bytes(4, "big"), decode_share_byte, 1
    ) == 0b01101110.to_bytes(1, "big")


def overlap(door_share: bytes, user_share: bytes, length: int = 200) -> bytes:
    res = bytearray(length)
    for i in range(length):
        res[i] = door_share[i] | user_share[i]
    return bytes(res)


def test_overlap():
    assert overlap(
        0b01010101.to_bytes(1, "big"),
        0b10101010.to_bytes(1, "big"),
        1,
    ) == 0b11111111.to_bytes(1, "big")
    assert overlap(
        0b11111111.to_bytes(1, "big"),
        0b10101010.to_bytes(1, "big"),
        1,
    ) == 0b11111111.to_bytes(1, "big")
    assert overlap(
        0b10101011.to_bytes(1, "big"),
        0b11001010.to_bytes(1, "big"),
        1,
    ) == 0b11101011.to_bytes(1, "big")
    assert overlap(
        0b1010101110111000.to_bytes(2, "big"),
        0b1100101001111010.to_bytes(2, "big"),
        2,
    ) == 0b1110101111111010.to_bytes(2, "big")


def test_all():
    def case(user_name, door_name, length=50):
        secret = create_secret(length)
        door_share = create_door_share(door_name, length)
        user_share = create_user_share(user_name, secret, door_share, length)
        decoded_door_share = decode(door_share, decode_share_byte, length)
        assert get_share_name(decoded_door_share) == door_name
        decoded_user_share = decode(user_share, decode_share_byte, length)
        assert get_share_name(decoded_user_share) == user_name
        overlapped = overlap(door_share, user_share, length * 4)
        decoded = decode(overlapped, decode_overlapped_byte, length)
        assert decoded == secret

    case(user_name="123", door_name="abc", length=4)
    case(user_name="王景誠", door_name="大門", length=20)
    case(user_name="王景誠", door_name="大門")


def bytes_to_str(bs: bytes) -> str:
    """
    helper function
    我自己用來byte to string的工具，byte是怎麼排列的要自己調整。
    """
    res = ""
    for b in bs:
        res += f"{b:0>8b} "
    return res


def test_bytes_to_str():
    assert bytes_to_str(0b01011010.to_bytes(1, "big")) == "01011010 "
    assert bytes_to_str(0b0101101011100001.to_bytes(2, "big")) == "01011010 11100001 "


def get_share_name(share: bytes) -> str:
    idx = share.find(0)
    return (share[:idx] if idx != -1 else share).decode()


def test_get_share_name():
    assert get_share_name(b"123") == "123"
    assert get_share_name(b"123\x00") == "123"


def encode_base64_str(bs: bytes) -> str:
    return base64.b64encode(bs).decode()
