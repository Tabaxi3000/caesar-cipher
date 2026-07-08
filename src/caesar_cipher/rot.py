"""
rot.py

ROT13 and ROT47 self-inverse transforms (Challenge 4)

ROT13 is the special Caesar case of shift 13: because 13 is half of 26 it
is its own inverse, so a single operation both encodes and decodes. ROT47
extends the idea to the 94 printable ASCII characters (33-126) with a
shift of 47, again its own inverse, covering digits and punctuation as
well as letters.

Key exports:
  rot13() - Apply ROT13 to letters (self-inverse)
  rot47() - Apply ROT47 to printable ASCII (self-inverse)

Connects to:
  cipher.py - rot13 delegates to CaesarCipher(key=13)
  main.py - rot13 and rot47 CLI commands
"""

from caesar_cipher.cipher import CaesarCipher

_ROT47_LOW = 33
_ROT47_HIGH = 126
_ROT47_RANGE = _ROT47_HIGH - _ROT47_LOW + 1  # 94 printable characters
_ROT47_SHIFT = 47


def rot13(text: str) -> str:
    """
    Apply ROT13 to letters, leaving other characters unchanged (self-inverse)
    """
    return CaesarCipher(key = 13).encrypt(text)


def rot47(text: str) -> str:
    """
    Apply ROT47 across printable ASCII 33-126, leaving others unchanged (self-inverse)
    """
    result: list[str] = []
    for char in text:
        code = ord(char)
        if _ROT47_LOW <= code <= _ROT47_HIGH:
            rotated = (code - _ROT47_LOW + _ROT47_SHIFT) % _ROT47_RANGE
            result.append(chr(_ROT47_LOW + rotated))
        else:
            result.append(char)
    return "".join(result)
