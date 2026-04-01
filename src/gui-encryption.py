import customtkinter as ctk
from tkinter import filedialog
from encrypter import Encryption

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

tool = Encryption()

window = ctk.CTk()
window.title("File Encrypter and Decrypter")
window.geometry("380x300")
window.resizable(False, False)

folder_frame = ctk.CTkFrame(window, fg_color="transparent")
folder_frame.pack(padx=20, pady=(20, 0), fill="x")
ctk.CTkLabel(folder_frame, text="Folder", anchor="w").pack(fill="x")
row = ctk.CTkFrame(folder_frame, fg_color="transparent")
row.pack(fill="x", pady=(4, 0))
path_entry = ctk.CTkEntry(row, placeholder_text="Select a folder...")
path_entry.pack(side="left", expand=True, fill="x", padx=(0, 8))

def browse():
    path = filedialog.askdirectory(title="Select Folder")
    if path:
        path_entry.delete(0, "end")
        path_entry.insert(0, path)

ctk.CTkButton(row, text="Browse", width=80, command=browse).pack(side="right")

pw_frame = ctk.CTkFrame(window, fg_color="transparent")
pw_frame.pack(padx=20, pady=(12, 0), fill="x")
ctk.CTkLabel(pw_frame, text="Password", anchor="w").pack(fill="x")
password_entry = ctk.CTkEntry(pw_frame, placeholder_text="Enter password...", show="*")
password_entry.pack(fill="x", pady=(4, 0))

confirm_frame = ctk.CTkFrame(window, fg_color="transparent")
confirm_frame.pack(padx=20, pady=(12, 0), fill="x")
ctk.CTkLabel(confirm_frame, text="Confirm Password", anchor="w").pack(fill="x")
confirm_entry = ctk.CTkEntry(confirm_frame, placeholder_text="Confirm password...", show="*")
confirm_entry.pack(fill="x", pady=(4, 0))

status_label = ctk.CTkLabel(window, text="", font=ctk.CTkFont(size=12))
status_label.pack(pady=(10, 0))

def set_status(message, color):
    status_label.configure(text=message, text_color=color)

def encrypt():
    path = path_entry.get().strip()
    password = password_entry.get()
    confirm = confirm_entry.get()
    if not path:
        set_status("Please select a folder.", "red")
        return
    if not password:
        set_status("Please enter a password.", "red")
        return
    if password != confirm:
        set_status("Passwords do not match.", "red")
        return
    try:
        tool.Encrypt(path, password)
        set_status("Files encrypted successfully.", "green")
        password_entry.delete(0, "end")
        confirm_entry.delete(0, "end")
    except Exception as e:
        set_status(f"Error: {e}", "red")

def decrypt():
    path = path_entry.get().strip()
    password = password_entry.get()
    if not path:
        set_status("Please select a folder.", "red")
        return
    if not password:
        set_status("Please enter a password.", "red")
        return
    try:
        tool.Decrypt(path, password)
        set_status("Files decrypted successfully.", "green")
        password_entry.delete(0, "end")
        confirm_entry.delete(0, "end")
    except ValueError as e:
        set_status(str(e), "red")
    except FileNotFoundError:
        set_status("No encrypted files found in this folder.", "red")
    except Exception as e:
        set_status(f"Error: {e}", "red")

btn_frame = ctk.CTkFrame(window, fg_color="transparent")
btn_frame.pack(padx=20, pady=(12, 0), fill="x")
ctk.CTkButton(btn_frame, text="Encrypt", fg_color="#1f6aa5", hover_color="#144f7a", command=encrypt).pack(side="left", expand=True, fill="x", padx=(0, 6))
ctk.CTkButton(btn_frame, text="Decrypt", fg_color="#2d6a2d", hover_color="#1e4d1e", command=decrypt).pack(side="right", expand=True, fill="x", padx=(6, 0))

window.mainloop()
