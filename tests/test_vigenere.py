"""
test_vigenere.py

Tests for the Vigenere cipher and its cryptanalysis

Tests:
  VigenereCipher known-answer encryption and decryption roundtrip
  non-letters preserved and do not advance the key
  keyword validation rejects empty and non-alphabetic keywords
  index of coincidence separates English text from random text
  repeated-sequence detection and Kasiski key-length hints
  guess_key_length recovers the true length (not a multiple)
  crack_vigenere recovers key and plaintext from ciphertext alone

Connects to:
  vigenere.py - the module under test
"""

import pytest

from caesar_cipher.vigenere import (
    VigenereCipher,
    crack_vigenere,
    find_repeated_sequences,
    guess_key_length,
    index_of_coincidence,
    kasiski_examination,
)

# A passage long enough (~300 letters) for reliable Vigenere cryptanalysis.
LONG_PLAINTEXT = (
    "The index of coincidence is a statistic used in classical cryptography "
    "to break the vigenere cipher by first determining the length of the keyword "
    "and then applying frequency analysis to each column of the ciphertext letters "
    "because each column was enciphered with the same caesar shift the distribution "
    "of letters within a column mirrors ordinary english text quite closely"
)


class TestVigenereCipher:
    def test_known_answer(self) -> None:
        """
        Confirms ATTACKATDAWN with key LEMON gives the classic LXFOPVEFRNHR
        """
        assert VigenereCipher("LEMON").encrypt("ATTACKATDAWN") == "LXFOPVEFRNHR"

    def test_decrypt_known_answer(self) -> None:
        """
        Confirms LXFOPVEFRNHR with key LEMON decrypts back to ATTACKATDAWN
        """
        assert VigenereCipher("LEMON").decrypt("LXFOPVEFRNHR") == "ATTACKATDAWN"

    def test_roundtrip_with_punctuation(self) -> None:
        """
        Confirms a mixed-case sentence with punctuation round-trips exactly
        """
        cipher = VigenereCipher("SECRET")
        original = "Meet me at Dawn, by the old Bridge!"
        assert cipher.decrypt(cipher.encrypt(original)) == original

    def test_non_letters_do_not_advance_key(self) -> None:
        """
        Confirms spaces are preserved and do not consume a key letter
        """
        cipher = VigenereCipher("AB")
        # key A=0, B=1; spaces skip so the pattern stays 0,1,0,1 across letters
        assert cipher.encrypt("AA AA") == "AB AB"

    def test_empty_keyword_raises(self) -> None:
        """
        Confirms an empty keyword is rejected
        """
        with pytest.raises(ValueError, match = "non-empty"):
            VigenereCipher("")

    def test_non_alpha_keyword_raises(self) -> None:
        """
        Confirms a keyword containing non-letters is rejected
        """
        with pytest.raises(ValueError, match = "letters"):
            VigenereCipher("KEY123")


class TestIndexOfCoincidence:
    def test_english_higher_than_random(self) -> None:
        """
        Confirms English text has a higher IC than uniformly cycled letters
        """
        english_ic = index_of_coincidence(LONG_PLAINTEXT)
        random_ic = index_of_coincidence("ABCDEFGHIJKLMNOPQRSTUVWXYZ" * 5)
        assert english_ic > random_ic

    def test_english_in_expected_range(self) -> None:
        """
        Confirms English IC sits near the expected 0.066 value
        """
        assert 0.055 < index_of_coincidence(LONG_PLAINTEXT) < 0.075

    def test_short_text_returns_zero(self) -> None:
        """
        Confirms a single letter cannot form a coincidence and scores 0
        """
        assert index_of_coincidence("A") == 0.0


class TestKasiski:
    def test_finds_repeated_sequences(self) -> None:
        """
        Confirms a repeated trigram is detected with both of its positions
        """
        repeats = find_repeated_sequences("ABCXXABC", seq_len = 3)
        assert "ABC" in repeats
        assert len(repeats["ABC"]) == 2

    def test_kasiski_suggests_key_length(self) -> None:
        """
        Confirms Kasiski examination lists the true key length among its hints
        """
        ciphertext = VigenereCipher("LEMON").encrypt(LONG_PLAINTEXT)
        hints = kasiski_examination(ciphertext, max_key_length = 12)
        assert 5 in hints


class TestKeyLengthAndCrack:
    def test_guess_key_length(self) -> None:
        """
        Confirms the true key length is recovered rather than a multiple of it
        """
        ciphertext = VigenereCipher("LEMON").encrypt(LONG_PLAINTEXT)
        assert guess_key_length(ciphertext, max_key_length = 12) == 5

    def test_guess_key_length_pure_caesar(self) -> None:
        """
        Confirms a single-letter key (pure Caesar) is detected as length 1
        """
        ciphertext = VigenereCipher("D").encrypt(LONG_PLAINTEXT)
        assert guess_key_length(ciphertext, max_key_length = 12) == 1

    def test_crack_recovers_key_and_plaintext(self) -> None:
        """
        Confirms cracking recovers the LEMON key and the original plaintext
        """
        ciphertext = VigenereCipher("LEMON").encrypt(LONG_PLAINTEXT)
        result = crack_vigenere(ciphertext, max_key_length = 12)
        assert result.key == "LEMON"
        assert result.key_length == 5
        assert result.plaintext == LONG_PLAINTEXT

    def test_crack_different_keyword(self) -> None:
        """
        Confirms cracking also recovers a six-letter keyword
        """
        ciphertext = VigenereCipher("CRYPTO").encrypt(LONG_PLAINTEXT)
        result = crack_vigenere(ciphertext, max_key_length = 12)
        assert result.key == "CRYPTO"
        assert result.plaintext == LONG_PLAINTEXT
