import threading
import customtkinter as ctk
from tkinter import filedialog
from encrypter import Encryption

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

tool = Encryption()

window = ctk.CTk()
window.title("File Encrypter and Decrypter")
window.geometry("420x400")
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

progress_bar = ctk.CTkProgressBar(window, width=380)
progress_bar.pack(padx=20, pady=(14, 0), fill="x")
progress_bar.set(0)

file_label = ctk.CTkLabel(window, text="", font=ctk.CTkFont(size=11), text_color="gray")
file_label.pack(pady=(4, 0))

status_label = ctk.CTkLabel(window, text="", font=ctk.CTkFont(size=12))
status_label.pack(pady=(6, 0))

btn_frame = ctk.CTkFrame(window, fg_color="transparent")
btn_frame.pack(padx=20, pady=(12, 0), fill="x")
encrypt_btn = ctk.CTkButton(btn_frame, text="Encrypt", fg_color="#1f6aa5", hover_color="#144f7a")
encrypt_btn.pack(side="left", expand=True, fill="x", padx=(0, 6))
decrypt_btn = ctk.CTkButton(btn_frame, text="Decrypt", fg_color="#2d6a2d", hover_color="#1e4d1e")
decrypt_btn.pack(side="right", expand=True, fill="x", padx=(6, 0))


def set_status(message, color):
    status_label.configure(text=message, text_color=color)


def set_buttons_enabled(enabled: bool):
    state = "normal" if enabled else "disabled"
    encrypt_btn.configure(state=state)
    decrypt_btn.configure(state=state)


def make_progress_callback():
    def callback(current: int, total: int, filename: str):
        value = current / total
        progress_bar.set(value)
        label = filename if len(filename) <= 38 else filename[:35] + '...'
        file_label.configure(text=label)
        window.update_idletasks()
    return callback


def reset_progress():
    progress_bar.set(0)
    file_label.configure(text="")


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

    set_buttons_enabled(False)
    reset_progress()
    set_status("Encrypting...", "gray")

    def run():
        try:
            tool.Encrypt(path, password, progress_callback=make_progress_callback())
            window.after(0, lambda: set_status("Files encrypted successfully.", "green"))
            window.after(0, lambda: password_entry.delete(0, "end"))
            window.after(0, lambda: confirm_entry.delete(0, "end"))
        except Exception as e:
            msg = f"Error: {e}"
            window.after(0, lambda m=msg: set_status(m, "red"))
        finally:
            window.after(0, lambda: set_buttons_enabled(True))
            window.after(0, lambda: file_label.configure(text=""))

    threading.Thread(target=run, daemon=True).start()


def decrypt():
    path = path_entry.get().strip()
    password = password_entry.get()
    if not path:
        set_status("Please select a folder.", "red")
        return
    if not password:
        set_status("Please enter a password.", "red")
        return

    set_buttons_enabled(False)
    reset_progress()
    set_status("Decrypting...", "gray")

    def run():
        try:
            tool.Decrypt(path, password, progress_callback=make_progress_callback())
            window.after(0, lambda: set_status("Files decrypted successfully.", "green"))
            window.after(0, lambda: password_entry.delete(0, "end"))
            window.after(0, lambda: confirm_entry.delete(0, "end"))
        except ValueError as e:
            msg = str(e)
            window.after(0, lambda m=msg: set_status(m, "red"))
        except FileNotFoundError as e:
            msg = str(e)
            window.after(0, lambda m=msg: set_status(m, "red"))
        except Exception as e:
            msg = f"Error: {e}"
            window.after(0, lambda m=msg: set_status(m, "red"))
        finally:
            window.after(0, lambda: set_buttons_enabled(True))
            window.after(0, lambda: file_label.configure(text=""))

    threading.Thread(target=run, daemon=True).start()


encrypt_btn.configure(command=encrypt)
decrypt_btn.configure(command=decrypt)

window.mainloop()