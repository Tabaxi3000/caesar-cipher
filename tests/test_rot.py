"""
test_rot.py

Tests for ROT13 and ROT47 transforms

Tests:
  rot13 known output and self-inverse property
  rot13 preserves non-letters (digits, punctuation, spaces)
  rot47 self-inverse property and coverage of digits/punctuation
  rot47 known single-character mapping and out-of-range passthrough

Connects to:
  rot.py - the functions under test
"""

from caesar_cipher.rot import rot13, rot47


class TestRot13:
    def test_known_output(self) -> None:
        """
        Confirms HELLO becomes URYYB under ROT13
        """
        assert rot13("HELLO") == "URYYB"

    def test_self_inverse(self) -> None:
        """
        Confirms applying ROT13 twice returns the original text
        """
        text = "The Secret Message! 42"
        assert rot13(rot13(text)) == text

    def test_preserves_non_letters(self) -> None:
        """
        Confirms digits and punctuation pass through ROT13 unchanged
        """
        assert rot13("abc-123!") == "nop-123!"


class TestRot47:
    def test_self_inverse(self) -> None:
        """
        Confirms applying ROT47 twice returns the original text
        """
        text = "Hello, World! 123 @#$%"
        assert rot47(rot47(text)) == text

    def test_shifts_digits_and_punctuation(self) -> None:
        """
        Confirms ROT47 transforms digits and punctuation, not just letters
        """
        rotated = rot47("12345")
        assert rotated != "12345"
        assert all(not c.isdigit() for c in rotated)

    def test_known_mapping(self) -> None:
        """
        Confirms the ROT47 mapping of 'A' (code 65) lands on 'p' (code 112)
        """
        assert rot47("A") == "p"

    def test_space_unchanged(self) -> None:
        """
        Confirms a space (code 32, below the ROT47 range) is left unchanged
        """
        assert rot47("A B") == "p" + " " + rot47("B")
