# Encrypter

A powerful cross-platform tool to encrypt and decrypt entire folders. Available as both a CLI and a GUI application, compatible with Windows, Linux and macOS.

## How It Works

Encrypter uses **Fernet symmetric encryption** with **PBKDF2** password-based key derivation. When you encrypt a folder:

- Every file is encrypted and renamed to a random UUID with no extension
- The original filenames are stored in an encrypted mapping file
- The mapping file and salt are automatically hidden from view
- Subfolders are left untouched

Decrypting with the correct password restores everything exactly as it was.

## Installation

```bash
pip install cryptography customtkinter
```

Then clone the repository:

```bash
git clone https://github.com/manupolice12-sketch/encrypter
```

## Usage

### GUI

Run `gui-encryption.py` to open the graphical interface. Select a folder using the Browse button, enter and confirm your password, then click Encrypt or Decrypt.

### CLI

Run `cli-encryption.py` from the terminal. You will be prompted to choose encrypt or decrypt, enter the folder path, and enter your password.

```bash
python cli-encryption.py
```

## Platform Support

| Platform | File Hiding Method |
|---|---|
| Windows | `attrib +h +s` (Hidden + System attributes) |
| Linux / macOS | Dot-prefix rename (e.g. `.salt.bin`) |

## Version

Current release: **v1.0.0**

## Links

- GitHub: [manupolice12-sketch/encrypter](https://github.com/manupolice12-sketch/encrypter)
- Bug Reports: [GitHub Issues](https://github.com/manupolice12-sketch/encrypter/issues)
 
## Warning 

If you lose your password say goodbye to your files you encrypted as they are not recoverable.

## Licence

This project is Licenced under the GNU General Public Licence Version 3

## Executable

Inside the dist folder you will find an executable for windows soon one for Linux and MacOS will come and if your running it please click run anyway when Windows Defender SmartScreen says unknown publisher or use the encrypter-setup.exe and install the app