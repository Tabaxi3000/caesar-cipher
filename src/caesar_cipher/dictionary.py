"""
dictionary.py

Dictionary-based scoring to complement frequency analysis (Challenge 5)

Loads a word list into a set for O(1) membership checks, computes what
fraction of a text's tokens are real words, and combines that with the
chi-squared frequency score to rank brute-force candidates. Dictionary
checking is more robust than frequency alone on short messages. The word
list comes from the system dictionary when available, otherwise a bundled
set of common English words so the feature works offline.

Key exports:
  load_words() - Loads and caches a word set from a path or the system dict
  word_match_ratio() - Fraction of tokens found in the word set
  rank_candidates_combined() - Ranks candidates by weighted dict + frequency score

Connects to:
  analyzer.py - uses FrequencyAnalyzer for the frequency component
  main.py - crack command uses rank_candidates_combined when --dictionary is set
"""

import re
from functools import lru_cache
from pathlib import Path

from caesar_cipher.analyzer import FrequencyAnalyzer

_SYSTEM_WORD_LIST = Path("/usr/share/dict/words")

_TOKEN_PATTERN = re.compile(r"[a-z]+")

# Bundled fallback so dictionary ranking works with no system word list and no
# network access. Deliberately small but covers very common English words.
_FALLBACK_WORDS: frozenset[str] = frozenset({
    "a", "about", "all", "an", "and", "are", "as", "at", "attack", "back",
    "be", "been", "before", "big", "both", "brown", "but", "by", "call",
    "can", "come", "could", "dawn", "day", "do", "does", "dog", "down",
    "each", "find", "first", "for", "fox", "from", "get", "go", "good",
    "great", "had", "has", "have", "he", "hello", "her", "here", "him",
    "his", "how", "i", "if", "in", "into", "is", "it", "its", "jumps",
    "just", "keep", "know", "last", "lazy", "like", "little", "long",
    "look", "made", "make", "man", "many", "may", "me", "meet", "message",
    "more", "most", "my", "new", "no", "not", "now", "of", "off", "old",
    "on", "one", "only", "or", "other", "our", "out", "over", "own",
    "people", "quick", "run", "said", "same", "secret", "see", "she",
    "should", "so", "some", "strike", "such", "take", "than", "that",
    "the", "their", "them", "then", "there", "these", "they", "thing",
    "this", "those", "time", "to", "today", "too", "two", "under", "up",
    "us", "use", "very", "was", "way", "we", "well", "went", "were",
    "what", "when", "where", "which", "who", "will", "with", "word",
    "work", "world", "would", "year", "you", "your",
})


@lru_cache(maxsize = 4)
def load_words(path: Path | None = None) -> frozenset[str]:
    """
    Load a lowercase word set from a file, the system dictionary, or the fallback
    """
    source = path or _SYSTEM_WORD_LIST
    try:
        contents = source.read_text(encoding = "utf-8", errors = "ignore")
    except OSError:
        return _FALLBACK_WORDS

    words = {
        line.strip().lower()
        for line in contents.splitlines()
        if line.strip().isalpha()
    }
    return frozenset(words) if words else _FALLBACK_WORDS


def tokenize(text: str) -> list[str]:
    """
    Split text into lowercase alphabetic word tokens
    """
    return _TOKEN_PATTERN.findall(text.lower())


def word_match_ratio(text: str, words: frozenset[str]) -> float:
    """
    Return the fraction of word tokens that appear in the word set
    """
    tokens = tokenize(text)
    if not tokens:
        return 0.0
    matches = sum(1 for token in tokens if token in words)
    return matches / len(tokens)


def rank_candidates_combined(
    candidates: list[tuple[int, str]],
    analyzer: FrequencyAnalyzer,
    words: frozenset[str],
    *,
    dict_weight: float = 0.7,
    freq_weight: float = 0.3,
) -> list[tuple[int, str, float]]:
    """
    Rank candidates by a weighted blend of dictionary matches and frequency fit

    The returned score is in [0, 1] where higher is better, the opposite of the
    raw chi-squared score. Frequency scores are min-max normalized across the
    candidate set so the two components share a comparable scale.
    """
    if not candidates:
        return []

    chi_scores = [analyzer.score_text(text) for _, text in candidates]
    finite = [score for score in chi_scores if score != float("inf")]
    chi_min = min(finite) if finite else 0.0
    chi_max = max(finite) if finite else 0.0
    chi_range = chi_max - chi_min

    ranked: list[tuple[int, str, float]] = []
    for (shift, text), chi in zip(candidates, chi_scores, strict = True):
        dict_ratio = word_match_ratio(text, words)
        if chi == float("inf") or chi_range == 0:
            freq_goodness = 0.0 if chi == float("inf") else 1.0
        else:
            freq_goodness = (chi_max - chi) / chi_range
        combined = dict_weight * dict_ratio + freq_weight * freq_goodness
        ranked.append((shift, text, combined))

    return sorted(ranked, key = lambda item: item[2], reverse = True)
