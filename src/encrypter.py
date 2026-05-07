"""
CORE ENCRYPTION ENGINE
----------------------
This module handles the heavy lifting of securing your files.
It uses 'Fernet' (Symmetric encryption) and PBKDF2 (Password-based key derivation)
to ensure that files are unreadable without the correct password.
"""
# Fernet uses AES-128 in CBC mode with an HMAC for authentication.
# This ensures that files cannot be tampered with while encrypted.
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import json
import os
import shutil
import sys
import subprocess
import tempfile
import uuid
import zlib

# --- CONFIGURATION & CONSTANTS ---
SALT_FILE = 'salt.bin'
MAPPING_FILE = 'file_mapping.json'
ENC_EXTENSION = '.enc'
CHUNK_SIZE = 65536  # 64 KB — large enough to amortise Fernet overhead per token

# Minimum password requirements
MIN_PASSWORD_LENGTH = 8

# PBKDF2 iteration count. 600 000 is the OWASP 2023 recommendation for SHA-256.
PBKDF2_ITERATIONS = 600_000

# Handle hidden files differently based on the Operating System
if sys.platform != 'win32':
    HIDDEN_SALT = '.salt.bin'
    HIDDEN_MAPPING = '.file_mapping.json'
else:
    HIDDEN_SALT = SALT_FILE
    HIDDEN_MAPPING = MAPPING_FILE

SYSTEM_FILES = {SALT_FILE, MAPPING_FILE, HIDDEN_SALT, HIDDEN_MAPPING}


def validate_password(password: str) -> None:
    """
    Raise ValueError if the password does not meet minimum requirements.

    Args:
        password: The password string to check.

    Raises:
        ValueError: If the password is too short.
    """
    if len(password) < MIN_PASSWORD_LENGTH:
        raise ValueError(
            f"Password must be at least {MIN_PASSWORD_LENGTH} characters long."
        )


