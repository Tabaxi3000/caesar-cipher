"""
test_dictionary.py

Tests for dictionary-based scoring and combined ranking

Tests:
  load_words falls back to a bundled set when a path is missing
  load_words reads a custom word-list file
  word_match_ratio counts recognized words correctly
  rank_candidates_combined recovers the correct shift, including short text

Connects to:
  dictionary.py - the functions under test
  cipher.py - crack() generates candidates for ranking
  analyzer.py - FrequencyAnalyzer supplies the frequency component
"""

from pathlib import Path

from caesar_cipher.analyzer import FrequencyAnalyzer
from caesar_cipher.cipher import CaesarCipher
from caesar_cipher.dictionary import (
    load_words,
    rank_candidates_combined,
    word_match_ratio,
)


class TestLoadWords:
    def test_missing_path_uses_fallback(self) -> None:
        """
        Confirms a nonexistent path falls back to the bundled word set
        """
        words = load_words(Path("/nonexistent/words/file.txt"))
        assert "the" in words
        assert "hello" in words

    def test_custom_word_file(self, tmp_path: Path) -> None:
        """
        Confirms load_words reads and lowercases words from a file
        """
        word_file = tmp_path / "words.txt"
        word_file.write_text("Alpha\nBravo\nCharlie\n")
        words = load_words(word_file)
        assert "alpha" in words
        assert "bravo" in words


class TestWordMatchRatio:
    def test_all_words_recognized(self) -> None:
        """
        Confirms a sentence of known words scores a ratio of 1.0
        """
        words = load_words(Path("/nonexistent"))
        assert word_match_ratio("the quick brown fox", words) == 1.0

    def test_no_words_recognized(self) -> None:
        """
        Confirms gibberish tokens score a ratio of 0.0
        """
        words = load_words(Path("/nonexistent"))
        assert word_match_ratio("xqz vbn plk", words) == 0.0

    def test_empty_text(self) -> None:
        """
        Confirms empty text scores 0.0 without dividing by zero
        """
        words = load_words(Path("/nonexistent"))
        assert word_match_ratio("", words) == 0.0


class TestCombinedRanking:
    def test_recovers_correct_shift(self) -> None:
        """
        Confirms combined ranking puts the correct decryption first
        """
        ciphertext = CaesarCipher(key = 7).encrypt("THE QUICK BROWN FOX JUMPS")
        candidates = CaesarCipher.crack(ciphertext)
        words = load_words(Path("/nonexistent"))
        ranked = rank_candidates_combined(candidates, FrequencyAnalyzer(), words)
        assert ranked[0][1] == "THE QUICK BROWN FOX JUMPS"

    def test_short_text_dictionary_helps(self) -> None:
        """
        Confirms dictionary ranking recovers short text where frequency alone struggles
        """
        ciphertext = CaesarCipher(key = 5).encrypt("HELLO WORLD")
        candidates = CaesarCipher.crack(ciphertext)
        words = load_words(Path("/nonexistent"))
        ranked = rank_candidates_combined(candidates, FrequencyAnalyzer(), words)
        assert ranked[0][1] == "HELLO WORLD"

    def test_scores_are_descending(self) -> None:
        """
        Confirms combined scores come back sorted highest-first
        """
        ciphertext = CaesarCipher(key = 3).encrypt("THE LAZY DOG SLEEPS")
        candidates = CaesarCipher.crack(ciphertext)
        words = load_words(Path("/nonexistent"))
        ranked = rank_candidates_combined(candidates, FrequencyAnalyzer(), words)
        scores = [score for _, _, score in ranked]
        assert scores == sorted(scores, reverse = True)

    def test_empty_candidates(self) -> None:
        """
        Confirms an empty candidate list returns an empty ranking
        """
        words = load_words(Path("/nonexistent"))
        assert rank_candidates_combined([], FrequencyAnalyzer(), words) == []
