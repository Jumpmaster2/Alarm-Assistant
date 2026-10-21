"""Alarm code hash."""

from logic.code import hash_code, is_legacy, legacy_hash, valid_code, verify_code


def test_valid_code() -> None:
    assert valid_code("1234")
    assert valid_code("0123456789")
    assert not valid_code("123")
    assert not valid_code("12345678901")
    assert not valid_code("12a4")
    assert not valid_code("")


def test_salted_hash() -> None:
    first = hash_code("1234")
    assert first != hash_code("1234")  # random salt
    assert not is_legacy(first)
    assert verify_code("1234", first)
    assert not verify_code("1235", first)
    assert not verify_code("1234", "pbkdf2_sha256$broken")


def test_legacy_hash() -> None:
    stored = legacy_hash("1234")
    assert is_legacy(stored)
    assert verify_code("1234", stored)
    assert not verify_code("0000", stored)
