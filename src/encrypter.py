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

# --- CONFIGURATION & CONSTANTS ---
# These variables define how the program recognizes its own system files.
SALT_FILE = 'salt.bin'
MAPPING_FILE = 'file_mapping.json'
ENC_EXTENSION = '.enc'
HEADER_SIZE = 4096 # We encrypt the first 4KB separately to handle large files efficiently.

# Handle hidden files differently based on the Operating System (Windows vs Linux/Mac)
if sys.platform != 'win32':
    HIDDEN_SALT = '.salt.bin'
    HIDDEN_MAPPING = '.file_mapping.json'
else:
    HIDDEN_SALT = SALT_FILE
    HIDDEN_MAPPING = MAPPING_FILE

SYSTEM_FILES = {SALT_FILE, MAPPING_FILE, HIDDEN_SALT, HIDDEN_MAPPING}


def _derive_key(password: str, salt: bytes) -> bytes:
    """
    Turns a human-readable password into a mathematically strong 32-byte key.
    
    Args:
        password: The string the user typed.
        salt: Random data that makes the key unique even if two users use the same password.
        
    Returns:
        A URL-safe base64 encoded key.
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000, # More iterations = harder for hackers to guess via brute force.
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))


def _encrypt_file_to(src: str, dst: str, fernet: Fernet) -> None:
    """
    Reads a file, encrypts its contents, and writes it to a new location.
    """
    with open(src, 'rb') as f:
        header = f.read(HEADER_SIZE)
        rest = f.read()

    encrypted_header = fernet.encrypt(header)
    encrypted_rest = fernet.encrypt(rest) if rest else b''
    
    # We store the length of the header so we know where it ends during decryption.
    header_len = len(encrypted_header).to_bytes(8, 'big')

    with open(dst, 'wb') as f:
        f.write(header_len)
        f.write(encrypted_header)
        f.write(encrypted_rest)


def _decrypt_file_to(src: str, dst: str, fernet: Fernet) -> None:
    """
    Reverses the encryption process to restore the original file.
    """
    with open(src, 'rb') as f:
        # Read the first 8 bytes to find out how long the encrypted header is.
        header_len = int.from_bytes(f.read(8), 'big')
        encrypted_header = f.read(header_len)
        encrypted_rest = f.read()

    decrypted_header = fernet.decrypt(encrypted_header)
    decrypted_rest = fernet.decrypt(encrypted_rest) if encrypted_rest else b''

    with open(dst, 'wb') as f:
        f.write(decrypted_header)
        f.write(decrypted_rest)


def _hide_files(path: str) -> None:
    """
    Hides the salt and mapping files so the folder looks clean.
    """
    if sys.platform == 'win32':
        # On Windows, we use the 'attrib' command to set hidden (+h) and system (+s) flags.
        for name in [SALT_FILE, MAPPING_FILE]:
            target = os.path.join(path, name)
            if os.path.exists(target):
                subprocess.run(['attrib', '+h', '+s', target], check=True)
    else:
        # On Linux/macOS, simply adding a dot '.' to the start of a filename hides it.
        for src, dst in [(SALT_FILE, HIDDEN_SALT), (MAPPING_FILE, HIDDEN_MAPPING)]:
            s = os.path.join(path, src)
            d = os.path.join(path, dst)
            if os.path.exists(s):
                os.rename(s, d)


def _show_files(path: str) -> None:
    """
    Makes system files visible again so the program can read them.
    """
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
    The main class used to manage the encryption and decryption of entire folders.
    """
    def __init__(self):
        self.key = None
        self.salt = None
        self.origin = {} # Stores 'Encrypted_Name: Original_Name' mapping.

    def Encrypt(self, path: str, password: str, progress_callback=None) -> None:
        """
        Encrypts all eligible files in a directory.
        
        Args:
            path: Folder to secure.
            password: Password to use for key derivation.
            progress_callback: A function to update a progress bar in the GUI.
        """
        path = os.path.abspath(path)

        # 1. Find all files that aren't already encrypted or part of the system.
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
        
        # 2. Setup security (Salt + Key)
        self.salt = os.urandom(16) # Generate 16 bytes of random 'salt'.
        self.key = _derive_key(password, self.salt)
        fernet = Fernet(self.key)


        # 3. Use a temporary directory for encrypted files
        work_dir = tempfile.mkdtemp(prefix='enc_work_', dir=path)

        try:
            # 4. Encrypt each file one by one, then immediately swap
            # This minimizes the death zone to just ONE file at a time
            for i, filename in enumerate(candidates):
                src = os.path.join(path, filename)
                enc_name = uuid.uuid4().hex + ENC_EXTENSION
                dst = os.path.join(work_dir, enc_name)
                
                # Encrypt to temp location
                _encrypt_file_to(src, dst, fernet)
                self.origin[enc_name] = filename

                # Only now delete original and move encrypted file into place
                # Death zone: only this ONE file is at risk during the swap
                os.remove(src)
                shutil.move(dst, os.path.join(path, enc_name))

                if progress_callback:
                    progress_callback(i + 1, total, filename)

            # 5. Save the mapping and salt AFTER all files are safely encrypted
            mapping_json = json.dumps(self.origin)
            encrypted_mapping = fernet.encrypt(mapping_json.encode())

            salt_path = os.path.join(path, SALT_FILE)
            mapping_path = os.path.join(path, MAPPING_FILE)

            with open(salt_path, 'wb') as f:
                f.write(self.salt)
            with open(mapping_path, 'wb') as f:
                f.write(encrypted_mapping)

        except Exception as e:
            # If anything fails, try to recover remaining originals
            # Note: Files already swapped are lost, but remaining originals survive
            shutil.rmtree(work_dir, ignore_errors=True)
            raise

        shutil.rmtree(work_dir, ignore_errors=True)
        _hide_files(path)

    def Decrypt(self, path: str, password: str, progress_callback=None) -> None:
        """
        Decrypts files and restores their original names.
        """
        path = os.path.abspath(path)

        _show_files(path)

        salt_path = os.path.join(path, SALT_FILE)
        mapping_path = os.path.join(path, MAPPING_FILE)

        if not os.path.exists(salt_path) or not os.path.exists(mapping_path):
            raise FileNotFoundError("No encrypted files found in this folder.")

        # 1. Load the salt and reconstruct the key.
        with open(salt_path, 'rb') as f:
            salt = f.read(16)

        key = _derive_key(password, salt)
        fernet = Fernet(key)

        # 2. Try to decrypt the mapping file. If this fails, the password is wrong.
        try:
            with open(mapping_path, 'rb') as f:
                encrypted_mapping = f.read()
            origin = json.loads(fernet.decrypt(encrypted_mapping).decode())
        except Exception:
            _hide_files(path) # Hide files again before exiting.
            raise ValueError("Incorrect password.")

        total = len(origin)
        work_dir = tempfile.mkdtemp(prefix='dec_work_', dir=path)

        try:
            # 3. Decrypt and swap one file at a time (minimizes death zone)
            for i, (enc_name, orig_name) in enumerate(origin.items()):
                src = os.path.join(path, enc_name)
                dst = os.path.join(work_dir, orig_name)
                
                if os.path.exists(src):
                    # Decrypt to temp location
                    _decrypt_file_to(src, dst, fernet)
                    
                    # Delete encrypted file and move decrypted file into place
                    # Death zone: only this ONE file is at risk during the swap
                    os.remove(src)
                    shutil.move(dst, os.path.join(path, orig_name))

                if progress_callback:
                    progress_callback(i + 1, total, orig_name)

        except Exception as e:
            shutil.rmtree(work_dir, ignore_errors=True)
            raise

        shutil.rmtree(work_dir, ignore_errors=True)
        os.remove(salt_path)
        os.remove(mapping_path)