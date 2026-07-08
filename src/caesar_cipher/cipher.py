"""
cipher.py

Caesar cipher with encrypt, decrypt, progressive-shift, and brute-force crack

Provides the CaesarCipher class that performs letter shifting for a given
key while preserving case, spaces, and punctuation. A custom 26-letter
alphabet may be supplied to reorder the substitution (Challenge 2). The
progressive variants add a position-dependent shift so the same plaintext
letter encrypts differently by position (Challenge 1). The static crack()
method generates all 26 possible decryptions without needing the key,
leaving ranking to the analyzer layer.

Connects to:
  constants.py - imports UPPERCASE_LETTERS, LOWERCASE_LETTERS, ALPHABET_SIZE
  main.py - all CLI cipher commands instantiate CaesarCipher
  analyzer.py - crack() output is passed to FrequencyAnalyzer for ranking
"""

from caesar_cipher.constants import (
    ALPHABET_SIZE,
    UPPERCASE_LETTERS,
)


class CaesarCipher:
    """
    Caesar cipher implementation with configurable shift key and alphabet support
    """
    def __init__(self, key: int, alphabet: str | None = None) -> None:
        """
        Initialize Caesar cipher with shift key and optional custom alphabet
        """
        if not -25 <= key <= 26:
            msg = "Key must be between -25 and 26"
            raise ValueError(msg)

        self.key = key % ALPHABET_SIZE
        self.alphabet = (
            UPPERCASE_LETTERS if alphabet is None
            else self._validate_alphabet(alphabet)
        )
        self._upper = self.alphabet
        self._lower = self.alphabet.lower()

    @staticmethod
    def _validate_alphabet(alphabet: str) -> str:
        """
        Validate and normalize a custom alphabet to 26 unique uppercase letters
        """
        normalized = alphabet.upper()
        if len(normalized) != ALPHABET_SIZE:
            msg = f"Alphabet must contain exactly {ALPHABET_SIZE} characters"
            raise ValueError(msg)
        if not normalized.isalpha():
            msg = "Alphabet must contain only letters"
            raise ValueError(msg)
        if len(set(normalized)) != len(normalized):
            msg = "Alphabet must not contain duplicate characters"
            raise ValueError(msg)
        return normalized

    def _is_cipher_char(self, char: str) -> bool:
        """
        Return True when a character belongs to the active alphabet
        """
        return char in self._upper or char in self._lower

    def _shift_char(self, char: str, shift: int) -> str:
        """
        Shift a single character by the specified amount while preserving case
        """
        if char in self._upper:
            idx = self._upper.index(char)
            return self._upper[(idx + shift) % ALPHABET_SIZE]
        if char in self._lower:
            idx = self._lower.index(char)
            return self._lower[(idx + shift) % ALPHABET_SIZE]
        return char

    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt plaintext using the configured shift key
        """
        return "".join(self._shift_char(char, self.key) for char in plaintext)

    def decrypt(self, ciphertext: str) -> str:
        """
        Decrypt ciphertext using the configured shift key
        """
        return "".join(self._shift_char(char, -self.key) for char in ciphertext)

    def _shift_progressive(self, text: str, sign: int) -> str:
        """
        Apply a position-dependent shift of (key + position) to each letter

        The position counter advances only for characters in the alphabet, so
        spaces and punctuation do not desynchronize the running shift.
        """
        result: list[str] = []
        position = 0
        for char in text:
            if self._is_cipher_char(char):
                shift = (self.key + position) % ALPHABET_SIZE
                result.append(self._shift_char(char, sign * shift))
                position += 1
            else:
                result.append(char)
        return "".join(result)

    def encrypt_progressive(self, plaintext: str) -> str:
        """
        Encrypt with a position-dependent shift (autokey-style variant)
        """
        return self._shift_progressive(plaintext, 1)

    def decrypt_progressive(self, ciphertext: str) -> str:
        """
        Decrypt text that was encrypted with encrypt_progressive
        """
        return self._shift_progressive(ciphertext, -1)

    @staticmethod
    def crack(ciphertext: str) -> list[tuple[int, str]]:
        """
        Attempt all possible shifts to decrypt ciphertext without knowing the key
        """
        results = []
        for shift in range(ALPHABET_SIZE):
            cipher = CaesarCipher(key = shift)
            decrypted = cipher.decrypt(ciphertext)
            results.append((shift, decrypted))
        return results
