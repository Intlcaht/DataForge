"""
obfuscator_env.py

A Python script for encrypting and obfuscating environment (.env) files using AES encryption.
It supports both obfuscation and deobfuscation, maintaining a mapping between original and obfuscated keys.
Enhanced with application key requirement for additional security.

Dependencies:
    - cryptography
    - argparse

Install cryptography via pip:
    pip install cryptography

Example usage:
    # To obfuscate a file
    python obfuscator_env.py -i .env -p "secret" -a "app_key_123"

    # To obfuscate and provide a custom output file
    python obfuscator_env.py -i .env -o secret.env -p "secret" -a "app_key_123"

    # To deobfuscate a file
    python obfuscator_env.py -i .env.obfuscated -m .env.obfuscated.mapping.json -p "secret" -a "app_key_123" -d
"""

import os
import argparse
import base64
import json
import hmac
import hashlib

from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

# Global default extension for obfuscated files
DEFAULT_OUTPUT_EXTENSION = "obfuscated"

def generate_key(password: str, app_key: str, salt: bytes) -> bytes:
    """
    Generates a 32-byte AES encryption key from a password and application key using the Scrypt KDF.
    
    The application key adds an additional layer of security by requiring API clients to provide
    not just the password but also a valid application key that would typically be distributed
    separately from the password.

    Args:
        password (str): The user password to derive the key from.
        app_key (str): Application-specific key required for encryption/decryption.
        salt (bytes): A random salt to make key derivation unique.

    Returns:
        bytes: The derived encryption key.
    """
    # Combine password and app_key to create a stronger composite key
    composite_key = f"{password}:{app_key}"
    
    kdf = Scrypt(
        salt=salt,
        length=32,
        n=2**14,
        r=8,
        p=1,
        backend=default_backend()
    )
    return kdf.derive(composite_key.encode())

def derive_value_specific_key(base_key: bytes, original_key_name: str) -> bytes:
    """
    Derives a value-specific encryption key by incorporating the original key name.
    This ensures that if the key name in the mapping is altered, decryption will fail.

    Args:
        base_key (bytes): The base encryption key.
        original_key_name (str): The original environment variable key name.

    Returns:
        bytes: A 32-byte key derived from the base key and original key name.
    """
    # Create an HMAC using the base key and the original key name
    h = hmac.new(base_key, original_key_name.encode(), hashlib.sha256)
    return h.digest()

