#!/usr/bin/env python3
"""
encryption_tool.py
------------------
Small security toolkit for the ETTCS801 Integrated Situation (Task 2).

Provides:
    genkey   - generate a new symmetric encryption key
    encrypt  - encrypt a file using the key
    decrypt  - decrypt a file and verify it matches the original
    hash     - calculate the SHA-256 hash of a file
    verify   - check whether a file's current hash matches a stored hash

Uses Fernet (AES-128 in CBC mode with HMAC authentication) from the
`cryptography` library, so encrypted files are both confidential and
tamper-evident on their own. A separate SHA-256 hash utility is also
provided to satisfy the explicit integrity-check requirement (2c).

IMPORTANT: Never commit the key file or real student records to GitHub.
Keep the key outside the repository (see README.md).
"""

import argparse
import hashlib
import sys
from pathlib import Path

from cryptography.fernet import Fernet, InvalidToken


# ---------------------------------------------------------------------------
# Key management
# ---------------------------------------------------------------------------

def generate_key(key_path: Path) -> None:
    """Generate a new Fernet key and save it to key_path."""
    try:
        key = Fernet.generate_key()
        key_path.parent.mkdir(parents=True, exist_ok=True)
        key_path.write_bytes(key)
        print(f"[OK] New key written to: {key_path}")
        print("     Keep this file private and outside the Git repository.")
    except OSError as e:
        print(f"[ERROR] Could not write key file: {e}")
        sys.exit(1)


def load_key(key_path: Path) -> bytes:
    """Load a Fernet key from disk, with friendly error handling."""
    try:
        key = key_path.read_bytes()
    except FileNotFoundError:
        print(f"[ERROR] Key file not found: {key_path}")
        print("        Run 'python encryption_tool.py genkey' first.")
        sys.exit(1)
    except OSError as e:
        print(f"[ERROR] Could not read key file: {e}")
        sys.exit(1)

    try:
        Fernet(key)  # validates key format
    except (ValueError, TypeError):
        print(f"[ERROR] Key file is invalid or corrupted: {key_path}")
        sys.exit(1)

    return key


# ---------------------------------------------------------------------------
# Encryption / decryption
# ---------------------------------------------------------------------------

def encrypt_file(input_path: Path, output_path: Path, key: bytes) -> None:
    try:
        data = input_path.read_bytes()
    except FileNotFoundError:
        print(f"[ERROR] Input file not found: {input_path}")
        sys.exit(1)
    except OSError as e:
        print(f"[ERROR] Could not read input file: {e}")
        sys.exit(1)

    if len(data) == 0:
        print(f"[ERROR] Input file is empty: {input_path}")
        sys.exit(1)

    fernet = Fernet(key)
    token = fernet.encrypt(data)

    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(token)
    except OSError as e:
        print(f"[ERROR] Could not write encrypted output: {e}")
        sys.exit(1)

    print(f"[OK] Encrypted '{input_path}' -> '{output_path}'")
    print(f"     SHA-256 of original file: {sha256_of_bytes(data)}")


def decrypt_file(input_path: Path, output_path: Path, key: bytes,
                  original_path: Path | None = None) -> None:
    try:
        token = input_path.read_bytes()
    except FileNotFoundError:
        print(f"[ERROR] Encrypted file not found: {input_path}")
        sys.exit(1)
    except OSError as e:
        print(f"[ERROR] Could not read encrypted file: {e}")
        sys.exit(1)

    fernet = Fernet(key)
    try:
        data = fernet.decrypt(token)
    except InvalidToken:
        print("[ERROR] Decryption failed: wrong key, or the file is corrupted/tampered with.")
        sys.exit(1)

    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(data)
    except OSError as e:
        print(f"[ERROR] Could not write decrypted output: {e}")
        sys.exit(1)

    print(f"[OK] Decrypted '{input_path}' -> '{output_path}'")

    if original_path is not None:
        if not original_path.exists():
            print(f"[WARN] Cannot verify: original file not found at {original_path}")
            return
        original_data = original_path.read_bytes()
        if original_data == data:
            print("[OK] Verification PASSED: decrypted content matches the original file.")
        else:
            print("[FAIL] Verification FAILED: decrypted content differs from the original file.")


