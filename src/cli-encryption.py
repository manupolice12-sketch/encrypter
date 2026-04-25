"""
COMMAND LINE INTERFACE (CLI)
----------------------------
A lightweight terminal version of the Encrypter.
This version is faster for power users and perfect for learning how 
input/output works in a non-graphical environment.
"""

from encrypter import Encryption
import getpass # Used to hide the password as you type it
import sys


def _progress(current: int, total: int, filename: str) -> None:
    """
    Creates a visual progress bar in the terminal.
    
    Args:
        current: Number of files processed.
        total: Total number of files.
        filename: The name of the file currently being handled.
    """
    bar_width = 30
    filled = int(bar_width * current / total)
    
    # Using '█' for the filled part and '░' for the empty part
    bar = '█' * filled + '░' * (bar_width - filled)
    percent = int(100 * current / total)
    
    # If the filename is too long, we cut it off so it doesn't break the bar line
    label = filename if len(filename) <= 28 else filename[:25] + '...'
    
    # '\r' is the "Carriage Return" - it moves the cursor back to the start 
    # of the line so we can overwrite it instead of printing a new line every time.
    print(f'\r  [{bar}] {percent:>3}%  {label:<28}', end='', flush=True)
    
    # When finished, move the cursor to a new line
    if current == total:
        print()


def main():
    """The main control loop for the CLI tool."""
    tool = Encryption()
    
    print("=== File Encrypter CLI ===")
    command = input("Enter 'encrypt' or 'decrypt': ").strip().lower()

    if command == "encrypt":
        path = input("Enter the directory path: ").strip()
        
        # getpass.getpass() hides the user's input so bystanders can't see the password
        password = getpass.getpass("Enter password: ")
        confirm = getpass.getpass("Confirm password: ")
        
        if password != confirm:
            print("Error: Passwords do not match. Exiting.")
            sys.exit(1)
            
        # Security warning for the user
        warning = input("Warning: All files in this folder will be transformed. Continue? (y/n): ")
        if warning.lower() == "y":    
           print("Processing...")
           try:
               if tool.backup_possible == False:
                  Resource_command = input("You don't have enough space to create a backup for your folder. Continue? (y/n)")
                  if Resource_command.lower().strip() == "y":
                     tool.Encrypt(path, password, progress_callback=_progress)
                     print("Done! Files encrypted successfully.")
                  else:
                      print("Operation cancelled.")
                      sys.exit(1) 
               else:
                     tool.Encrypt(path, password, progress_callback=_progress)
                     print("Done! Files encrypted successfully.")      
           except Exception as e:
               print(f"Failed: {e}")
        else:
            print("Operation cancelled.")
            sys.exit(1)
            
    elif command == "decrypt":
        path = input("Enter the directory path: ").strip()
        password = getpass.getpass("Enter password: ")
        
        try:
            print("Processing...")
            tool.Decrypt(path, password, progress_callback=_progress)
            print("Done! Files decrypted successfully.")
        except (ValueError, FileNotFoundError) as e:
            # We catch common errors (like wrong password) and show them nicely
            print(f"Error: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            sys.exit(1)

    else:
        print("Invalid command. Please use 'encrypt' or 'decrypt'.")
        sys.exit(1)


# This check ensures main() only runs if the script is executed directly, 
# not if it's imported into another file.
if __name__ == "__main__":
    main()