def encrypt_value(value: str, key: bytes, original_key_name: str) -> str:
    """
    Encrypts a plaintext string using AES-CBC encryption with a key derived from
    both the main encryption key and the original key name.

    Args:
        value (str): The plaintext value to encrypt.
        key (bytes): The base AES key.
        original_key_name (str): The original key name to bind to the encryption.

    Returns:
        str: The base64-encoded ciphertext, including the IV.
    """
    # Derive a key-specific encryption key
    value_key = derive_value_specific_key(key, original_key_name)
    
    iv = os.urandom(16)  # Initialization vector
    cipher = Cipher(algorithms.AES(value_key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(value.encode()) + padder.finalize()

    encrypted = encryptor.update(padded_data) + encryptor.finalize()
    return base64.b64encode(iv + encrypted).decode()

def decrypt_value(encrypted_value: str, key: bytes, original_key_name: str) -> str:
    """
    Decrypts a base64-encoded ciphertext using AES-CBC with a key derived from
    both the main key and the original key name.

    Args:
        encrypted_value (str): The base64-encoded ciphertext (with IV).
        key (bytes): The base AES key.
        original_key_name (str): The original key name used during encryption.

    Returns:
        str: The decrypted plaintext string.
    """
    # Derive the same key-specific encryption key used during encryption
    value_key = derive_value_specific_key(key, original_key_name)
    
    data = base64.b64decode(encrypted_value.encode())
    iv = data[:16]
    ciphertext = data[16:]

    cipher = Cipher(algorithms.AES(value_key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    padded_data = decryptor.update(ciphertext) + decryptor.finalize()

    unpadder = padding.PKCS7(128).unpadder()
    value = unpadder.update(padded_data) + unpadder.finalize()

    return value.decode()

def generate_file_signature(content: str, key: bytes) -> str:
    """
    Generates a signature for the file content using HMAC-SHA256.
    
    This signature helps verify file integrity and detect tampering with the obfuscated file.
    
    Args:
        content (str): The content to sign.
        key (bytes): The key used for signing.
        
    Returns:
        str: Base64-encoded signature.
    """
    h = hmac.new(key, content.encode(), hashlib.sha256)
    return base64.b64encode(h.digest()).decode()

def obfuscate_env_file(input_file: str, output_file: str, password: str, app_key: str):
    """
    Obfuscates the key names and encrypts the values of a .env file.

    Args:
        input_file (str): Path to the original .env file.
        output_file (str): Path to save the obfuscated file.
        password (str): Password used to derive encryption key.
        app_key (str): Application key required for additional security.

    Outputs:
        - Encrypted .env file.
        - Mapping JSON file to reverse the obfuscation.
    """
    salt = os.urandom(16)  # Generate a unique salt for key derivation
    key = generate_key(password, app_key, salt)
    obfuscation_mapping = {}
    obfuscated_content = ""

    with open(input_file, 'r') as file:
        lines = file.readlines()

    with open(output_file, 'w') as file:
        for line in lines:
            if '=' in line:
                key_name, value = line.strip().split('=', 1)
                obfuscated_key = base64.urlsafe_b64encode(key_name.encode()).decode().strip("=")
                
                # Now we pass the original key name to bind it to the encryption
                encrypted_value = encrypt_value(value, key, key_name)

                obfuscation_mapping[obfuscated_key] = key_name
                output_line = f"{obfuscated_key}={encrypted_value}\n"
                obfuscated_content += output_line
                file.write(output_line)
    
    # Generate a signature for the obfuscated content
    file_signature = generate_file_signature(obfuscated_content, key)

    # Save mapping with the salt used for key derivation and file signature
    mapping_file = f"{output_file}.mapping.json"
    with open(mapping_file, 'w') as file:
        json.dump({
            "salt": base64.b64encode(salt).decode(), 
            "mapping": obfuscation_mapping,
            "signature": file_signature
        }, file)

    print(f"✅ Obfuscated file saved as: {output_file}")
    print(f"🧩 Mapping file saved as: {mapping_file}")
    print(f"🔑 File protected with application key and password")

def deobfuscate_env_file(input_file: str, mapping_file: str, output_file: str, password: str, app_key: str):
    """
    Decrypts and restores the original key-value pairs from an obfuscated .env file.

    Args:
        input_file (str): Path to the obfuscated .env file.
        mapping_file (str): Path to the JSON mapping file.
        output_file (str): Path to save the restored .env file.
        password (str): Password used to derive the encryption key.
        app_key (str): Application key required for additional security.
    """
    with open(mapping_file, 'r') as file:
        mapping_data = json.load(file)
        salt = base64.b64decode(mapping_data["salt"].encode())
        obfuscation_mapping = mapping_data["mapping"]
        stored_signature = mapping_data.get("signature")

    key = generate_key(password, app_key, salt)

    # Read and verify file signature if available
    if stored_signature:
        with open(input_file, 'r') as file:
            content = file.read()
        
        calculated_signature = generate_file_signature(content, key)
        if calculated_signature != stored_signature:
            print("⚠️ WARNING: File signature verification failed. The file may have been tampered with.")
            print("   Proceeding with decryption, but results may be compromised.")
    
    with open(input_file, 'r') as file:
        lines = file.readlines()

    with open(output_file, 'w') as file:
        for line in lines:
            if '=' in line:
                obfuscated_key, encrypted_value = line.strip().split('=', 1)
                original_key = obfuscation_mapping.get(obfuscated_key)
                
                if not original_key:
                    print(f"❌ Unknown key: '{obfuscated_key}' not found in mapping")
                    file.write(f"# UNKNOWN KEY: {obfuscated_key}\n")
                    continue
                
                try:
                    # Pass the original key name during decryption
                    decrypted_value = decrypt_value(encrypted_value, key, original_key)
                    file.write(f"{original_key}={decrypted_value}\n")
                except Exception as e:
                    print(f"❌ Error decrypting value for key '{original_key}': {str(e)}")
                    print("   This may indicate tampering with the mapping file or incorrect application key.")
                    # Write the error as a comment in the file to indicate the issue
                    file.write(f"# ERROR decrypting {original_key}: Possible tampering or wrong app key\n")

    print(f"🔓 Deobfuscated file saved as: {output_file}")

def main():
    """
    Command-line interface for the script. Supports both encryption (obfuscation) and decryption.
    """
    parser = argparse.ArgumentParser(description="🔐 Obfuscate and encrypt .env files")
    parser.add_argument("-i", "--input", required=True, help="Input .env file")
    parser.add_argument("-o", "--output", help="Output file name (optional)")
    parser.add_argument("-p", "--password", required=True, help="Password for encryption")
    parser.add_argument("-a", "--app-key", required=True, help="Application key for additional security")
    parser.add_argument("-d", "--decrypt", action="store_true", help="Enable to decrypt instead of encrypt")
    parser.add_argument("-m", "--mapping", help="Mapping file for decryption (required with -d)")

    args = parser.parse_args()

    if args.decrypt:
        if not args.mapping:
            parser.error("❌ Mapping file is required for decryption.")
        output_file = args.output if args.output else args.input.replace(f".{DEFAULT_OUTPUT_EXTENSION}", "")
        deobfuscate_env_file(args.input, args.mapping, output_file, args.password, args.app_key)
    else:
        output_file = args.output if args.output else f"{args.input}.{DEFAULT_OUTPUT_EXTENSION}"
        obfuscate_env_file(args.input, output_file, args.password, args.app_key)

if __name__ == "__main__":
    main()