"""
constants.py

Shared constants for the Caesar cipher: alphabet definitions and multi-language letter frequency data

Defines the letter sets used by the cipher for case-aware shifting,
the expected frequency percentages for each letter in several languages
(used by frequency analysis to score decryption candidates), an accent
normalization map so accented input folds onto the 26-letter alphabet,
and the chi-squared threshold for filtering results.

Connects to:
  cipher.py - imports UPPERCASE_LETTERS, LOWERCASE_LETTERS, ALPHABET_SIZE
  analyzer.py - imports LANGUAGE_FREQUENCIES, ACCENT_MAP, Language
  vigenere.py - imports ALPHABET_SIZE, UPPERCASE_LETTERS
  main.py - imports Language for the --language option
"""

import string
from enum import StrEnum
from typing import Final


UPPERCASE_LETTERS: Final[str] = string.ascii_uppercase
LOWERCASE_LETTERS: Final[str] = string.ascii_lowercase
ALL_LETTERS: Final[str] = UPPERCASE_LETTERS + LOWERCASE_LETTERS

ALPHABET_SIZE: Final[int] = 26


class Language(StrEnum):
    ENGLISH = "english"
    SPANISH = "spanish"
    FRENCH = "french"
    GERMAN = "german"

ENGLISH_LETTER_FREQUENCIES: Final[dict[str,
                                       float]] = {
                                           "E": 12.70,
                                           "T": 9.06,
                                           "A": 8.17,
                                           "O": 7.51,
                                           "I": 6.97,
                                           "N": 6.75,
                                           "S": 6.33,
                                           "H": 6.09,
                                           "R": 5.99,
                                           "D": 4.25,
                                           "L": 4.03,
                                           "C": 2.78,
                                           "U": 2.76,
                                           "M": 2.41,
                                           "W": 2.36,
                                           "F": 2.23,
                                           "G": 2.02,
                                           "Y": 1.97,
                                           "P": 1.93,
                                           "B": 1.29,
                                           "V": 0.98,
                                           "K": 0.77,
                                           "J": 0.15,
                                           "X": 0.15,
                                           "Q": 0.10,
                                           "Z": 0.07,
                                       }

# Spanish letter frequencies (%). Accented vowels and Ñ are folded onto their
# base letters, so the table stays over the 26-letter A-Z alphabet.
SPANISH_LETTER_FREQUENCIES: Final[dict[str, float]] = {
    "A": 11.53, "B": 2.22, "C": 4.02, "D": 5.01, "E": 12.18, "F": 0.69,
    "G": 1.77, "H": 0.70, "I": 6.25, "J": 0.44, "K": 0.02, "L": 4.97,
    "M": 3.15, "N": 7.02, "O": 8.68, "P": 2.51, "Q": 0.88, "R": 6.87,
    "S": 7.98, "T": 4.63, "U": 2.93, "V": 0.90, "W": 0.02, "X": 0.22,
    "Y": 0.90, "Z": 0.52,
}

# French letter frequencies (%), accents folded onto base letters.
FRENCH_LETTER_FREQUENCIES: Final[dict[str, float]] = {
    "A": 7.64, "B": 0.90, "C": 3.26, "D": 3.67, "E": 14.72, "F": 1.07,
    "G": 0.87, "H": 0.74, "I": 7.53, "J": 0.55, "K": 0.05, "L": 5.46,
    "M": 2.97, "N": 7.10, "O": 5.80, "P": 2.52, "Q": 1.36, "R": 6.69,
    "S": 7.95, "T": 7.24, "U": 6.31, "V": 1.84, "W": 0.04, "X": 0.43,
    "Y": 0.13, "Z": 0.33,
}

# German letter frequencies (%), umlauts and ß folded onto base letters.
GERMAN_LETTER_FREQUENCIES: Final[dict[str, float]] = {
    "A": 6.51, "B": 1.89, "C": 3.06, "D": 5.08, "E": 17.40, "F": 1.66,
    "G": 3.01, "H": 4.76, "I": 7.55, "J": 0.27, "K": 1.21, "L": 3.44,
    "M": 2.53, "N": 9.78, "O": 2.51, "P": 0.79, "Q": 0.02, "R": 7.00,
    "S": 7.27, "T": 6.15, "U": 4.35, "V": 0.67, "W": 1.89, "X": 0.03,
    "Y": 0.04, "Z": 1.13,
}

LANGUAGE_FREQUENCIES: Final[dict[Language, dict[str, float]]] = {
    Language.ENGLISH: ENGLISH_LETTER_FREQUENCIES,
    Language.SPANISH: SPANISH_LETTER_FREQUENCIES,
    Language.FRENCH: FRENCH_LETTER_FREQUENCIES,
    Language.GERMAN: GERMAN_LETTER_FREQUENCIES,
}

# Maps accented characters onto their base A-Z letter so that multi-language
# input can be scored against the 26-letter frequency tables. 'ß' folds to 'S'.
ACCENT_MAP: Final[dict[str, str]] = {
    "Á": "A", "À": "A", "Â": "A", "Ä": "A", "Ã": "A", "Å": "A",
    "É": "E", "È": "E", "Ê": "E", "Ë": "E",
    "Í": "I", "Ì": "I", "Î": "I", "Ï": "I",
    "Ó": "O", "Ò": "O", "Ô": "O", "Ö": "O", "Õ": "O",
    "Ú": "U", "Ù": "U", "Û": "U", "Ü": "U",
    "Ñ": "N", "Ç": "C", "Ý": "Y", "ß": "S",
}

CHI_SQUARED_THRESHOLD: Final[float] = 50.0