def _derive_key(password: str, salt: bytes) -> bytes:
    """
    Turns a human-readable password into a mathematically strong 32-byte key.

    Args:
        password: The string the user typed.
        salt: Random bytes that make the key unique even for identical passwords.

    Returns:
        A URL-safe base64 encoded key suitable for Fernet.
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=PBKDF2_ITERATIONS,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))


def _encrypt_file_to(src: str, dst: str, fernet: Fernet) -> None:
    """
    Reads a file, compresses and encrypts its contents in chunks,
    and writes the result to dst.

    Each chunk is prefixed with a 4-byte big-endian length so the decoder
    knows how many bytes to read for each Fernet token.
    """
    with open(src, 'rb') as f_in, open(dst, 'wb') as f_out:
        while True:
            chunk = f_in.read(CHUNK_SIZE)
            if not chunk:
                break
            compressed_chunk = zlib.compress(chunk)
            encrypted_chunk = fernet.encrypt(compressed_chunk)
            f_out.write(len(encrypted_chunk).to_bytes(4, 'big'))
            f_out.write(encrypted_chunk)


def _decrypt_file_to(src: str, dst: str, fernet: Fernet) -> None:
    """
    Reverses the encryption process to restore the original file.
    """
    with open(src, 'rb') as f_in, open(dst, 'wb') as f_out:
        while True:
            length_bytes = f_in.read(4)
            if not length_bytes:
                break
            chunk_len = int.from_bytes(length_bytes, 'big')
            encrypted_chunk = f_in.read(chunk_len)
            compressed_chunk = fernet.decrypt(encrypted_chunk)
            f_out.write(zlib.decompress(compressed_chunk))


def _hide_files(path: str) -> None:
    """Hides the salt and mapping files so the folder looks clean."""
    if sys.platform == 'win32':
        for name in [SALT_FILE, MAPPING_FILE]:
            target = os.path.join(path, name)
            if os.path.exists(target):
                subprocess.run(['attrib', '+h', '+s', target], check=True)
    else:
        for src, dst in [(SALT_FILE, HIDDEN_SALT), (MAPPING_FILE, HIDDEN_MAPPING)]:
            s = os.path.join(path, src)
            d = os.path.join(path, dst)
            if os.path.exists(s):
                os.rename(s, d)


def _show_files(path: str) -> None:
    """Makes system files visible again so the program can read them."""
    if sys.platform == 'win32':
        for name in [SALT_FILE, MAPPING_FILE]:
            target = os.path.join(path, name)
            if os.path.exists(target):
                subprocess.run(['attrib', '-h', '-s', target], check=True)
    else:
        for src, dst in [(HIDDEN_SALT, SALT_FILE), (HIDDEN_MAPPING, MAPPING_FILE)]:
            s = os.path.join(path, src)
            d = os.path.join(path, dst)
            if os.path.exists(s):
                os.rename(s, d)


class Encryption:
    """
    Manages encryption and decryption of all eligible files in a folder.

    Each instance is stateless between operations — it is safe to reuse
    the same instance for multiple Encrypt / Decrypt calls.
    """

    def __init__(self):
        self.key = None
        self.salt = None
        self.origin = {}  # {encrypted_name: original_name}

    def Encrypt(self, path: str, password: str, progress_callback=None) -> None:
        """
        Encrypts all eligible files in a directory.

        Args:
            path: Folder to secure.
            password: Password to use for key derivation.
            progress_callback: Optional function(current, total, filename).

        Raises:
            ValueError: If the password is too short or no eligible files exist.
        """
        validate_password(password)
        path = os.path.abspath(path)

        candidates = [
            f for f in os.listdir(path)
            if os.path.isfile(os.path.join(path, f))
            and f not in SYSTEM_FILES
            and not f.endswith(ENC_EXTENSION)
        ]

        if not candidates:
            raise ValueError("No eligible files found to encrypt.")

        total = len(candidates)
        self.origin = {}

        self.salt = os.urandom(16)
        self.key = _derive_key(password, self.salt)
        fernet = Fernet(self.key)

        # Temp dir on the same filesystem ensures shutil.move is an atomic rename.
        work_dir = tempfile.mkdtemp(prefix='enc_work_', dir=path)

        try:
            for i, filename in enumerate(candidates):
                src = os.path.join(path, filename)
                enc_name = uuid.uuid4().hex + ENC_EXTENSION
                dst = os.path.join(work_dir, enc_name)

                _encrypt_file_to(src, dst, fernet)
                self.origin[enc_name] = filename

                # Original is removed only after the encrypted copy exists
                # safely in the temp dir — only one file is at risk at a time.
                os.remove(src)
                shutil.move(dst, os.path.join(path, enc_name))

                if progress_callback:
                    progress_callback(i + 1, total, filename)

            # Persist mapping and salt only after all files are safely swapped.
            mapping_json = json.dumps(self.origin)
            encrypted_mapping = fernet.encrypt(mapping_json.encode())

            with open(os.path.join(path, SALT_FILE), 'wb') as f:
                f.write(self.salt)
            with open(os.path.join(path, MAPPING_FILE), 'wb') as f:
                f.write(encrypted_mapping)

        except Exception:
            shutil.rmtree(work_dir, ignore_errors=True)
            raise

        shutil.rmtree(work_dir, ignore_errors=True)
        _hide_files(path)

    def Decrypt(self, path: str, password: str, progress_callback=None) -> None:
        """
        Decrypts files and restores their original names.

        Args:
            path: Folder to restore.
            password: Password used during encryption.
            progress_callback: Optional function(current, total, filename).

        Raises:
            FileNotFoundError: If no encrypted session is found, or files are missing.
            ValueError: If the password is incorrect.
        """
        path = os.path.abspath(path)
        _show_files(path)

        salt_path = os.path.join(path, SALT_FILE)
        mapping_path = os.path.join(path, MAPPING_FILE)

        if not os.path.exists(salt_path) or not os.path.exists(mapping_path):
            raise FileNotFoundError("No encrypted files found in this folder.")

        with open(salt_path, 'rb') as f:
            salt = f.read(16)

        key = _derive_key(password, salt)
        fernet = Fernet(key)

        # Decrypt the mapping first — wrong password raises here before any
        # files are touched.
        try:
            with open(mapping_path, 'rb') as f:
                encrypted_mapping = f.read()
            origin = json.loads(fernet.decrypt(encrypted_mapping).decode())
        except Exception:
            _hide_files(path)
            raise ValueError("Incorrect password.")

        # Verify all expected files are present before modifying anything.
        missing = [enc for enc in origin if not os.path.exists(os.path.join(path, enc))]
        if missing:
            _hide_files(path)
            raise FileNotFoundError(
                f"{len(missing)} encrypted file(s) listed in the mapping are "
                "missing from the folder. The folder may have been modified."
            )

        total = len(origin)
        work_dir = tempfile.mkdtemp(prefix='dec_work_', dir=path)

        try:
            for i, (enc_name, orig_name) in enumerate(origin.items()):
                src = os.path.join(path, enc_name)
                dst = os.path.join(work_dir, orig_name)

                _decrypt_file_to(src, dst, fernet)
                os.remove(src)
                shutil.move(dst, os.path.join(path, orig_name))

                if progress_callback:
                    progress_callback(i + 1, total, orig_name)

        except Exception:
            shutil.rmtree(work_dir, ignore_errors=True)
            raise

        shutil.rmtree(work_dir, ignore_errors=True)
        os.remove(salt_path)
        os.remove(mapping_path)
