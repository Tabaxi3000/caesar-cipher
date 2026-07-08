"""
main.py

CLI entry point wiring cipher, analysis, and web commands via Typer

Registers the classic Caesar commands (encrypt, decrypt, crack) plus the
extension commands: progressive-shift and custom-alphabet options on
encrypt/decrypt (Challenges 1, 2), a stats frequency chart (Challenge 3),
rot13/rot47 (Challenge 4), dictionary and multi-language cracking
(Challenges 5, 6), Vigenere encrypt/decrypt/crack (Challenge 7), and a
serve command that launches the web visualizer (Challenge 8).

Key exports:
  app - Typer application, registered as the caesar-cipher CLI entry point

Connects to:
  cipher.py - CaesarCipher for encrypt/decrypt/crack
  analyzer.py - FrequencyAnalyzer for crack ranking and stats
  dictionary.py - dictionary-based crack ranking
  vigenere.py - Vigenere encrypt/decrypt/crack
  rot.py - rot13 and rot47 transforms
  web.py - lazily imported by the serve command
  utils.py - read_input, validate_key, write_output
"""

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from caesar_cipher.analyzer import FrequencyAnalyzer
from caesar_cipher.cipher import CaesarCipher
from caesar_cipher.constants import Language
from caesar_cipher.dictionary import load_words, rank_candidates_combined
from caesar_cipher.rot import rot13, rot47
from caesar_cipher.utils import read_input, validate_key, write_output
from caesar_cipher.vigenere import (
    VigenereCipher,
    crack_vigenere,
    kasiski_examination,
)


app = typer.Typer(
    name = "caesar-cipher",
    help = "Caesar cipher encryption, decryption, and brute-force cracking tool",
    no_args_is_help = True,
)
console = Console()


@app.command()
def encrypt(
    text: Annotated[
        str | None,
        typer.Argument(help = "Text to encrypt (or use --input-file or stdin)"),
    ] = None,
    key: Annotated[int,
                   typer.Option("--key",
                                "-k",
                                help = "Shift key (0-25)")] = 3,
    alphabet: Annotated[
        str | None,
        typer.Option("--alphabet",
                     help = "Custom 26-letter alphabet")] = None,
    progressive: Annotated[
        bool,
        typer.Option("--progressive",
                     "-p",
                     help = "Position-dependent shift (key + position)")] = False,
    input_file: Annotated[
        Path | None,
        typer.Option("--input-file",
                     "-i",
                     help = "Input file path")] = None,
    output_file: Annotated[
        Path | None,
        typer.Option("--output-file",
                     "-o",
                     help = "Output file path")] = None,
    quiet: Annotated[
        bool,
        typer.Option("--quiet",
                     "-q",
                     help = "Suppress output messages")] = False,
) -> None:
    """
    Encrypt text using Caesar cipher with specified shift key
    """
    try:
        validate_key(key)
        plaintext = read_input(text, input_file)
        cipher = CaesarCipher(key = key, alphabet = alphabet)
        encrypted = (
            cipher.encrypt_progressive(plaintext) if progressive
            else cipher.encrypt(plaintext)
        )

        if not quiet and not output_file:
            console.print(f"[green]Encrypted:[/green] {encrypted}")
        else:
            write_output(encrypted, output_file, quiet)

    except (ValueError, OSError) as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code = 1) from None


@app.command()
def decrypt(
    text: Annotated[
        str | None,
        typer.Argument(help = "Text to decrypt (or use --input-file or stdin)"),
    ] = None,
    key: Annotated[int,
                   typer.Option("--key",
                                "-k",
                                help = "Shift key (0-25)")] = 3,
    alphabet: Annotated[
        str | None,
        typer.Option("--alphabet",
                     help = "Custom 26-letter alphabet")] = None,
    progressive: Annotated[
        bool,
        typer.Option("--progressive",
                     "-p",
                     help = "Position-dependent shift (key + position)")] = False,
    input_file: Annotated[
        Path | None,
        typer.Option("--input-file",
                     "-i",
                     help = "Input file path")] = None,
    output_file: Annotated[
        Path | None,
        typer.Option("--output-file",
                     "-o",
                     help = "Output file path")] = None,
    quiet: Annotated[
        bool,
        typer.Option("--quiet",
                     "-q",
                     help = "Suppress output messages")] = False,
) -> None:
    """
    Decrypt text using Caesar cipher with specified shift key
    """
    try:
        validate_key(key)
        ciphertext = read_input(text, input_file)
        cipher = CaesarCipher(key = key, alphabet = alphabet)
        decrypted = (
            cipher.decrypt_progressive(ciphertext) if progressive
            else cipher.decrypt(ciphertext)
        )

        if not quiet and not output_file:
            console.print(f"[blue]Decrypted:[/blue] {decrypted}")
        else:
            write_output(decrypted, output_file, quiet)

    except (ValueError, OSError) as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code = 1) from None