# ---------------------------------------------------------------------------
# Integrity (SHA-256)
# ---------------------------------------------------------------------------

def sha256_of_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def hash_file(path: Path, hash_out: Path | None = None) -> str:
    try:
        data = path.read_bytes()
    except FileNotFoundError:
        print(f"[ERROR] File not found: {path}")
        sys.exit(1)
    except OSError as e:
        print(f"[ERROR] Could not read file: {e}")
        sys.exit(1)

    digest = sha256_of_bytes(data)
    print(f"[OK] SHA-256({path}) = {digest}")

    if hash_out is not None:
        try:
            hash_out.write_text(digest + "\n")
            print(f"     Hash saved to: {hash_out}")
        except OSError as e:
            print(f"[ERROR] Could not write hash file: {e}")
            sys.exit(1)

    return digest


def verify_integrity(path: Path, hash_file_path: Path) -> None:
    try:
        stored_hash = hash_file_path.read_text().strip()
    except FileNotFoundError:
        print(f"[ERROR] Stored hash file not found: {hash_file_path}")
        sys.exit(1)
    except OSError as e:
        print(f"[ERROR] Could not read stored hash file: {e}")
        sys.exit(1)

    try:
        current_data = path.read_bytes()
    except FileNotFoundError:
        print(f"[ERROR] File to verify not found: {path}")
        sys.exit(1)
    except OSError as e:
        print(f"[ERROR] Could not read file to verify: {e}")
        sys.exit(1)

    current_hash = sha256_of_bytes(current_data)

    print(f"     Stored hash : {stored_hash}")
    print(f"     Current hash: {current_hash}")

    if current_hash == stored_hash:
        print("[OK] Integrity check PASSED: file has not changed.")
    else:
        print("[FAIL] Integrity check FAILED: file has been modified since the hash was recorded.")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Small security toolkit: encrypt, decrypt, hash and verify files."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_genkey = sub.add_parser("genkey", help="Generate a new encryption key")
    p_genkey.add_argument("--key", default="../secret.key",
                           help="Path to save the key (default: ../secret.key, kept outside the repo)")

    p_enc = sub.add_parser("encrypt", help="Encrypt a file")
    p_enc.add_argument("input", help="Path to the plaintext file")
    p_enc.add_argument("output", help="Path to write the encrypted file")
    p_enc.add_argument("--key", default="../secret.key", help="Path to the key file")

    p_dec = sub.add_parser("decrypt", help="Decrypt a file and optionally verify it")
    p_dec.add_argument("input", help="Path to the encrypted file")
    p_dec.add_argument("output", help="Path to write the decrypted file")
    p_dec.add_argument("--key", default="../secret.key", help="Path to the key file")
    p_dec.add_argument("--compare-to", default=None,
                        help="Original plaintext file to compare against after decrypting")

    p_hash = sub.add_parser("hash", help="Calculate the SHA-256 hash of a file")
    p_hash.add_argument("input", help="Path to the file to hash")
    p_hash.add_argument("--save", default=None, help="Path to save the hash to a text file")

    p_verify = sub.add_parser("verify", help="Verify a file against a previously saved hash")
    p_verify.add_argument("input", help="Path to the file to check")
    p_verify.add_argument("hashfile", help="Path to the previously saved hash file")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "genkey":
        generate_key(Path(args.key))
    elif args.command == "encrypt":
        key = load_key(Path(args.key))
        encrypt_file(Path(args.input), Path(args.output), key)
    elif args.command == "decrypt":
        key = load_key(Path(args.key))
        compare_to = Path(args.compare_to) if args.compare_to else None
        decrypt_file(Path(args.input), Path(args.output), key, compare_to)
    elif args.command == "hash":
        save = Path(args.save) if args.save else None
        hash_file(Path(args.input), save)
    elif args.command == "verify":
        verify_integrity(Path(args.input), Path(args.hashfile))


if __name__ == "__main__":
    main()
