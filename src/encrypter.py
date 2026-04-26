"""
CORE ENCRYPTION ENGINE
----------------------
This module handles the heavy lifting of securing your files. 
It uses 'Fernet' (Symmetric encryption) and PBKDF2 (Password-based key derivation)
to ensure that files are unreadable without the correct password.
"""
# Fernet uses AES-128 in CBC mode with HMAC
# This ensures your files are not tampered with
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import json
import os
import shutil
import sys
import tempfile
import uuid

# --- CONFIGURATION & CONSTANTS ---
SALT_FILE = 'salt.bin'
MAPPING_FILE = 'file_mapping.json'
ENC_EXTENSION = '.enc'
HEADER_SIZE = 4096 

if sys.platform != 'win32':
    HIDDEN_SALT = '.salt.bin'
    HIDDEN_MAPPING = '.file_mapping.json'
else:
    HIDDEN_SALT = SALT_FILE
    HIDDEN_MAPPING = MAPPING_FILE

SYSTEM_FILES = {SALT_FILE, MAPPING_FILE, HIDDEN_SALT, HIDDEN_MAPPING}

def _derive_key(password: str, salt: bytes) -> bytes:
    """Derives a secure 32-byte key from a password and salt."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))

def _hide_files(path):
    """Hides system files using OS-specific commands."""
    if sys.platform == 'win32':
        for f in [SALT_FILE, MAPPING_FILE]:
            p = os.path.join(path, f)
            if os.path.exists(p):
                os.system(f'attrib +h +s "{p}"')

def _encrypt_file_to(src, dst, fernet):
    """Encrypts the header of a file and streams the rest to a destination."""
    with open(src, 'rb') as f_in, open(dst, 'wb') as f_out:
        header = f_in.read(HEADER_SIZE)
        if header:
            f_out.write(fernet.encrypt(header))
        shutil.copyfileobj(f_in, f_out)

def _decrypt_file_to(src, dst, fernet):
    """Decrypts a file header and reconstructs the original file."""
    with open(src, 'rb') as f_in, open(dst, 'wb') as f_out:
        full_data = f_in.read()
        # Find the end of the Fernet token (always ends in '=')
        split_point = full_data.find(b'=', 0, 8192) + 1
        header = full_data[:split_point]
        body = full_data[split_point:]
        
        f_out.write(fernet.decrypt(header))
        f_out.write(body)

class Encryption:
    def __init__(self):
        self.backup_possible = False

    def check_backup_feasibility(self, path):
        """Calculates folder size vs free disk space to see if a backup can be made."""
        total_size = 0
        for dirpath, _, filenames in os.walk(path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                if not os.path.islink(fp):
                    total_size += os.path.getsize(fp)
        
        _, _, free = shutil.disk_usage(os.path.abspath(path))
        # Require folder size + 100MB buffer
        self.backup_possible = free > (total_size + 104857600)
        return self.backup_possible

    def Encrypt(self, path, password, progress_callback=None):
        """Encrypts all files in a folder, renames them to UUIDs, and creates a mapping."""
        if self.backup_possible:
            backup_path = f"{path}-Backup"
            if os.path.exists(backup_path):
                shutil.rmtree(backup_path)
            shutil.copytree(path, backup_path)

        salt = os.urandom(16)
        with open(os.path.join(path, SALT_FILE), 'wb') as f:
            f.write(salt)

        key = _derive_key(password, salt)
        fernet = Fernet(key)

        files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)) and f not in SYSTEM_FILES]
        mapping = {}
        work_dir = tempfile.mkdtemp(prefix='enc_work_', dir=path)

        try:
            for i, filename in enumerate(files):
                src = os.path.join(path, filename)
                enc_name = uuid.uuid4().hex + ENC_EXTENSION
                dst = os.path.join(work_dir, enc_name)
                
                _encrypt_file_to(src, dst, fernet)
                mapping[enc_name] = filename
                
                if progress_callback:
                    progress_callback(i + 1, len(files), filename)

            # Save the encrypted mapping file
            with open(os.path.join(path, MAPPING_FILE), 'wb') as f:
                f.write(fernet.encrypt(json.dumps(mapping).encode()))

            # Finalize: Remove originals and move encrypted files into place
            for f in files:
                os.remove(os.path.join(path, f))
            for f in os.listdir(work_dir):
                shutil.move(os.path.join(work_dir, f), os.path.join(path, f))

            _hide_files(path)
            if self.backup_possible:
                shutil.rmtree(f"{path}-Backup")

        finally:
            shutil.rmtree(work_dir, ignore_errors=True)

    def Decrypt(self, path, password, progress_callback=None):
        """Restores files to their original names using the mapping and password."""
        salt_p = os.path.join(path, HIDDEN_SALT)
        map_p = os.path.join(path, HIDDEN_MAPPING)

        if not os.path.exists(salt_p) or not os.path.exists(map_p):
            raise FileNotFoundError("Decryption system files are missing.")

        with open(salt_p, 'rb') as f:
            salt = f.read()

        key = _derive_key(password, salt)
        fernet = Fernet(key)

        try:
            with open(map_p, 'rb') as f:
                origin = json.loads(fernet.decrypt(f.read()).decode())
        except Exception:
            raise ValueError("Incorrect password.")

        work_dir = tempfile.mkdtemp(prefix='dec_work_', dir=path)
        try:
            items = list(origin.items())
            for i, (enc, orig) in enumerate(items):
                src = os.path.join(path, enc)
                if os.path.exists(src):
                    _decrypt_file_to(src, os.path.join(work_dir, orig), fernet)
                if progress_callback:
                    progress_callback(i + 1, len(items), orig)

            # Cleanup and restore
            for enc in origin:
                p = os.path.join(path, enc)
                if os.path.exists(p): os.remove(p)
            
            os.remove(salt_p)
            os.remove(map_p)

            for f in os.listdir(work_dir):
                shutil.move(os.path.join(work_dir, f), os.path.join(path, f))
        finally:
            shutil.rmtree(work_dir, ignore_errors=True)