@app.command()
def crack(
    text: Annotated[
        str | None,
        typer.Argument(help = "Text to crack (or use --input-file or stdin)"),
    ] = None,
    input_file: Annotated[
        Path | None,
        typer.Option("--input-file",
                     "-i",
                     help = "Input file path")] = None,
    top: Annotated[int,
                   typer.Option("--top",
                                "-t",
                                help = "Show top N candidates")] = 5,
    show_all: Annotated[
        bool,
        typer.Option("--all",
                     "-a",
                     help = "Show all 26 possible shifts")] = False,
    language: Annotated[
        Language,
        typer.Option("--language",
                     "-l",
                     help = "Language frequency table to score against")] = Language.ENGLISH,
    use_dictionary: Annotated[
        bool,
        typer.Option("--dictionary",
                     "-D",
                     help = "Rank using dictionary word matches too")] = False,
) -> None:
    """
    Brute-force decrypt text by trying all shifts with frequency analysis ranking
    """
    try:
        ciphertext = read_input(text, input_file)
        candidates = CaesarCipher.crack(ciphertext)
        analyzer = FrequencyAnalyzer(language)

        if use_dictionary:
            ranked = rank_candidates_combined(
                candidates, analyzer, load_words()
            )
            score_label = "Score (higher=better)"
        else:
            ranked = analyzer.rank_candidates(candidates)
            score_label = "Score (lower=better)"

        table = Table(title = "Caesar Cipher Brute Force Results")
        table.add_column("Rank", style = "cyan", justify = "right")
        table.add_column("Shift", style = "magenta", justify = "right")
        table.add_column(score_label, style = "yellow", justify = "right")
        table.add_column("Decrypted Text", style = "green")

        display_count = len(ranked) if show_all else min(top, len(ranked))

        for rank, (shift, text_result, score) in enumerate(ranked[:display_count], 1):
            table.add_row(
                str(rank),
                str(shift),
                f"{score:.2f}",
                text_result[: 80]
            )

        console.print(table)
        console.print(
            f"\n[bold]Best match (Shift {ranked[0][0]}):[/bold] {ranked[0][1]}"
        )

    except (ValueError, OSError) as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code = 1) from None


@app.command()
def stats(
    text: Annotated[
        str | None,
        typer.Argument(help = "Text to analyze (or use --input-file or stdin)"),
    ] = None,
    input_file: Annotated[
        Path | None,
        typer.Option("--input-file",
                     "-i",
                     help = "Input file path")] = None,
    language: Annotated[
        Language,
        typer.Option("--language",
                     "-l",
                     help = "Language to compare frequencies against")] = Language.ENGLISH,
) -> None:
    """
    Show a letter frequency bar chart for the given text
    """
    try:
        content = read_input(text, input_file)
        analyzer = FrequencyAnalyzer(language)
        counts = analyzer.letter_counts(content)
        frequencies = analyzer.letter_frequencies(content)
        total = sum(counts.values())

        if total == 0:
            console.print("[yellow]No letters to analyze.[/yellow]")
            return

        max_freq = max(frequencies.values())
        ordered = sorted(
            frequencies.items(),
            key = lambda item: item[1],
            reverse = True,
        )

        table = Table(title = f"Letter Frequency ({total} letters)")
        table.add_column("Letter", style = "cyan", justify = "center")
        table.add_column("Count", style = "magenta", justify = "right")
        table.add_column("Freq", style = "yellow", justify = "right")
        table.add_column("Distribution", style = "green")

        for letter, freq in ordered:
            if counts.get(letter, 0) == 0:
                continue
            bar_length = round((freq / max_freq) * 40) if max_freq else 0
            table.add_row(
                letter,
                str(counts.get(letter, 0)),
                f"{freq:.1f}%",
                "█" * bar_length,
            )

        console.print(table)

    except (ValueError, OSError) as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code = 1) from None


@app.command(name = "rot13")
def rot13_cmd(
    text: Annotated[
        str | None,
        typer.Argument(help = "Text to transform (or use --input-file or stdin)"),
    ] = None,
    input_file: Annotated[
        Path | None,
        typer.Option("--input-file",
                     "-i",
                     help = "Input file path")] = None,
) -> None:
    """
    Apply ROT13 (self-inverse shift of 13); run twice to get the original back
    """
    try:
        content = read_input(text, input_file)
        console.print(rot13(content))
    except (ValueError, OSError) as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code = 1) from None


@app.command(name = "rot47")
def rot47_cmd(
    text: Annotated[
        str | None,
        typer.Argument(help = "Text to transform (or use --input-file or stdin)"),
    ] = None,
    input_file: Annotated[
        Path | None,
        typer.Option("--input-file",
                     "-i",
                     help = "Input file path")] = None,
) -> None:
    """
    Apply ROT47 across printable ASCII (self-inverse); covers digits and punctuation
    """
    try:
        content = read_input(text, input_file)
        console.print(rot47(content))
    except (ValueError, OSError) as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code = 1) from None


