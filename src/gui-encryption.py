"""
GRAPHICAL USER INTERFACE (GUI)
------------------------------
This script creates the window, buttons, and progress bars.
It acts as the 'bridge' between the user and the Encryption logic.
"""

import threading
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
from encrypter import Encryption, MIN_PASSWORD_LENGTH
import os

# --- APPEARANCE SETUP ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

tool = Encryption()

window = ctk.CTk()
window.title("File Encrypter and Decrypter")
window.geometry("420x400")
window.resizable(False, False)


def set_icon():
    """Attempts to load the window icon from the /image folder."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(current_dir, "image", "icon.png")
    try:
        if os.path.exists(icon_path):
            icon_image = tk.PhotoImage(file=icon_path)
            window.iconphoto(False, icon_image)
    except Exception:
        print("Note: Icon could not be loaded.")


window.after(200, set_icon)

# --- FOLDER SELECTION UI ---
folder_frame = ctk.CTkFrame(window, fg_color="transparent")
folder_frame.pack(padx=20, pady=(20, 0), fill="x")

ctk.CTkLabel(folder_frame, text="Folder Path", anchor="w").pack(fill="x")

row = ctk.CTkFrame(folder_frame, fg_color="transparent")
row.pack(fill="x", pady=(4, 0))

path_entry = ctk.CTkEntry(row, placeholder_text="Select a folder...")
path_entry.pack(side="left", expand=True, fill="x", padx=(0, 8))


def browse():
    """Opens a folder picker dialog."""
    path = filedialog.askdirectory(title="Select Folder")
    if path:
        path_entry.delete(0, "end")
        path_entry.insert(0, path)


ctk.CTkButton(row, text="Browse", width=80, command=browse).pack(side="right")

# --- PASSWORD UI ---
pw_frame = ctk.CTkFrame(window, fg_color="transparent")
pw_frame.pack(padx=20, pady=(12, 0), fill="x")

ctk.CTkLabel(
    pw_frame,
    text=f"Security Password  (min {MIN_PASSWORD_LENGTH} characters)",
    anchor="w"
).pack(fill="x")

password_entry = ctk.CTkEntry(pw_frame, placeholder_text="Enter password...", show="*")
password_entry.pack(fill="x", pady=(4, 0))

# --- PROGRESS & STATUS UI ---
# Progress bar is always in the layout but starts with zero height so the
# window size stays stable until a task begins.
progress_bar = ctk.CTkProgressBar(window, width=380, height=12)
progress_bar.set(0)
progress_bar.pack(pady=(10, 0))
progress_bar.pack_forget()  # Hidden until a task starts

file_label = ctk.CTkLabel(window, text="", font=ctk.CTkFont(size=11), text_color="gray")
file_label.pack(pady=(10, 0))

status_label = ctk.CTkLabel(window, text="Ready", font=ctk.CTkFont(size=12))
status_label.pack(pady=(2, 0))

# --- ACTION BUTTONS ---
btn_frame = ctk.CTkFrame(window, fg_color="transparent")
btn_frame.pack(padx=20, pady=(12, 0), fill="x")

encrypt_btn = ctk.CTkButton(btn_frame, text="Encrypt Folder", fg_color="#1f6aa5", hover_color="#144f7a")
encrypt_btn.pack(side="left", expand=True, fill="x", padx=(0, 6))

decrypt_btn = ctk.CTkButton(btn_frame, text="Decrypt Folder", fg_color="#2d6a2d", hover_color="#1e4d1e")
decrypt_btn.pack(side="right", expand=True, fill="x", padx=(6, 0))


# --- HELPER FUNCTIONS ---

def set_status(message, color):
    """Updates the status text at the bottom."""
    status_label.configure(text=message, text_color=color)


def set_buttons_enabled(enabled: bool):
    """Prevents users from clicking buttons while a task is running."""
    state = "normal" if enabled else "disabled"
    encrypt_btn.configure(state=state)
    decrypt_btn.configure(state=state)
    path_entry.configure(state=state)


def make_progress_callback():
    """
    Returns a callback that the encryption engine calls after each file.
    All UI updates are scheduled via window.after() so they always run on
    the main thread — safe regardless of which thread calls the callback.
    """
    def callback(current: int, total: int, filename: str):
        value = current / total
        label = filename if len(filename) <= 38 else filename[:35] + '...'

        def _update():
            progress_bar.set(value)
            file_label.configure(text=f"Processing: {label}")

        window.after(0, _update)

    return callback


def get_password_confirmation(title, text):
    """Creates a popup window to confirm the password (prevents typos)."""
    dialog = ctk.CTkToplevel(window)
    dialog.title(title)
    dialog.geometry("300x160")
    dialog.resizable(False, False)
    dialog.attributes("-topmost", True)
    dialog.wait_visibility()
    dialog.grab_set()

    ctk.CTkLabel(dialog, text=text).pack(pady=(15, 5))
    entry = ctk.CTkEntry(dialog, show="*")
    entry.pack(pady=(0, 15))
    entry.focus()

    result = [None]

    def on_ok():
        result[0] = entry.get()
        dialog.destroy()

    ctk.CTkButton(dialog, text="Confirm", command=on_ok, width=100).pack()
    window.wait_window(dialog)
    return result[0]


# --- MAIN LOGIC WRAPPERS ---

def start_task(mode):
    """
    Validates input, shows a confirmation for destructive actions,
    then hands off to a background thread so the UI stays responsive.
    """
    path = path_entry.get().strip()
    password = password_entry.get()

    if not path or not os.path.exists(path):
        set_status("Error: Invalid folder path.", "red")
        return
    if not password:
        set_status("Error: Password required.", "red")
        return
    if len(password) < MIN_PASSWORD_LENGTH:
        set_status(f"Error: Password must be at least {MIN_PASSWORD_LENGTH} characters.", "red")
        return

    if mode == "encrypt":
        # Confirm the password to guard against typos before a destructive op.
        confirm = get_password_confirmation("Confirm Password", "Re-type password to lock:")
        if confirm is None:
            return  # User closed the dialog
        if confirm != password:
            set_status("Error: Passwords did not match.", "red")
            return
        # Extra safety: warn the user before encrypting
        if not messagebox.askyesno(
            "Confirm Encryption",
            f"All files in:\n\n  {path}\n\nwill be encrypted. Continue?",
            icon="warning"
        ):
            return

    set_buttons_enabled(False)
    progress_bar.pack(pady=10)
    progress_bar.set(0)
    set_status(f"{mode.capitalize()}ing files...", "gray")

    def run():
        try:
            if mode == "encrypt":
                tool.Encrypt(path, password, progress_callback=make_progress_callback())
            else:
                tool.Decrypt(path, password, progress_callback=make_progress_callback())

            # Clear the password field on success to avoid leaving it in memory.
            window.after(0, lambda: password_entry.delete(0, "end"))
            window.after(0, lambda: set_status(f"Success: Folder {mode}ed!", "green"))
        except Exception as e:
            msg = str(e)
            window.after(0, lambda m=msg: set_status(f"Error: {m}", "red"))
        finally:
            window.after(0, lambda: set_buttons_enabled(True))
            window.after(0, lambda: progress_bar.pack_forget())
            window.after(0, lambda: file_label.configure(text=""))

    threading.Thread(target=run, daemon=True).start()


encrypt_btn.configure(command=lambda: start_task("encrypt"))
decrypt_btn.configure(command=lambda: start_task("decrypt"))

window.mainloop()
