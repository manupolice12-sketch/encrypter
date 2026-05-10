# Encrypter

A powerful cross-platform tool to encrypt and decrypt entire folders. Available as both a CLI and a GUI application, compatible with Windows, Linux and macOS.

## How It Works

Encrypter uses **Fernet symmetric encryption** with **PBKDF2** password-based key derivation. When you encrypt a folder:

- Every file is encrypted and renamed to a random UUID with the `.enc` extension
- The original filenames are stored in an encrypted mapping file
- The mapping file and salt are automatically hidden from view
- Files are processed in **64 KB chunks** to keep memory usage low regardless of file size
- Each chunk is **compressed with zlib before encryption**, reducing file sizes
- Before decryption begins, all expected files are verified to exist on disk — if any are missing, the operation is aborted safely
- Subfolders are left untouched

Decrypting with the correct password restores everything exactly as it was.

## Security

| Property | Detail |
|---|---|
| Encryption | Fernet (AES-128-CBC + HMAC-SHA256) |
| Key derivation | PBKDF2-HMAC-SHA256 |
| KDF iterations | 600,000 (OWASP 2023 recommendation) |
| Salt | 16 bytes of `os.urandom()` per session |
| Minimum password length | 8 characters |

## Installation

```bash
pip install cryptography customtkinter
```

Then clone the repository:

```bash
git clone https://github.com/manupolice12-sketch/encrypter
```

Or use the executables included in the releases.

## Usage

### GUI

Run `gui-encryption.py` to open the graphical interface. Select a folder using the Browse button, enter your password, then click Encrypt or Decrypt. When encrypting, you will be asked to confirm your password and then confirm the operation before anything is changed.

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

Current release: **v1.5.0**

## Links

- GitHub: [manupolice12-sketch/encrypter](https://github.com/manupolice12-sketch/encrypter)
- Bug Reports: [GitHub Issues](https://github.com/manupolice12-sketch/encrypter/issues)

## Warning

If you lose your password, your files are not recoverable. There is no reset mechanism.

**Death Zone Protection:** Files are encrypted and swapped one at a time. If power is lost during encryption, only the file currently being processed is at risk — all previously processed files remain safely encrypted and recoverable with your password.

## Compatibility Notice

Files encrypted with versions prior to **v1.5.0** cannot be decrypted with this version due to the chunk-based compression format introduced in **v1.4.0** and as **v1.5.0** increased the **4 KB** chunk based encryption to **64 KB**. Decrypt those files first before upgrading.

## Licence

This project is licensed under the GNU General Public Licence Version 3.

## Executable

Executables are available for all major platforms including Windows, Linux and macOS.

## Note for macOS Users

You may need to right-click the app and select "Open" the first time to bypass Gatekeeper and ensure the app has permission to access the folders you wish to encrypt.
