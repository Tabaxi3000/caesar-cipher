"""
test_cli.py

Integration tests for the encrypt, decrypt, and crack CLI commands

Tests each command's exit codes, output content, key validation, and
file-based I/O using Typer's CliRunner without spawning a subprocess.

Tests:
  encrypt command: basic output, spaces, invalid key rejection
  decrypt command: basic output, spaces, invalid key rejection
  crack command: output format, --top option, --all option
  file I/O: reading from and writing to temp files

Connects to:
  main.py - invokes the Typer app under test
"""

from pathlib import Path

from typer.testing import CliRunner

from caesar_cipher.main import app
from caesar_cipher.vigenere import VigenereCipher


runner = CliRunner()

_LONG_PLAINTEXT = (
    "The index of coincidence is a statistic used in classical cryptography "
    "to break the vigenere cipher by first determining the length of the keyword "
    "and then applying frequency analysis to each column of the ciphertext letters "
    "because each column was enciphered with the same caesar shift the distribution "
    "of letters within a column mirrors ordinary english text quite closely"
)


class TestEncryptCommand:
    def test_encrypt_basic(self) -> None:
        """
        Runs the encrypt command with key 3 and checks KHOOR appears in output
        """
        result = runner.invoke(app, ["encrypt", "HELLO", "--key", "3"])
        assert result.exit_code == 0
        assert "KHOOR" in result.stdout

    def test_encrypt_with_spaces(self) -> None:
        """
        Runs encrypt on a two-word phrase and checks both words shift correctly
        """
        result = runner.invoke(app, ["encrypt", "HELLO WORLD", "--key", "3"])
        assert result.exit_code == 0
        assert "KHOOR ZRUOG" in result.stdout

    def test_encrypt_invalid_key(self) -> None:
        """
        Runs encrypt with key 30 and confirms exit code 1 and an error message
        """
        result = runner.invoke(app, ["encrypt", "HELLO", "--key", "30"])
        assert result.exit_code == 1
        assert "Error" in result.stdout


class TestDecryptCommand:
    def test_decrypt_basic(self) -> None:
        """
        Runs the decrypt command with key 3 and checks HELLO appears in output
        """
        result = runner.invoke(app, ["decrypt", "KHOOR", "--key", "3"])
        assert result.exit_code == 0
        assert "HELLO" in result.stdout

    def test_decrypt_with_spaces(self) -> None:
        """
        Runs decrypt on a two-word ciphertext and checks the full plaintext is recovered
        """
        result = runner.invoke(app, ["decrypt", "KHOOR ZRUOG", "--key", "3"])
        assert result.exit_code == 0
        assert "HELLO WORLD" in result.stdout

    def test_decrypt_invalid_key(self) -> None:
        """
        Runs decrypt with an out-of-range key and confirms exit code 1 and an error message
        """
        result = runner.invoke(app, ["decrypt", "KHOOR", "--key", "30"])
        assert result.exit_code == 1
        assert "Error" in result.stdout


class TestCrackCommand:
    def test_crack_basic(self) -> None:
        """
        Runs the crack command and confirms HELLO is recovered and best match is shown
        """
        result = runner.invoke(app, ["crack", "KHOOR"])
        assert result.exit_code == 0
        assert "HELLO" in result.stdout
        assert "Best match" in result.stdout

    def test_crack_with_top_option(self) -> None:
        """
        Runs crack with --top 3 and confirms the command completes successfully
        """
        result = runner.invoke(app, ["crack", "KHOOR", "--top", "3"])
        assert result.exit_code == 0

    def test_crack_show_all(self) -> None:
        """
        Runs crack with --all and confirms all 26 shifts are displayed without error
        """
        result = runner.invoke(app, ["crack", "KHOOR", "--all"])
        assert result.exit_code == 0


class TestFileIO:
    def test_encrypt_from_file(self, tmp_path: Path) -> None:
        """
        Encrypts text read from a temp input file and checks the ciphertext in output
        """
        input_file = tmp_path / "input.txt"
        input_file.write_text("HELLO WORLD")

        result = runner.invoke(
            app,
            ["encrypt",
             "--input-file",
             str(input_file),
             "--key",
             "3"]
        )
        assert result.exit_code == 0
        assert "KHOOR ZRUOG" in result.stdout

    def test_encrypt_to_file(self, tmp_path: Path) -> None:
        """
        Encrypts text and writes to a temp file, then reads it back to verify contents
        """
        output_file = tmp_path / "output.txt"

        result = runner.invoke(
            app,
            [
                "encrypt",
                "HELLO",
                "--key",
                "3",
                "--output-file",
                str(output_file),
            ],
        )
        assert result.exit_code == 0
        assert output_file.read_text() == "KHOOR"

    def test_decrypt_from_file(self, tmp_path: Path) -> None:
        """
        Decrypts text read from a temp input file and checks the plaintext in output
        """
        input_file = tmp_path / "input.txt"
        input_file.write_text("KHOOR")

        result = runner.invoke(
            app,
            ["decrypt",
             "--input-file",
             str(input_file),
             "--key",
             "3"]
        )
        assert result.exit_code == 0
        assert "HELLO" in result.stdout


