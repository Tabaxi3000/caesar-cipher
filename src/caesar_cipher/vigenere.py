"""
vigenere.py

Vigenere polyalphabetic cipher with Kasiski and index-of-coincidence cracking

Implements the Vigenere cipher, where a repeating keyword selects a
different Caesar shift for each position, plus the cryptanalysis needed
to break it without the key: the index of coincidence, Kasiski
examination for candidate key lengths, and a full crack that recovers
the key by running frequency analysis on each key-length column
(Challenge 7).

Key exports:
  VigenereCipher - encrypt/decrypt with a keyword
  index_of_coincidence() - Statistical measure of letter clustering
  find_repeated_sequences() - Repeated substrings and their positions (Kasiski)
  kasiski_examination() - Candidate key lengths from repeated-sequence spacings
  guess_key_length() - Best key length by average per-column IC
  crack_vigenere() - Recovers the key and plaintext from ciphertext alone
  VigenereCrackResult - Frozen result of a crack

Connects to:
  constants.py - imports ALPHABET_SIZE, Language
  cipher.py - reuses CaesarCipher to decrypt each column during cracking
  analyzer.py - uses FrequencyAnalyzer to score column decryptions
  main.py - vigenere CLI commands
"""

from collections import Counter
from dataclasses import dataclass
from itertools import combinations

from caesar_cipher.analyzer import FrequencyAnalyzer
from caesar_cipher.cipher import CaesarCipher
from caesar_cipher.constants import ALPHABET_SIZE, Language

# Index of coincidence of natural English; random text sits near 1/26 = 0.0385.
ENGLISH_IC = 0.0667
RANDOM_IC = 0.0385

# A per-column IC above this midpoint between random and English signals that a
# candidate key length lines the ciphertext up into single-shift columns.
IC_ELEVATED_THRESHOLD = (ENGLISH_IC + RANDOM_IC) / 2


@dataclass(frozen = True, slots = True)
class VigenereCrackResult:
    key: str
    key_length: int
    plaintext: str
    index_of_coincidence: float


class VigenereCipher:
    """
    Vigenere cipher using a repeating alphabetic keyword
    """
    def __init__(self, keyword: str) -> None:
        """
        Initialize with a keyword; each letter becomes a Caesar shift
        """
        normalized = keyword.upper()
        if not normalized or not normalized.isalpha():
            msg = "Keyword must be a non-empty string of letters"
            raise ValueError(msg)
        self.keyword = normalized
        self.shifts = [ord(char) - ord("A") for char in normalized]

    def _transform(self, text: str, sign: int) -> str:
        """
        Encrypt (sign=1) or decrypt (sign=-1); non-letters do not advance the key
        """
        result: list[str] = []
        key_index = 0
        for char in text:
            if char.isalpha():
                base = ord("A") if char.isupper() else ord("a")
                shift = self.shifts[key_index % len(self.shifts)]
                offset = (ord(char) - base + sign * shift) % ALPHABET_SIZE
                result.append(chr(base + offset))
                key_index += 1
            else:
                result.append(char)
        return "".join(result)

    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt plaintext with the repeating keyword
        """
        return self._transform(plaintext, 1)

    def decrypt(self, ciphertext: str) -> str:
        """
        Decrypt ciphertext with the repeating keyword
        """
        return self._transform(ciphertext, -1)


def _letters_only(text: str) -> str:
    """
    Return uppercase letters of text with everything else removed
    """
    return "".join(char for char in text.upper() if char.isalpha())


def index_of_coincidence(text: str) -> float:
    """
    Compute the index of coincidence: probability two random letters match
    """
    letters = _letters_only(text)
    n = len(letters)
    if n < 2:
        return 0.0
    counts = Counter(letters)
    return sum(count * (count - 1) for count in counts.values()) / (n * (n - 1))


def find_repeated_sequences(
    text: str,
    seq_len: int = 3,
) -> dict[str, list[int]]:
    """
    Find substrings of length seq_len that occur more than once, with positions
    """
    letters = _letters_only(text)
    positions: dict[str, list[int]] = {}
    for i in range(len(letters) - seq_len + 1):
        seq = letters[i: i + seq_len]
        positions.setdefault(seq, []).append(i)
    return {seq: pos for seq, pos in positions.items() if len(pos) > 1}


def kasiski_examination(
    text: str,
    seq_len: int = 3,
    max_key_length: int = 20,
) -> list[int]:
    """
    Suggest key lengths from the spacings between repeated sequences

    Returns candidate key lengths ordered by how many repeated-sequence
    spacings they divide (most likely first).
    """
    repeats = find_repeated_sequences(text, seq_len)
    factor_votes: Counter[int] = Counter()
    for occurrences in repeats.values():
        for earlier, later in combinations(occurrences, 2):
            spacing = later - earlier
            for factor in range(2, min(max_key_length, spacing) + 1):
                if spacing % factor == 0:
                    factor_votes[factor] += 1
    return [factor for factor, _ in factor_votes.most_common()]


def average_ic_for_length(text: str, key_length: int) -> float:
    """
    Average the index of coincidence across the columns for a given key length
    """
    letters = _letters_only(text)
    if key_length < 1 or key_length > len(letters):
        return 0.0
    ics = [
        index_of_coincidence(letters[start:: key_length])
        for start in range(key_length)
    ]
    return sum(ics) / len(ics)


def guess_key_length(text: str, max_key_length: int = 20) -> int:
    """
    Guess the key length as the shortest whose columns look like real language

    The correct key length AND its multiples push each column's IC toward the
    language IC (~0.0667); wrong lengths sit near random (~0.0385). Because a
    multiple of the true length also scores high, taking the shortest length
    whose average column IC clears the elevated threshold recovers the true key
    length rather than a multiple of it.
    """
    letters = _letters_only(text)
    if len(letters) < 2:
        return 1

    ics = {
        length: average_ic_for_length(text, length)
        for length in range(1, min(max_key_length, len(letters)) + 1)
    }
    for length in sorted(ics):
        if ics[length] >= IC_ELEVATED_THRESHOLD:
            return length
    return max(ics, key = lambda length: ics[length])


def _best_shift_for_column(
    column: str,
    analyzer: FrequencyAnalyzer,
) -> int:
    """
    Find the Caesar shift that makes a single column score most like the language
    """
    return min(
        range(ALPHABET_SIZE),
        key = lambda shift: analyzer.score_text(
            CaesarCipher(key = shift).decrypt(column)
        ),
    )


def crack_vigenere(
    ciphertext: str,
    max_key_length: int = 20,
    language: Language = Language.ENGLISH,
) -> VigenereCrackResult:
    """
    Recover the Vigenere key and plaintext from ciphertext alone
    """
    analyzer = FrequencyAnalyzer(language)
    key_length = guess_key_length(ciphertext, max_key_length)
    letters = _letters_only(ciphertext)

    key_chars: list[str] = []
    for start in range(key_length):
        column = letters[start:: key_length]
        shift = _best_shift_for_column(column, analyzer)
        key_chars.append(chr(shift + ord("A")))

    key = "".join(key_chars)
    plaintext = VigenereCipher(key).decrypt(ciphertext)
    return VigenereCrackResult(
        key = key,
        key_length = key_length,
        plaintext = plaintext,
        index_of_coincidence = index_of_coincidence(ciphertext),
    )
