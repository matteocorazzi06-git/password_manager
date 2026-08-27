import hashlib
import os
import customtkinter as ctk
from crypto_utils import handle_key,generate_password
import database as db
import pyperclip
import time 
import threading 

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class dashBoardWindow(ctk.CTk):
    def __init__(self,key):
        super().__init__()
        self.key = key
        self.geometry("800x800")
        self.title("Dashboard") 
        self.clear_timer = None 

        self.title_label = ctk.CTkLabel(
            self, text = "Your passwords", font = ("Arial",20,"bold")
        )

        self.title_label.pack(pady = 10)

        self.add_frame = ctk.CTkFrame(self)
        self.add_frame.pack(pady=10, padx=20, fill="x")

        self.entry_search = ctk.CTkEntry(
            self, placeholder_text= "Search by username...🔎"
        )
        self.entry_search.pack(padx = 20, pady = (0,10), fill= "x")
        self.entry_search.bind("<KeyRelease>", lambda event: self.load_passwords() )

        self.entry_user = ctk.CTkEntry(
            self.add_frame, placeholder_text="Username/Email", width=180
        )
        self.entry_user.pack(side="left", padx=5, pady=10, expand=True, fill="x")

        self.entry_pass = ctk.CTkEntry(
            self.add_frame, placeholder_text="Password", show="*", width=180
        )
        self.entry_pass.pack(side="left", padx=5, pady=10, expand=True, fill="x")

        self.entry_pass.bind("<Return>", lambda event: self.handle_password())

        self.btn_generate = ctk.CTkButton(
            self.add_frame, 
            text = "Generate",
            width = 100,
            command=self.generate_secure_password,
        )
        self.btn_generate.pack(side = "left", padx = 5, pady = 10)

        self.btn_add = ctk.CTkButton(
            self.add_frame,
            text="Add",
            width=100,
            command=self.handle_password,
        )
        self.btn_add.pack(side="left", padx=5, pady=10)

        self.scrollable_frame = ctk.CTkScrollableFrame(
            self, width = 550, height = 280
        )

        self.scrollable_frame.pack(pady = 10, padx = 10)

        self.load_passwords()

    def generate_secure_password(self):
        password = generate_password()
        self.copy_to_clipboard(password)
        self.entry_pass.delete(0,'end')
        self.entry_pass.insert(0,password)

    def load_passwords(self):
            for widget in self.scrollable_frame.winfo_children():
                widget.destroy()

            passwords = db.get_all_passwords(self.key)

            search_query = (
                self.entry_search.get().strip().lower()
                if hasattr(self,"entry_search")
                else ""
            )
            if search_query:
                passwords = [
                    p
                    for p in passwords
                    if search_query in p["username"].lower()
            ]
            

            if not passwords:
                no_data_label = ctk.CTkLabel(
                    self.scrollable_frame, text="No passwords to show"
                )
                no_data_label.grid(row=0, column=0, columnspan=3, pady=20)
                return 

            self.scrollable_frame.grid_columnconfigure(0, weight=2)
            self.scrollable_frame.grid_columnconfigure(1, weight=3)
            self.scrollable_frame.grid_columnconfigure(2, weight=0)
            self.scrollable_frame.grid_columnconfigure(3, weight=0)
            self.scrollable_frame.grid_columnconfigure(4, weight=1)
            self.scrollable_frame.grid_columnconfigure(5, weight=0)


            ctk.CTkLabel(
                self.scrollable_frame, text="Username", font=("Arial", 12, "bold"), anchor="w"
            ).grid(row=0, column=0, padx=10, pady=(5, 10), sticky="ew")

            ctk.CTkLabel(
                self.scrollable_frame, text="Password", font=("Arial", 12, "bold"), anchor="w"
            ).grid(row=0, column=1, padx=10, pady=(5, 10), sticky="ew")

            ctk.CTkLabel(
                self.scrollable_frame, text="Date", font=("Arial", 12, "bold"), anchor="center"
            ).grid(row=0, column=4, padx=10, pady=(5, 10), sticky="ew")

            for idx, item in enumerate(passwords, start=1):
                # Colonna 0: Username
                ctk.CTkLabel(
                    self.scrollable_frame, text=item["username"], anchor="w"
                ).grid(row=idx, column=0, padx=10, pady=5, sticky="ew")

                pwd_entry = ctk.CTkEntry(self.scrollable_frame, show="*")
                pwd_entry.insert(0, item["password"])
                pwd_entry.configure(state="readonly")
                pwd_entry.grid(row=idx, column=1, padx=10, pady=5, sticky="ew")

                ctk.CTkLabel(
                    self.scrollable_frame, text=item["date"], anchor="center"
                ).grid(row=idx, column=4, padx=10, pady=5, sticky="ew")

                btn_toggle = ctk.CTkButton(
                    self.scrollable_frame, text = "👁️", width = 35,command = lambda p = pwd_entry: self.toggle_password(p)

                )
                btn_toggle.grid(row = idx, column = 2, padx = 2, pady = 5)

                btn_clipboard = ctk.CTkButton(
                    self.scrollable_frame, text = "📝", width = 35,command = lambda p = item["password"]: self.copy_to_clipboard(p)

                )
                btn_clipboard.grid(row = idx, column = 3, padx = 2, pady = 5)

                btn_delete = ctk.CTkButton(
                    self.scrollable_frame, text = "❌", width = 35, command = lambda i = idx: self.delete_password_entry(i-1) 
                )
                btn_delete.grid(row = idx, column = 5, padx = 2, pady = 5)

    def delete_password_entry(self,idx):
        db.delete_password_index(idx)
        self.load_passwords()

    def handle_password(self):

        user = self.entry_user.get().strip()
        pwd = self.entry_pass.get().strip()

        if user and pwd:
            db.add_password(user,pwd,self.key)

            self.entry_user.delete(0, "end")
            self.entry_pass.delete(0, "end")
            self.load_passwords()


    def toggle_password(self,entry_widget):
        if entry_widget.cget("show") == "*":
            entry_widget.configure(show = "")
        else:
            entry_widget.configure(show = "*")

    def copy_to_clipboard(self,password):
        pyperclip.copy(password)
        print("La password sarà cancellata dalla clipboard tra 30 secondi dalla clipboard")
        if self.clear_timer:
            self.clear_timer.cancel()
        self.clear_timer = threading.Timer(30, self.clear_clipboard)
        self.clear_timer.daemon = True
        self.clear_timer.start()

    def clear_clipboard(self):
        time.sleep(30)
        pyperclip.copy("")
        print("Cancellata dalla clipboard")
        self.clear_timer = None

class loginWindow(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Password manager - Login")
        self.geometry("400x300")

        db.initialize_db()
        self.encrypted_master = self.manage_master_password()

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
                text="Error: master password is not configured", text_color="red"
            )
            return

        hashed_input = hashlib.sha256(password_input.encode()).hexdigest()

        if hashed_input == self.encrypted_master:
            key = handle_key(password_input)
            if key is not None:
                self.title_label.configure(
                    text="Access granted", text_color="green"
                )
                self.after(
                    300, lambda: self.open_main_dashboard(key)
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
            self.withdraw()
            print(f"Access granted")
            dashboard = dashBoardWindow(key)
            dashboard.mainloop()
if __name__ == "__main__":
    app = loginWindow()
    app.mainloop()