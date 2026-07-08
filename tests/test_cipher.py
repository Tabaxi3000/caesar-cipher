"""
test_cipher.py

Tests for CaesarCipher covering encryption, decryption, and brute-force cracking

Tests:
  encrypt/decrypt correctness for upper, lower, and mixed case
  non-letter preservation (spaces, punctuation, numbers)
  encrypt/decrypt roundtrip fidelity
  key validation and edge cases (zero key, negative key, alphabet wrapping)
  crack() generating all 26 shifts and locating the correct one

Connects to:
  cipher.py - the class under test
"""

import pytest

from caesar_cipher.cipher import CaesarCipher


class TestCaesarCipher:
    def test_encrypt_basic(self) -> None:
        """
        Encrypts uppercase text with key 3 and checks the shifted output
        """
        cipher = CaesarCipher(key = 3)
        assert cipher.encrypt("HELLO") == "KHOOR"

    def test_encrypt_lowercase(self) -> None:
        """
        Encrypts lowercase text and confirms lowercase output is preserved
        """
        cipher = CaesarCipher(key = 3)
        assert cipher.encrypt("hello") == "khoor"

    def test_encrypt_mixed_case(self) -> None:
        """
        Encrypts mixed-case text and confirms upper and lower shift independently
        """
        cipher = CaesarCipher(key = 3)
        assert cipher.encrypt("Hello World") == "Khoor Zruog"

    def test_encrypt_preserves_spaces(self) -> None:
        """
        Confirms spaces pass through encryption without being shifted
        """
        cipher = CaesarCipher(key = 5)
        assert cipher.encrypt("ABC XYZ") == "FGH CDE"

    def test_encrypt_preserves_punctuation(self) -> None:
        """
        Confirms commas and exclamation marks pass through encryption unchanged
        """
        cipher = CaesarCipher(key = 3)
        assert cipher.encrypt("Hello, World!") == "Khoor, Zruog!"

    def test_encrypt_preserves_numbers(self) -> None:
        """
        Confirms digits pass through encryption unchanged
        """
        cipher = CaesarCipher(key = 3)
        assert cipher.encrypt("Test123") == "Whvw123"

    def test_decrypt_basic(self) -> None:
        """
        Decrypts uppercase ciphertext back to plaintext using the matching key
        """
        cipher = CaesarCipher(key = 3)
        assert cipher.decrypt("KHOOR") == "HELLO"

    def test_decrypt_lowercase(self) -> None:
        """
        Decrypts lowercase ciphertext and confirms case is preserved in output
        """
        cipher = CaesarCipher(key = 3)
        assert cipher.decrypt("khoor") == "hello"

    def test_encrypt_decrypt_roundtrip(self) -> None:
        """
        Encrypts then decrypts a full sentence and asserts the result matches the original
        """
        cipher = CaesarCipher(key = 13)
        original = "The Quick Brown Fox Jumps Over The Lazy Dog!"
        encrypted = cipher.encrypt(original)
        decrypted = cipher.decrypt(encrypted)
        assert decrypted == original

    def test_key_wrapping(self) -> None:
        """
        Confirms key 26 is equivalent to key 0 and produces no shift
        """
        cipher = CaesarCipher(key = 26)
        assert cipher.encrypt("ABC") == "ABC"

    def test_negative_key(self) -> None:
        """
        Confirms a negative key shifts letters backward through the alphabet
        """
        cipher = CaesarCipher(key = -3)
        assert cipher.encrypt("HELLO") == "EBIIL"

    def test_zero_key(self) -> None:
        """
        Confirms key 0 leaves the plaintext completely unchanged
        """
        cipher = CaesarCipher(key = 0)
        assert cipher.encrypt("HELLO") == "HELLO"

    def test_key_validation_too_large(self) -> None:
        """
        Confirms keys above 26 raise ValueError with the expected message
        """
        with pytest.raises(ValueError, match = "Key must be between -25 and 26"):
            CaesarCipher(key = 30)

    def test_key_validation_too_small(self) -> None:
        """
        Confirms keys below -25 raise ValueError with the expected message
        """
        with pytest.raises(ValueError, match = "Key must be between -25 and 26"):
            CaesarCipher(key = -30)

    def test_crack_returns_all_shifts(self) -> None:
        """
        Confirms crack() produces exactly 26 candidate decryptions
        """
        results = CaesarCipher.crack("KHOOR")
        assert len(results) == 26

    def test_crack_finds_correct_shift(self) -> None:
        """
        Confirms the known shift key appears in crack() output with the correct plaintext
        """
        cipher = CaesarCipher(key = 3)
        encrypted = cipher.encrypt("HELLO")
        results = CaesarCipher.crack(encrypted)
        shifts_dict = dict(results)
        assert shifts_dict[3] == "HELLO"

    def test_empty_string(self) -> None:
        """
        Confirms empty string input returns empty string for both encrypt and decrypt
        """
        cipher = CaesarCipher(key = 3)
        assert cipher.encrypt("") == ""
        assert cipher.decrypt("") == ""

    def test_alphabet_wraparound_uppercase(self) -> None:
        """
        Confirms XYZ wraps around to ABC when shifted forward by 3
        """
        cipher = CaesarCipher(key = 3)
        assert cipher.encrypt("XYZ") == "ABC"

    def test_alphabet_wraparound_lowercase(self) -> None:
        """
        Confirms xyz wraps around to abc when shifted forward by 3
        """
        cipher = CaesarCipher(key = 3)
        assert cipher.encrypt("xyz") == "abc"


