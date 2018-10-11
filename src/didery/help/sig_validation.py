from typing import Tuple


def int_to_big_endian(value: int) -> bytes:
    return value.to_bytes((value.bit_length() + 7) // 8 or 1, "big")


def big_endian_to_int(value: bytes) -> int:
    return int.from_bytes(value, "big")


def pad32(value: bytes) -> bytes:
    return value.rjust(32, b'\x00')


def decode_public_key(public_key_bytes: bytes) -> Tuple[int, int]:
    left = big_endian_to_int(public_key_bytes[0:32])
    right = big_endian_to_int(public_key_bytes[32:64])
    return left, right


def encode_raw_public_key(raw_public_key: Tuple[int, int]) -> bytes:
    left, right = raw_public_key
    return b''.join((
        pad32(int_to_big_endian(left)),
        pad32(int_to_big_endian(right)),
    ))
