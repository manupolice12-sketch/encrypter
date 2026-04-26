"""
GRAPHICAL USER INTERFACE (GUI)
------------------------------
This script creates the window, buttons, and progress bars.
It acts as the 'bridge' between the user and the Encryption logic.
"""

import threading
import customtkinter as ctk
from tkinter import filedialog
from encrypter import Encryption
import os

# --- APPEARANCE SETUP ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

tool = Encryption()
window = ctk.CTk()
window.title("File Encrypter and Decrypter")
window.geometry("420x420")
window.resizable(False, False)

def set_status(text, color):
    status_label.configure(text=text, text_color=color)

def set_buttons_enabled(state):
    s = "normal" if state else "disabled"
    encrypt_btn.configure(state=s)
    decrypt_btn.configure(state=s)
    browse_btn.configure(state=s)

def browse_folder():
    p = filedialog.askdirectory()
    if p:
        path_entry.delete(0, "end")
        path_entry.insert(0, p)
        # Background check for disk space so the UI doesn't freeze
        threading.Thread(target=lambda: tool.check_backup_feasibility(p), daemon=True).start()

def start_task(mode):
    path = path_entry.get().strip()
    password = password_entry.get().strip()

    if not path or not os.path.exists(path):
        return set_status("Error: Invalid path", "red")
    if not password:
        return set_status("Error: Password required", "red")

    if mode == "encrypt":
        dialog = ctk.CTkInputDialog(text="Confirm Password:", title="Confirmation")
        res = dialog.get_input()
        if res is None: return # User cancelled
        if res != password:
            return set_status("Error: Passwords did not match", "red")

    set_buttons_enabled(False)
    progress_bar.pack(pady=10)
    progress_bar.set(0)
    
    def run():
        try:
            if mode == "encrypt":
                if not tool.backup_possible:
                    window.after(0, lambda: set_status("Risk: No space for backup. Encrypting...", "orange"))
                
                tool.Encrypt(path, password, lambda c, t, f: window.after(0, lambda: [
                    progress_bar.set(c/t), 
                    file_label.configure(text=f)
                ]))
            else:
                tool.Decrypt(path, password, lambda c, t, f: window.after(0, lambda: [
                    progress_bar.set(c/t), 
                    file_label.configure(text=f)
                ]))
            
            window.after(0, lambda: [set_status("Success!", "green"), password_entry.delete(0, "end")])
        except Exception as e:
            window.after(0, lambda: set_status(f"Error: {str(e)}", "red"))
        finally:
            window.after(0, lambda: [
                set_buttons_enabled(True), 
                progress_bar.pack_forget(), 
                file_label.configure(text="")
            ])

    threading.Thread(target=run, daemon=True).start()

# --- UI ELEMENTS ---
path_entry = ctk.CTkEntry(window, width=300, placeholder_text="Select folder...")
path_entry.pack(pady=20)

browse_btn = ctk.CTkButton(window, text="Browse Folder", command=browse_folder)
browse_btn.pack()

password_entry = ctk.CTkEntry(window, width=300, show="*", placeholder_text="Enter password...")
password_entry.pack(pady=20)

encrypt_btn = ctk.CTkButton(window, text="Encrypt Folder", command=lambda: start_task("encrypt"), fg_color="green", hover_color="#006400")
encrypt_btn.pack(pady=5)

decrypt_btn = ctk.CTkButton(window, text="Decrypt Folder", command=lambda: start_task("decrypt"))
decrypt_btn.pack(pady=5)

status_label = ctk.CTkLabel(window, text="")
status_label.pack(pady=10)

file_label = ctk.CTkLabel(window, text="", font=("Arial", 10))
file_label.pack()

progress_bar = ctk.CTkProgressBar(window, width=300)

window.mainloop()