class TestProgressiveShift:
    def test_progressive_increments_shift(self) -> None:
        """
        Confirms AAA with key 1 becomes BCD as the shift grows by position
        """
        cipher = CaesarCipher(key = 1)
        assert cipher.encrypt_progressive("AAA") == "BCD"

    def test_progressive_zero_key_is_position(self) -> None:
        """
        Confirms AAAA with key 0 shifts purely by position (0,1,2,3)
        """
        cipher = CaesarCipher(key = 0)
        assert cipher.encrypt_progressive("AAAA") == "ABCD"

    def test_progressive_roundtrip(self) -> None:
        """
        Confirms progressive encryption reverses cleanly, including punctuation
        """
        cipher = CaesarCipher(key = 5)
        original = "Attack at dawn, now!"
        encrypted = cipher.encrypt_progressive(original)
        assert cipher.decrypt_progressive(encrypted) == original

    def test_progressive_differs_from_plain(self) -> None:
        """
        Confirms the progressive variant differs from the fixed-shift cipher
        """
        cipher = CaesarCipher(key = 3)
        assert cipher.encrypt_progressive("HELLO") != cipher.encrypt("HELLO")

    def test_progressive_non_letters_do_not_advance(self) -> None:
        """
        Confirms spaces do not advance the position counter (A_A_A stays aligned)
        """
        cipher = CaesarCipher(key = 0)
        # positions 0,1,2 land on the three letters despite the spaces
        assert cipher.encrypt_progressive("A A A") == "A B C"


class TestCustomAlphabet:
    def test_reverse_alphabet_roundtrip(self) -> None:
        """
        Confirms encrypt then decrypt with a reversed alphabet recovers the text
        """
        cipher = CaesarCipher(key = 1, alphabet = "ZYXWVUTSRQPONMLKJIHGFEDCBA")
        assert cipher.decrypt(cipher.encrypt("HELLO")) == "HELLO"

    def test_reverse_alphabet_changes_output(self) -> None:
        """
        Confirms a custom alphabet produces different ciphertext than the default
        """
        custom = CaesarCipher(key = 1, alphabet = "ZYXWVUTSRQPONMLKJIHGFEDCBA")
        assert custom.encrypt("HELLO") != CaesarCipher(key = 1).encrypt("HELLO")

    def test_custom_alphabet_preserves_case(self) -> None:
        """
        Confirms a lowercase letter stays lowercase under a custom alphabet
        """
        cipher = CaesarCipher(key = 2, alphabet = "QWERTYUIOPASDFGHJKLZXCVBNM")
        result = cipher.encrypt("Hi")
        assert result[0].isupper()
        assert result[1].islower()

    def test_custom_alphabet_lowercase_input_accepted(self) -> None:
        """
        Confirms a lowercase custom alphabet is normalized and still usable
        """
        cipher = CaesarCipher(key = 1, alphabet = "zyxwvutsrqponmlkjihgfedcba")
        assert cipher.decrypt(cipher.encrypt("test")) == "test"

    def test_wrong_length_alphabet_raises(self) -> None:
        """
        Confirms an alphabet without exactly 26 characters is rejected
        """
        with pytest.raises(ValueError, match = "exactly 26"):
            CaesarCipher(key = 1, alphabet = "ABC")

    def test_duplicate_alphabet_raises(self) -> None:
        """
        Confirms an alphabet with duplicate letters is rejected
        """
        with pytest.raises(ValueError, match = "duplicate"):
            CaesarCipher(key = 1, alphabet = "A" * 26)

    def test_non_letter_alphabet_raises(self) -> None:
        """
        Confirms an alphabet containing a non-letter is rejected
        """
        with pytest.raises(ValueError, match = "only letters"):
            CaesarCipher(key = 1, alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXY1")
