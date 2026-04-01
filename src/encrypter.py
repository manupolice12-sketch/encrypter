from cryptography.fernet import Fernet
import os
import json
import sys
import subprocess
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import uuid

SALT_FILE = 'salt.bin'
MAPPING_FILE = 'file_mapping.json'

if sys.platform != 'win32':
    HIDDEN_SALT = '.salt.bin'
    HIDDEN_MAPPING = '.file_mapping.json'
else:
    HIDDEN_SALT = SALT_FILE
    HIDDEN_MAPPING = MAPPING_FILE

class Encryption:
    def __init__(self):
        self.key = None
        self.salt = None
        self.origin = {}

    def Encrypt(self, path, password):
        os.chdir(path)
        self.origin = {}
        self.salt = os.urandom(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=100000,
        )
        self.key = base64.urlsafe_b64encode(kdf.derive(password.encode()))

        for file in os.listdir():
            if os.path.isdir(file):
                continue
            if file in [SALT_FILE, MAPPING_FILE, HIDDEN_SALT, HIDDEN_MAPPING]:
                continue
            name = uuid.uuid4().hex
            with open(file, 'rb') as f:
                data = f.read()
            fernet = Fernet(self.key)
            encrypted = fernet.encrypt(data)
            with open(name, 'wb') as f:
                f.write(encrypted)
            os.remove(file)
            self.origin[name] = file

        self.SaveKeyAndMapping()
        self.hide_files()

    def SaveKeyAndMapping(self):
        with open(SALT_FILE, 'wb') as f:
            f.write(self.salt)
        mapping_json = json.dumps(self.origin)
        fernet = Fernet(self.key)
        encrypted_mapping = fernet.encrypt(mapping_json.encode())
        with open(MAPPING_FILE, 'wb') as f:
            f.write(encrypted_mapping)

    def hide_files(self):
        if sys.platform == 'win32':
            for f in [SALT_FILE, MAPPING_FILE]:
                subprocess.run(['attrib', '+h', '+s', f], check=True)
        else:
            if os.path.exists(SALT_FILE):
                os.rename(SALT_FILE, HIDDEN_SALT)
            if os.path.exists(MAPPING_FILE):
                os.rename(MAPPING_FILE, HIDDEN_MAPPING)

    def show_files(self):
        if sys.platform == 'win32':
            for f in [SALT_FILE, MAPPING_FILE]:
                if os.path.exists(f):
                    subprocess.run(['attrib', '-h', '-s', f], check=True)
        else:
            if os.path.exists(HIDDEN_SALT):
                os.rename(HIDDEN_SALT, SALT_FILE)
            if os.path.exists(HIDDEN_MAPPING):
                os.rename(HIDDEN_MAPPING, MAPPING_FILE)

    def Decrypt(self, path, password):
        os.chdir(path)
        self.show_files()

        with open(SALT_FILE, 'rb') as f:
            salt = f.read()

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        fernet = Fernet(key)

        try:
            with open(MAPPING_FILE, 'rb') as f:
                encrypted_mapping = f.read()
            decrypted_mapping = fernet.decrypt(encrypted_mapping).decode()
            origin = json.loads(decrypted_mapping)
        except Exception:
            self.hide_files()
            raise ValueError("Incorrect password.")

        for enc_name, orig_name in origin.items():
            with open(enc_name, 'rb') as f:
                encrypted_data = f.read()
            decrypted = fernet.decrypt(encrypted_data)
            with open(orig_name, 'wb') as f:
                f.write(decrypted)
            os.remove(enc_name)

        os.remove(SALT_FILE)
        os.remove(MAPPING_FILE)