@app.command(name = "vigenere-encrypt")
def vigenere_encrypt(
    text: Annotated[
        str | None,
        typer.Argument(help = "Text to encrypt (or use --input-file or stdin)"),
    ] = None,
    keyword: Annotated[
        str,
        typer.Option("--keyword",
                     "-w",
                     help = "Vigenere keyword")] = "KEY",
    input_file: Annotated[
        Path | None,
        typer.Option("--input-file",
                     "-i",
                     help = "Input file path")] = None,
    output_file: Annotated[
        Path | None,
        typer.Option("--output-file",
                     "-o",
                     help = "Output file path")] = None,
    quiet: Annotated[
        bool,
        typer.Option("--quiet",
                     "-q",
                     help = "Suppress output messages")] = False,
) -> None:
    """
    Encrypt text with the Vigenere cipher using a keyword
    """
    try:
        plaintext = read_input(text, input_file)
        encrypted = VigenereCipher(keyword).encrypt(plaintext)
        if not quiet and not output_file:
            console.print(f"[green]Encrypted:[/green] {encrypted}")
        else:
            write_output(encrypted, output_file, quiet)
    except (ValueError, OSError) as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code = 1) from None


@app.command(name = "vigenere-decrypt")
def vigenere_decrypt(
    text: Annotated[
        str | None,
        typer.Argument(help = "Text to decrypt (or use --input-file or stdin)"),
    ] = None,
    keyword: Annotated[
        str,
        typer.Option("--keyword",
                     "-w",
                     help = "Vigenere keyword")] = "KEY",
    input_file: Annotated[
        Path | None,
        typer.Option("--input-file",
                     "-i",
                     help = "Input file path")] = None,
    output_file: Annotated[
        Path | None,
        typer.Option("--output-file",
                     "-o",
                     help = "Output file path")] = None,
    quiet: Annotated[
        bool,
        typer.Option("--quiet",
                     "-q",
                     help = "Suppress output messages")] = False,
) -> None:
    """
    Decrypt Vigenere ciphertext using a keyword
    """
    try:
        ciphertext = read_input(text, input_file)
        decrypted = VigenereCipher(keyword).decrypt(ciphertext)
        if not quiet and not output_file:
            console.print(f"[blue]Decrypted:[/blue] {decrypted}")
        else:
            write_output(decrypted, output_file, quiet)
    except (ValueError, OSError) as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code = 1) from None


@app.command(name = "vigenere-crack")
def vigenere_crack(
    text: Annotated[
        str | None,
        typer.Argument(help = "Ciphertext to crack (or use --input-file or stdin)"),
    ] = None,
    input_file: Annotated[
        Path | None,
        typer.Option("--input-file",
                     "-i",
                     help = "Input file path")] = None,
    max_key_length: Annotated[
        int,
        typer.Option("--max-key-length",
                     "-m",
                     help = "Maximum key length to consider")] = 20,
    language: Annotated[
        Language,
        typer.Option("--language",
                     "-l",
                     help = "Language frequency table to score against")] = Language.ENGLISH,
) -> None:
    """
    Recover a Vigenere key and plaintext from ciphertext using Kasiski and IC
    """
    try:
        ciphertext = read_input(text, input_file)
        result = crack_vigenere(
            ciphertext,
            max_key_length = max_key_length,
            language = language,
        )
        kasiski = kasiski_examination(ciphertext, max_key_length = max_key_length)

        console.print(f"[bold]Index of coincidence:[/bold] {result.index_of_coincidence:.4f}")
        if kasiski:
            hints = ", ".join(str(length) for length in kasiski[: 5])
            console.print(f"[bold]Kasiski key-length hints:[/bold] {hints}")
        console.print(f"[bold]Recovered key:[/bold] [magenta]{result.key}[/magenta] "
                      f"(length {result.key_length})")
        console.print(f"[green]Plaintext:[/green] {result.plaintext}")

    except (ValueError, OSError) as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code = 1) from None


@app.command()
def serve(
    host: Annotated[str,
                    typer.Option("--host",
                                 "-h",
                                 help = "Host to bind")] = "127.0.0.1",
    port: Annotated[int,
                    typer.Option("--port",
                                 "-p",
                                 help = "Port to listen on")] = 5000,
) -> None:
    """
    Launch the live frequency-analysis web visualizer (requires the web extra)
    """
    try:
        from caesar_cipher.web import create_app
    except ImportError:
        console.print(
            "[red]Error:[/red] Flask is not installed. "
            "Install it with: pip install 'caesar-salad-cipher[web]'"
        )
        raise typer.Exit(code = 1) from None

    console.print(f"[green]Serving on[/green] http://{host}:{port}")
    create_app().run(host = host, port = port)


if __name__ == "__main__":
    app()
