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
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))


def _encrypt_file_to(src: str, dst: str, fernet: Fernet) -> None:
    with open(src, 'rb') as f:
        header = f.read(HEADER_SIZE)
        rest = f.read()

    encrypted_header = fernet.encrypt(header)
    encrypted_rest = fernet.encrypt(rest) if rest else b''
    header_len = len(encrypted_header).to_bytes(8, 'big')

    with open(dst, 'wb') as f:
        f.write(header_len)
        f.write(encrypted_header)
        f.write(encrypted_rest)


def _decrypt_file_to(src: str, dst: str, fernet: Fernet) -> None:
    with open(src, 'rb') as f:
        header_len = int.from_bytes(f.read(8), 'big')
        encrypted_header = f.read(header_len)
        encrypted_rest = f.read()

    decrypted_header = fernet.decrypt(encrypted_header)
    decrypted_rest = fernet.decrypt(encrypted_rest) if encrypted_rest else b''

    with open(dst, 'wb') as f:
        f.write(decrypted_header)
        f.write(decrypted_rest)


def _hide_files(path: str) -> None:
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
    def __init__(self):
        self.key = None
        self.salt = None
        self.origin = {}

    def Encrypt(self, path: str, password: str, progress_callback=None) -> None:
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

        work_dir = tempfile.mkdtemp(prefix='enc_work_', dir=path)

        try:
            for i, filename in enumerate(candidates):
                src = os.path.join(path, filename)
                enc_name = uuid.uuid4().hex + ENC_EXTENSION
                dst = os.path.join(work_dir, enc_name)
                _encrypt_file_to(src, dst, fernet)
                self.origin[enc_name] = filename

                if progress_callback:
                    progress_callback(i + 1, total, filename)

            salt_path = os.path.join(work_dir, SALT_FILE)
            with open(salt_path, 'wb') as f:
                f.write(self.salt)

            mapping_json = json.dumps(self.origin)
            encrypted_mapping = fernet.encrypt(mapping_json.encode())
            mapping_path = os.path.join(work_dir, MAPPING_FILE)
            with open(mapping_path, 'wb') as f:
                f.write(encrypted_mapping)

            for filename in candidates:
                os.remove(os.path.join(path, filename))

            for item in os.listdir(work_dir):
                shutil.move(os.path.join(work_dir, item), os.path.join(path, item))

        except Exception:
            shutil.rmtree(work_dir, ignore_errors=True)
            raise

        shutil.rmtree(work_dir, ignore_errors=True)
        _hide_files(path)

    def Decrypt(self, path: str, password: str, progress_callback=None) -> None:
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

        try:
            with open(mapping_path, 'rb') as f:
                encrypted_mapping = f.read()
            origin = json.loads(fernet.decrypt(encrypted_mapping).decode())
        except Exception:
            _hide_files(path)
            raise ValueError("Incorrect password.")

        total = len(origin)
        work_dir = tempfile.mkdtemp(prefix='dec_work_', dir=path)

        try:
            for i, (enc_name, orig_name) in enumerate(origin.items()):
                src = os.path.join(path, enc_name)
                dst = os.path.join(work_dir, orig_name)
                if os.path.exists(src):
                    _decrypt_file_to(src, dst, fernet)

                if progress_callback:
                    progress_callback(i + 1, total, orig_name)

            for enc_name in origin:
                enc_path = os.path.join(path, enc_name)
                if os.path.exists(enc_path):
                    os.remove(enc_path)

            for item in os.listdir(work_dir):
                shutil.move(os.path.join(work_dir, item), os.path.join(path, item))

        except Exception:
            shutil.rmtree(work_dir, ignore_errors=True)
            raise

        shutil.rmtree(work_dir, ignore_errors=True)
        os.remove(salt_path)
        os.remove(mapping_path)
