"""
test_analyzer.py

Tests for FrequencyAnalyzer covering chi-squared scoring and candidate ranking

Tests:
  chi-squared scoring distinguishes English text from gibberish
  empty string returns infinity
  rank_candidates() orders results by score ascending
  end-to-end crack-and-rank against a known plaintext

Connects to:
  analyzer.py - the class under test
  cipher.py - crack() output used as input to rank_candidates()
"""

import pytest

from caesar_cipher.analyzer import FrequencyAnalyzer
from caesar_cipher.cipher import CaesarCipher
from caesar_cipher.constants import Language


class TestFrequencyAnalyzer:
    def test_calculate_chi_squared_english_text(self) -> None:
        """
        Confirms real English text scores below a reasonable chi-squared threshold
        """
        analyzer = FrequencyAnalyzer()
        english_text = "THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG"
        score = analyzer.calculate_chi_squared(english_text)
        assert score < 150

    def test_calculate_chi_squared_gibberish(self) -> None:
        """
        Confirms text made of rare letters scores above the threshold
        """
        analyzer = FrequencyAnalyzer()
        gibberish = "ZZZZZ QQQQQ XXXXX"
        score = analyzer.calculate_chi_squared(gibberish)
        assert score > 100

    def test_calculate_chi_squared_empty_string(self) -> None:
        """
        Confirms an empty string returns infinity since there are no letters to score
        """
        analyzer = FrequencyAnalyzer()
        assert analyzer.calculate_chi_squared("") == float("inf")

    def test_score_text_lowercase(self) -> None:
        """
        Confirms score_text returns a non-negative float for lowercase input
        """
        analyzer = FrequencyAnalyzer()
        score = analyzer.score_text("hello world")
        assert isinstance(score, float)
        assert score >= 0

    def test_rank_candidates_orders_by_score(self) -> None:
        """
        Confirms candidates are sorted so the most English-like text ranks first
        """
        analyzer = FrequencyAnalyzer()
        candidates = [
            (0,
             "gibberish zzz"),
            (1,
             "the quick brown fox"),
            (2,
             "qqq xxx zzz"),
        ]
        ranked = analyzer.rank_candidates(candidates)

        assert len(ranked) == 3
        assert ranked[0][1] == "the quick brown fox"
        assert ranked[0][2] < ranked[1][2]
        assert ranked[1][2] < ranked[2][2]

    def test_rank_candidates_with_actual_cipher(self) -> None:
        """
        Encrypts known text, brute-forces all shifts, and confirms the correct key ranks first
        """
        cipher = CaesarCipher(key = 3)
        plaintext = "THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG"
        ciphertext = cipher.encrypt(plaintext)

        candidates = CaesarCipher.crack(ciphertext)
        analyzer = FrequencyAnalyzer()
        ranked = analyzer.rank_candidates(candidates)

        best_shift, best_text, _best_score = ranked[0]
        assert best_shift == 3
        assert best_text == plaintext

    def test_rank_candidates_empty_list(self) -> None:
        """
        Confirms an empty candidate list returns an empty ranked list
        """
        analyzer = FrequencyAnalyzer()
        ranked = analyzer.rank_candidates([])
        assert ranked == []


class TestLetterDistribution:
    def test_letter_counts(self) -> None:
        """
        Confirms letter_counts tallies letters and ignores spaces and case
        """
        analyzer = FrequencyAnalyzer()
        counts = analyzer.letter_counts("Hello")
        assert counts["L"] == 2
        assert counts["H"] == 1
        assert sum(counts.values()) == 5

    def test_letter_frequencies_sum_to_100(self) -> None:
        """
        Confirms the returned percentages cover all 26 letters and sum to ~100
        """
        analyzer = FrequencyAnalyzer()
        freqs = analyzer.letter_frequencies("THE QUICK BROWN FOX")
        assert len(freqs) == 26
        assert sum(freqs.values()) == pytest.approx(100.0)

    def test_letter_frequencies_empty(self) -> None:
        """
        Confirms empty text yields a zeroed distribution rather than dividing by zero
        """
        analyzer = FrequencyAnalyzer()
        freqs = analyzer.letter_frequencies("")
        assert set(freqs.values()) == {0.0}

    def test_accented_input_folds_to_base_letter(self) -> None:
        """
        Confirms accented characters are counted against their base A-Z letter
        """
        analyzer = FrequencyAnalyzer()
        counts = analyzer.letter_counts("ÑOÑO")
        assert counts["N"] == 2
        assert counts["O"] == 2


class TestMultiLanguage:
    def test_language_selects_reference_table(self) -> None:
        """
        Confirms selecting a language swaps in its frequency reference table
        """
        english = FrequencyAnalyzer(Language.ENGLISH)
        spanish = FrequencyAnalyzer(Language.SPANISH)
        assert english.reference_frequencies != spanish.reference_frequencies

    def test_spanish_text_scores_better_as_spanish(self) -> None:
        """
        Confirms Spanish text scores lower against the Spanish table than English
        """
        spanish_text = (
            "el rapido zorro marron salta sobre el perro perezoso mientras "
            "la mayoria de las personas duermen en la casa grande"
        )
        english_score = FrequencyAnalyzer(Language.ENGLISH).score_text(spanish_text)
        spanish_score = FrequencyAnalyzer(Language.SPANISH).score_text(spanish_text)
        assert spanish_score < english_score

    def test_default_language_is_english(self) -> None:
        """
        Confirms the analyzer defaults to the English frequency table
        """
        assert FrequencyAnalyzer().language == Language.ENGLISH
