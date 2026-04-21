from encrypter import Encryption
import getpass
import sys


def _progress(current: int, total: int, filename: str) -> None:
    bar_width = 30
    filled = int(bar_width * current / total)
    bar = '█' * filled + '░' * (bar_width - filled)
    percent = int(100 * current / total)
    label = filename if len(filename) <= 28 else filename[:25] + '...'
    print(f'\r  [{bar}] {percent:>3}%  {label:<28}', end='', flush=True)
    if current == total:
        print()


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
        if input("Are you sure? All files in the folder will be encrypted type y to continue") == "y":
           print("Encrypting...")
           tool.Encrypt(path, password, progress_callback=_progress)
           print("Files encrypted successfully.")
        else:
            sys.exit(1)
            
    elif command == "decrypt":
        path = input("Enter the directory path to decrypt files: ").strip()
        password = getpass.getpass("Enter password: ")
        try:
            print("Decrypting...")
            tool.Decrypt(path, password, progress_callback=_progress)
            print("Files decrypted successfully.")
        except (ValueError, FileNotFoundError) as e:
            print(e)
            sys.exit(1)

    else:
        print("Invalid command. Exiting.")
        sys.exit(1)


if __name__ == "__main__":
    main()