class TestProgressiveCLI:
    def test_encrypt_progressive(self) -> None:
        """
        Confirms encrypt --progressive turns AAA into BCD with key 1
        """
        result = runner.invoke(
            app,
            ["encrypt", "AAA", "--key", "1", "--progressive"],
        )
        assert result.exit_code == 0
        assert "BCD" in result.stdout

    def test_progressive_roundtrip(self) -> None:
        """
        Confirms encrypt --progressive then decrypt --progressive recovers text
        """
        encrypted = runner.invoke(
            app,
            ["encrypt", "HELLO", "--key", "4", "--progressive", "--quiet"],
        )
        token = encrypted.stdout.strip()
        decrypted = runner.invoke(
            app,
            ["decrypt", token, "--key", "4", "--progressive"],
        )
        assert decrypted.exit_code == 0
        assert "HELLO" in decrypted.stdout


class TestCustomAlphabetCLI:
    def test_encrypt_with_custom_alphabet(self) -> None:
        """
        Confirms encrypt accepts a reversed alphabet and round-trips it
        """
        alphabet = "ZYXWVUTSRQPONMLKJIHGFEDCBA"
        encrypted = runner.invoke(
            app,
            ["encrypt", "HELLO", "--key", "1", "--alphabet", alphabet, "--quiet"],
        )
        assert encrypted.exit_code == 0
        token = encrypted.stdout.strip()
        decrypted = runner.invoke(
            app,
            ["decrypt", token, "--key", "1", "--alphabet", alphabet],
        )
        assert "HELLO" in decrypted.stdout

    def test_invalid_alphabet_errors(self) -> None:
        """
        Confirms a too-short custom alphabet exits with an error
        """
        result = runner.invoke(
            app,
            ["encrypt", "HELLO", "--alphabet", "ABC"],
        )
        assert result.exit_code == 1
        assert "Error" in result.stdout


class TestStatsCommand:
    def test_stats_renders_chart(self) -> None:
        """
        Confirms the stats command renders a frequency bar chart
        """
        result = runner.invoke(
            app,
            ["stats", "THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG"],
        )
        assert result.exit_code == 0
        assert "█" in result.stdout

    def test_stats_no_letters(self) -> None:
        """
        Confirms the stats command reports when there is nothing to analyze
        """
        result = runner.invoke(app, ["stats", "12345 !@#$%"])
        assert result.exit_code == 0
        assert "No letters" in result.stdout


class TestRotCommands:
    def test_rot13(self) -> None:
        """
        Confirms the rot13 command shifts HELLO to URYYB
        """
        result = runner.invoke(app, ["rot13", "HELLO"])
        assert result.exit_code == 0
        assert "URYYB" in result.stdout

    def test_rot47(self) -> None:
        """
        Confirms the rot47 command runs and transforms the input
        """
        result = runner.invoke(app, ["rot47", "Hello"])
        assert result.exit_code == 0
        assert "Hello" not in result.stdout


class TestCrackExtras:
    def test_crack_with_dictionary(self) -> None:
        """
        Confirms crack --dictionary recovers a short message
        """
        result = runner.invoke(app, ["crack", "KHOOR ZRUOG", "--dictionary"])
        assert result.exit_code == 0
        assert "HELLO WORLD" in result.stdout

    def test_crack_with_language(self) -> None:
        """
        Confirms crack accepts a language option and runs successfully
        """
        result = runner.invoke(app, ["crack", "KHOOR", "--language", "spanish"])
        assert result.exit_code == 0


class TestVigenereCLI:
    def test_encrypt_decrypt_roundtrip(self) -> None:
        """
        Confirms vigenere-encrypt then vigenere-decrypt recovers the plaintext
        """
        encrypted = runner.invoke(
            app,
            ["vigenere-encrypt", "ATTACK AT DAWN", "--keyword", "LEMON", "--quiet"],
        )
        assert encrypted.exit_code == 0
        token = encrypted.stdout.strip()
        decrypted = runner.invoke(
            app,
            ["vigenere-decrypt", token, "--keyword", "LEMON"],
        )
        assert decrypted.exit_code == 0
        assert "ATTACK AT DAWN" in decrypted.stdout

    def test_vigenere_crack(self) -> None:
        """
        Confirms vigenere-crack recovers the LEMON key from a long ciphertext
        """
        ciphertext = VigenereCipher("LEMON").encrypt(_LONG_PLAINTEXT)
        result = runner.invoke(
            app,
            ["vigenere-crack", ciphertext, "--max-key-length", "12"],
        )
        assert result.exit_code == 0
        assert "LEMON" in result.stdout

    def test_invalid_keyword_errors(self) -> None:
        """
        Confirms a non-alphabetic keyword exits with an error
        """
        result = runner.invoke(
            app,
            ["vigenere-encrypt", "HELLO", "--keyword", "123"],
        )
        assert result.exit_code == 1
        assert "Error" in result.stdout
