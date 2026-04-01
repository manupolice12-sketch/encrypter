from .encrypter import Encryption
import sys
tool = Encryption()
command = input("Enter 'encrypt' to encrypt files or 'decrypt' to decrypt files: ").strip().lower()
if command == "encrypt":
    path = input("Enter the directory path to encrypt files: ").strip()
    tool.Encrypt(path)
elif command == "decrypt":
    path = input("Enter the directory path to decrypt files: ").strip()
    tool.Decrypt(path)
else:
    print("Invalid command. Exiting.")
    sys.exit(1)