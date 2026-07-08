"""
analyzer.py

Statistical frequency analysis for ranking Caesar cipher brute-force results

Provides the FrequencyAnalyzer class that scores decryption candidates
by comparing their letter distributions against expected letter frequency
percentages using a chi-squared test. Lower scores indicate text that
more closely matches the chosen language. A language may be selected so
the same machinery ranks Spanish, French, or German text (Challenge 6),
and accented input is folded onto the 26-letter alphabet first. The
letter-distribution helpers back the stats command and web view.

Connects to:
  constants.py - imports LANGUAGE_FREQUENCIES, ACCENT_MAP, Language, UPPERCASE_LETTERS
  main.py - crack and stats commands use FrequencyAnalyzer
  web.py - reuses letter_frequencies and rank_candidates
"""

from collections import Counter

from caesar_cipher.constants import (
    ACCENT_MAP,
    LANGUAGE_FREQUENCIES,
    UPPERCASE_LETTERS,
    Language,
)


class FrequencyAnalyzer:
    """
    Analyzes text for language patterns using letter frequency distribution
    """
    def __init__(self, language: Language = Language.ENGLISH) -> None:
        """
        Initialize analyzer with the reference frequency table for a language
        """
        self.language = language
        self.reference_frequencies = LANGUAGE_FREQUENCIES[language]

    @staticmethod
    def _normalize(text: str) -> str:
        """
        Uppercase text and fold accented characters onto their base letters
        """
        return "".join(ACCENT_MAP.get(char, char) for char in text.upper())

    def letter_counts(self, text: str) -> Counter[str]:
        """
        Count occurrences of each A-Z letter after accent normalization
        """
        normalized = self._normalize(text)
        return Counter(char for char in normalized if char in UPPERCASE_LETTERS)

    def letter_frequencies(self, text: str) -> dict[str, float]:
        """
        Return the percentage frequency of every A-Z letter (0.0 when absent)
        """
        counts = self.letter_counts(text)
        total = sum(counts.values())
        if total == 0:
            return dict.fromkeys(UPPERCASE_LETTERS, 0.0)
        return {
            letter: counts.get(letter, 0) / total * 100
            for letter in UPPERCASE_LETTERS
        }

    def calculate_chi_squared(self, text: str) -> float:
        """
        Calculate chi-squared statistic comparing text to expected frequencies
        """
        letter_counts = self.letter_counts(text)

        if not letter_counts:
            return float("inf")

        total_letters = sum(letter_counts.values())
        chi_squared = 0.0

        for letter, expected_freq in self.reference_frequencies.items():
            observed_count = letter_counts.get(letter, 0)
            expected_count = (expected_freq / 100) * total_letters

            if expected_count > 0:
                chi_squared += (
                    (observed_count - expected_count)**2
                ) / expected_count

        return chi_squared

    def score_text(self, text: str) -> float:
        """
        Score text likelihood of matching the language (lower is better)
        """
        return self.calculate_chi_squared(text)

    def rank_candidates(self,
                        candidates: list[tuple[int,
                                               str]]) -> list[tuple[int,
                                                                    str,
                                                                    float]]:
        """
        Rank decryption candidates by their frequency score
        """
        scored = [
            (shift,
             text,
             self.score_text(text)) for shift, text in candidates
        ]
        return sorted(scored, key = lambda x: x[2])
