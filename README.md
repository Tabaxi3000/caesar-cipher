```ruby
 ██████╗ █████╗ ███████╗███████╗ █████╗ ██████╗
██╔════╝██╔══██╗██╔════╝██╔════╝██╔══██╗██╔══██╗
██║     ███████║█████╗  ███████╗███████║██████╔╝
██║     ██╔══██║██╔══╝  ╚════██║██╔══██║██╔══██╗
╚██████╗██║  ██║███████╗███████║██║  ██║██║  ██║
 ╚═════╝╚═╝  ╚═╝╚══════╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝
```

> Caesar cipher encryption, decryption, and brute-force cracking CLI with frequency analysis.

## What It Does

- Encrypt text using Caesar cipher with a specified shift key
- Decrypt ciphertext back to plaintext with the original key
- Brute-force crack unknown ciphertext by testing all 26 shifts
- Frequency analysis ranking to identify the most likely plaintext
- Clean Rich terminal output with colored tables

## Quick Start

```bash
uv tool install caesar-salad-cipher
caesar-cipher encrypt "HELLO WORLD" --key 3
```

> [!TIP]
> This project uses [`just`](https://github.com/casey/just) as a command runner. Type `just` to see all available commands.
>
> Install: `curl -sSf https://just.systems/install.sh | bash -s -- --to ~/.local/bin`

## Commands

| Command | Description |
|---------|-------------|
| `caesar-cipher encrypt` | Encrypt plaintext using a specified shift key |
| `caesar-cipher decrypt` | Decrypt ciphertext back to plaintext with the original key |
| `caesar-cipher crack` | Brute-force all 26 shifts with frequency analysis ranking |