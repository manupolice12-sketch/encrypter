import customtkinter as ctk
import sys
from .encrypter import Encryption
from tkinter import filedialog
 
tool = Encryption()
window = ctk.CTk()
window.title("File Encrypter and Decrypter")
window.geometry("230x230")
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")
entry = ctk.CTkEntry(window, placeholder_text="Type Decrypt or Encrypt")
entry.pack(pady=115)
def conduct():
    global tool
    command = entry.get().lower().strip()
    if command == 'encrypt':
        tool.Encrypt()
    elif command == 'decrypt':
        tool.Decrypt()
button = ctk.CTkButton(window, text="submit", command=conduct)
button.pack(pady=120)
