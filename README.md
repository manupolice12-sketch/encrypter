# Encrypter

A powerful cross-platform tool to encrypt and decrypt entire folders. Available as both a CLI and a GUI application, compatible with Windows, Linux and macOS.

## How It Works

Encrypter uses **Fernet symmetric encryption** with **PBKDF2** password-based key derivation. When you encrypt a folder:

- Every file is encrypted and renamed to a random UUID with the enc extension
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
or use the executables included in the releases

## Usage

### GUI

Run `gui-encryption.py` to open the graphical interface. Select a folder using the Browse button, enter your password, then click Encrypt or Decrypt If your encrypting a window will popup asking you to confirm you passsowrd confirm it and The files will be encrypted.

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

Current release: **v1.2.0**

## Links

- GitHub: [manupolice12-sketch/encrypter](https://github.com/manupolice12-sketch/encrypter)
- Bug Reports: [GitHub Issues](https://github.com/manupolice12-sketch/encrypter/issues)
 
## Warning 

If you lose your password say goodbye to your files you encrypted as they are not recoverable and while this tool is designed for high reliability, there is a theoretical "death zone" of approximately 1–5 milliseconds during the final file swap. If the system suffers a total power failure at the exact moment the original is deleted but before the encrypted version is moved into place, data loss could occur so make sure when encrypting you have a stable power source.

## Licence

This project is Licenced under the GNU General Public Licence Version 3

## Executable

As of know this project's executables are finally there for all major platforms including Windows, Linux and MacOS

## Note for MacOS users
  
 You may need to right-click the app and select "Open" the first time to bypass Gatekeeper and ensure the app has permission to access the folders you wish to encrypt  


