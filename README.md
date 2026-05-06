# Encrypter

A powerful cross-platform tool to encrypt and decrypt entire folders. Available as both a CLI and a GUI application, compatible with Windows, Linux and macOS.

## How It Works

Encrypter uses **Fernet symmetric encryption** with **PBKDF2** password-based key derivation. When you encrypt a folder:

- Every file is encrypted and renamed to a random UUID with the `.enc` extension
- The original filenames are stored in an encrypted mapping file
- The mapping file and salt are automatically hidden from view
- Files are processed in **4KB chunks** to keep memory usage low regardless of file size
- Each chunk is **compressed with zlib before encryption**, reducing file sizes
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
or use the executables included in the releases

## Usage

### GUI

Run `gui-encryption.py` to open the graphical interface. Select a folder using the Browse button, enter your password, then click Encrypt or Decrypt. If you're encrypting, a window will pop up asking you to confirm your password. Confirm it and the files will be encrypted.

```bash
python gui-encryption.py
```

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

Current release: **v1.4.0**

## Links

- GitHub: [manupolice12-sketch/encrypter](https://github.com/manupolice12-sketch/encrypter)
- Bug Reports: [GitHub Issues](https://github.com/manupolice12-sketch/encrypter/issues)

## Warning

If you lose your password say goodbye to your files you encrypted as they are not recoverable.

**Death Zone Protection:** This version uses incremental file swapping — each file is encrypted and swapped individually rather than in a bulk operation. This reduces the death zone from the entire folder to just one file at a time (~1-5ms per file). If power is lost during encryption, only the current file being processed is at risk; all previously swapped files remain encrypted and recoverable with your password.

## Compatibility Notice

Files encrypted with versions prior to **v1.4.0** cannot be decrypted with this version due to the new chunk-based compression format. If you have files encrypted with an older version, decrypt them first before upgrading.

## Licence

This project is licensed under the GNU General Public Licence Version 3.

## Executable

Executables are available for all major platforms including Windows, Linux and macOS.

## Note for macOS Users

You may need to right-click the app and select "Open" the first time to bypass Gatekeeper and ensure the app has permission to access the folders you wish to encrypt.