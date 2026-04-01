from encrypter import Encryption
import getpass
import sys

def main():
    tool = Encryption()
    command = input("Enter 'encrypt' to encrypt files or 'decrypt' to decrypt files: ").strip().lower()

    if command == "encrypt":
        path = input("Enter the directory path to encrypt files: ").strip()
        password = getpass.getpass("Enter password: ")
        confirm = getpass.getpass("Confirm password: ")
        if password != confirm:
            print("Passwords do not match. Exiting.")
            sys.exit(1)
        tool.Encrypt(path, password)
        print("Files encrypted successfully.")

    elif command == "decrypt":
        path = input("Enter the directory path to decrypt files: ").strip()
        password = getpass.getpass("Enter password: ")
        try:
            tool.Decrypt(path, password)
            print("Files decrypted successfully.")
        except ValueError as e:
            print(e)
            sys.exit(1)

    else:
        print("Invalid command. Exiting.")
        sys.exit(1)

if __name__ == "__main__":
    main()
