"""
JSON Obfuscator/Encryptor CLI Tool

This script provides functionality to obfuscate and encrypt the keys and values of a JSON file or inline JSON data,
and later decrypt and deobfuscate it back to the original structure using a password.

Key Features:
- Obfuscate JSON keys using base64 encoding
- Encrypt JSON values using AES encryption with a derived key from a user-provided password
- Store and reuse salt and key mappings for decryption
- Supports both file-based and inline JSON input/output

Usage Examples:
---------------------
Encrypt a JSON file:
    python obfuscator_json.py -i data.json -p secret

Encrypt a JSON string:
    python obfuscator_json.py -j '{"email": "test@example.com", "name": "John"}' -p secret

Decrypt an obfuscated file:
    python obfuscator_json.py -i data.json.obfuscated -m data.json.obfuscated.mapping.json -p secret -d

Decrypt inline JSON:
    python obfuscator_json.py -j '{"ZW1haWw": "..."}' -m data.json.obfuscated.mapping.json -p secret -d

Outputs:
- The obfuscated JSON file
- A `.mapping.json` file containing the key mapping and salt used for encryption
"""

import os
import argparse
import base64
import json
from typing import Tuple

# Cryptography modules for key derivation and AES encryption/decryption
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC  # unused but common alternative
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt  # key derivation using Scrypt
from cryptography.hazmat.primitives import hashes, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

# Global default extension for obfuscated output
DEFAULT_OUTPUT_EXTENSION = "obfuscated"


def generate_key(password: str, salt: bytes) -> bytes:
    """
    Generate a symmetric key from the user's password using Scrypt key derivation.

    Args:
        password (str): The user-provided password.
        salt (bytes): Random salt used to make the key derivation unique and secure.

    Returns:
        bytes: A derived 256-bit (32-byte) key for encryption/decryption.
    """
    kdf = Scrypt(
        salt=salt,
        length=32,
        n=2**14,
        r=8,
        p=1,
        backend=default_backend()
    )
    return kdf.derive(password.encode())


def encrypt_value(value: str, key: bytes) -> str:
    """
    Encrypt a single string value using AES encryption in CBC mode.

    Args:
        value (str): The plaintext string to encrypt.
        key (bytes): The symmetric key used for encryption.

    Returns:
        str: A base64-encoded string containing IV + ciphertext.
    """
    iv = os.urandom(16)  # Generate a random 16-byte IV
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    # Apply PKCS7 padding to match AES block size (16 bytes)
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(value.encode()) + padder.finalize()

    encrypted_value = encryptor.update(padded_data) + encryptor.finalize()

    # Encode IV + ciphertext into base64 for storage
    return base64.b64encode(iv + encrypted_value).decode()


def decrypt_value(encrypted_value: str, key: bytes) -> str:
    """
    Decrypt a base64-encoded AES-encrypted string.

    Args:
        encrypted_value (str): The encrypted string (IV + ciphertext) in base64.
        key (bytes): The key used during encryption.

    Returns:
        str: The original plaintext string.
    """
    data = base64.b64decode(encrypted_value.encode())
    iv = data[:16]
    encrypted_data = data[16:]

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    padded_data = decryptor.update(encrypted_data) + decryptor.finalize()

    # Remove PKCS7 padding after decryption
    unpadder = padding.PKCS7(128).unpadder()
    value = unpadder.update(padded_data) + unpadder.finalize()

    return value.decode()


def obfuscate_json(input_data: dict, password: str) -> Tuple[dict, dict, bytes]:
    """
    Obfuscate the keys and encrypt the values of a given JSON dictionary.

    Args:
        input_data (dict): The original JSON data.
        password (str): Password to derive the encryption key.

    Returns:
        Tuple[dict, dict, bytes]: Obfuscated data, key mapping, and salt used for key derivation.
    """
    salt = os.urandom(16)  # Random salt for key derivation
    key = generate_key(password, salt)
    obfuscation_mapping = {}
    obfuscated_data = {}

    for key_name, value in input_data.items():
        # Obfuscate key using base64 URL-safe encoding (without padding)
        obfuscated_key = base64.urlsafe_b64encode(key_name.encode()).decode().strip("=")

        # Encrypt value
        encrypted_value = encrypt_value(value, key)

        # Store mapping and obfuscated entry
        obfuscation_mapping[obfuscated_key] = key_name
        obfuscated_data[obfuscated_key] = encrypted_value

    return obfuscated_data, obfuscation_mapping, salt


