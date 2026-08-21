import hashlib
import os
import customtkinter as ctk
from crypto_utils import handle_key
import database as db

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class loginWindow(ctk.CTk):

    def __init__(self):
        super().__init__()

        # window
        self.title("Password manager - Login")
        self.geometry("400x300")

        db.initialize_db()
        self.encrypted_master = self.manage_master_password()

        #widget
        self.title_label = ctk.CTkLabel(
            self,
            text = "Insert Password",
            font = ("Arial",18,"bold")
        )
        self.title_label.pack(pady=20)

        self.entry_password = ctk.CTkEntry(
            self, placeholder_text = "Type here...", show = "*",width = 250
        )
        self.entry_password.pack(pady=10)

        self.entry_password.bind("<Return>", lambda event: self.verify_login())

        self.login_button = ctk.CTkButton(
            self,text = "Log in",command = self.verify_login
        )

        self.login_button.pack(pady = 10)

    def manage_master_password(self):
        key_path = "masterpassword.key"
        if not os.path.exists(key_path):
            pass
        if os.path.exists(key_path):
            with open(key_path) as infile:
                return infile.read()
        return None
    def verify_login(self):
        password_input = self.entry_password.get()

        if not self.encrypted_master:
            self.title_label.configure(
                text="Errore: Master password non configurata.", text_color="red"
            )
            return

        # Verifica hash SHA-256
        hashed_input = hashlib.sha256(password_input.encode()).hexdigest()

        if hashed_input == self.encrypted_master:
            # Sblocchiamo la chiave Fernet
            key = handle_key(password_input)
            if key is not None:
                self.title_label.configure(
                    text="Access granted", text_color="green"
                )
                self.after(
                    1000, lambda: self.open_main_dashboard(key)
                )  
            else:
                self.title_label.configure(
                    text="Key error", text_color="red"
                )
        else:
            self.title_label.configure(
                text="Incorrect Password. Try again", text_color="red"
            )
            self.entry_password.delete(0, "end")

    def open_main_dashboard(self, key):
            self.destroy()
            print(f"Access granted")
if __name__ == "__main__":
    app = loginWindow()
    app.mainloop()