def deobfuscate_json(input_data: dict, mapping: dict, password: str, salt: bytes) -> dict:
    """
    Revert obfuscated and encrypted JSON data back to its original form.

    Args:
        input_data (dict): Obfuscated and encrypted JSON.
        mapping (dict): Mapping from obfuscated keys to original keys.
        password (str): Password to derive the decryption key.
        salt (bytes): Salt used during encryption.

    Returns:
        dict: Original JSON structure with decrypted values.
    """
    key = generate_key(password, salt)
    deobfuscated_data = {}

    for obfuscated_key, encrypted_value in input_data.items():
        original_key = mapping[obfuscated_key]
        decrypted_value = decrypt_value(encrypted_value, key)
        deobfuscated_data[original_key] = decrypted_value

    return deobfuscated_data


def main():
    """
    Main CLI entry point.
    Parses arguments and runs either obfuscation/encryption or decryption/deobfuscation.
    """
    parser = argparse.ArgumentParser(description="Obfuscate and encrypt JSON files or data.")
    parser.add_argument("-i", "--input", help="Input JSON file or JSON data as a string")
    parser.add_argument("-o", "--output", help="Output file (default: input file with .obfuscated extension)")
    parser.add_argument("-p", "--password", required=True, help="Password for encryption")
    parser.add_argument("-d", "--decrypt", action="store_true", help="Decrypt the input file or data")
    parser.add_argument("-m", "--mapping", help="Mapping file for decryption")
    parser.add_argument("-j", "--json", help="JSON data as a string")

    args = parser.parse_args()

    if args.decrypt:
        # Decryption mode
        if not args.mapping:
            parser.error("Mapping file is required for decryption.")

        with open(args.mapping, 'r') as file:
            mapping_data = json.load(file)
            salt = base64.b64decode(mapping_data["salt"].encode())
            obfuscation_mapping = mapping_data["mapping"]

        if args.input:
            with open(args.input, 'r') as file:
                input_data = json.load(file)
        elif args.json:
            input_data = json.loads(args.json)
        else:
            parser.error("Input file or JSON data is required for decryption.")

        # Decrypt and save
        deobfuscated_data = deobfuscate_json(input_data, obfuscation_mapping, args.password, salt)
        output_file = args.output if args.output else args.input.replace(f".{DEFAULT_OUTPUT_EXTENSION}", "")

        with open(output_file, 'w') as file:
            json.dump(deobfuscated_data, file, indent=4)

        print(f"Deobfuscated file saved as {output_file}")

    else:
        # Obfuscation/encryption mode
        if args.input:
            with open(args.input, 'r') as file:
                input_data = json.load(file)
        elif args.json:
            input_data = json.loads(args.json)
        else:
            parser.error("Input file or JSON data is required.")

        obfuscated_data, obfuscation_mapping, salt = obfuscate_json(input_data, args.password)
        output_file = args.output if args.output else f"{args.input}.{DEFAULT_OUTPUT_EXTENSION}" if args.input else "output.json"

        # Save obfuscated output
        with open(output_file, 'w') as file:
            json.dump(obfuscated_data, file, indent=4)

        # Save mapping file with salt
        mapping_file = f"{output_file}.mapping.json"
        with open(mapping_file, 'w') as file:
            json.dump({"salt": base64.b64encode(salt).decode(), "mapping": obfuscation_mapping}, file, indent=4)

        print(f"Obfuscated file saved as {output_file}")
        print(f"Obfuscation mapping saved as {mapping_file}")


if __name__ == "__main__":
    main()
