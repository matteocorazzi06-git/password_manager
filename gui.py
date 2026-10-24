import time

import hashlib
import os
import customtkinter as ctk
from crypto_utils import handle_key,generate_password,check_strength
import database as db
import pyperclip
from tkinter import filedialog 
import sys 

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

from config import MASTER_PASSWORD_FILE, HINT_FILE


class dashBoardWindow(ctk.CTkToplevel):
    def __init__(self, parent, key):
        #debug per far sì che la finestra si chiuda con unico mainloop e parent

        super().__init__(parent)

        self.key = key
        self.geometry("900x850")
        self.title("Dashboard")
        self.clear_timer = None

        self.protocol("WM_DELETE_WINDOW", self.close_app)

        #Frame principale con titolo
        self.title_label = ctk.CTkLabel(
            self, text = "Your passwords", font = ("Arial",20,"bold")
        )

        self.title_label.pack(pady = 10)

        self.export_btn = ctk.CTkButton(
            self,
            text = "💾 Export passwords",
            fg_color="#2b5b84",
            hover_color="#1e3d59",
            command = self.export_backup,
        )
        self.export_btn.pack(pady = (0,10))

        self.status_label = ctk.CTkLabel(
            self,text = "", font = ("Arial",11,"bold")
        )
        self.status_label.pack(pady = (0,5))

        #Frame per la sola aggiunta password
        self.add_frame = ctk.CTkFrame(self)
        self.add_frame.pack(pady=10, padx=20, fill="x")

        self.add_frame.grid_columnconfigure(0, weight=1)
        self.add_frame.grid_columnconfigure(1, weight=1)

        self.entry_user = ctk.CTkEntry(
            self.add_frame, placeholder_text="Username/Email"
        )
        self.entry_user.grid(row=0, column=0, padx=5, pady=(10, 2), sticky="ew")
        self.entry_user.bind("<Return>", lambda event: self.handle_password())
        self.entry_pass = ctk.CTkEntry(
            self.add_frame, placeholder_text="Password", show="*"
        )
        self.entry_pass.grid(row=0, column=1, padx=5, pady=(10, 2), sticky="ew")
        self.entry_pass.bind("<Return>", lambda event: self.handle_password())

        self.btn_generate = ctk.CTkButton(
            self.add_frame, 
            text = "Generate",
            width = 100,
            command=self.generate_secure_password,
        )
        self.btn_generate.grid(row=0, column=2, padx=5, pady=(10, 2))

        self.btn_add = ctk.CTkButton(
            self.add_frame,
            text="Add",
            width=100,
            command=self.handle_password,
        )
        self.btn_add.grid(row=0, column=3, padx=5, pady=(10, 2))

        self.security_frame = ctk.CTkFrame(
            self.add_frame, fg_color = "transparent"
        )
        self.security_frame.grid(row=1, column=1, padx=5, pady=(0, 10), sticky="w")

        self.strength_bar = ctk.CTkProgressBar(
            self.security_frame, height = 8, width = 200
        )
        self.strength_bar.set(0)
        self.strength_bar.pack(side="left", padx=(0, 5))
        
        self.strength_label = ctk.CTkLabel(
            self.security_frame, text = "" , font = ("Arial",11,"bold")
        )
        self.strength_label.pack(side = "left")

        self.entry_pass.bind(
            "<KeyRelease>",lambda event: self.update_strength_meter()
        )     

        self.entry_search = ctk.CTkEntry(
            self, placeholder_text= "Search by username...🔎"
        )
        self.entry_search.pack(padx = 25, pady = (0,10), fill= "x")
        self._search_after_id = None

        self.entry_search.bind(
            "<KeyRelease>",
            self.schedule_password_reload
        )

        #Frame che può essere scrollato in base alle password che ci stanno
        self.scrollable_frame = ctk.CTkScrollableFrame(
            self, width = 750, height = 450
        )

        self.scrollable_frame.pack(pady = 10, padx = 10,fill = "both",expand = True)

        self.load_passwords()


    def show_status(self,message, is_error = False):
        color = "#e74c3c" if is_error else "#2ecc71"
        self.status_label.configure(text = message,text_color = color)


    def update_strength_meter(self):
        pwd = self.entry_pass.get()
        progress, color, text = check_strength(pwd)

        self.strength_bar.set(progress)
        self.strength_bar.configure(progress_color = color)
        self.strength_label.configure(text = text, text_color = color)

    def export_backup(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes = [("CSV files","*.csv"),("All files","*.*")],
            title = "Save CSV backup",
            initialfile = "passwords_backup.csv",

        )
        if file_path:
            success= db.export_csv_backup(file_path)
            if success:
                self.show_status("backup successfully exported")
            else:
                self.show_status("Error exporting backup")

    def generate_secure_password(self):
        password = generate_password()
        self.copy_to_clipboard(password)
        self.entry_pass.delete(0,'end')
        self.entry_pass.insert(0,password)
        self.entry_pass.configure(show = "*")
        self.update_strength_meter()

    def schedule_password_reload(self,event=None):
        if self._search_after_id is not None:
            try:
                self.after_cancel(self._search_after_id)
            except Exception:
                pass
        self._search_after_id = self.after(250, self.load_passwords)
    def load_passwords(self):
            self._search_after_id = None
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
            

            self.scrollable_frame.grid_columnconfigure(0, weight=2)
            self.scrollable_frame.grid_columnconfigure(1, weight=3)
            self.scrollable_frame.grid_columnconfigure(2, weight=0)
            self.scrollable_frame.grid_columnconfigure(3, weight=0)
            self.scrollable_frame.grid_columnconfigure(4, weight=1)
            self.scrollable_frame.grid_columnconfigure(5, weight=0)
            self.scrollable_frame.grid_columnconfigure(6, weight=0)

            if not passwords:
                no_data_label = ctk.CTkLabel(
                    self.scrollable_frame, text="No passwords to show", anchor = "center"
                )
                no_data_label.grid(row=0, column=0, columnspan=7, pady=20,sticky = "ew")
                return 


            ctk.CTkLabel(
                self.scrollable_frame, text="Username", font=("Arial", 12, "bold"), anchor="w"
            ).grid(row=0, column=0, padx=10, pady=(5, 10), sticky="ew")

            ctk.CTkLabel(
                self.scrollable_frame, text="Password", font=("Arial", 12, "bold"), anchor="w"
            ).grid(row=0, column=1, padx=10, pady=(5, 10), sticky="ew")

            ctk.CTkLabel(
                self.scrollable_frame, text="Date", font=("Arial", 12, "bold"), anchor="center"
            ).grid(row=0, column=4, padx=10, pady=(5, 10), sticky="ew")

            for idx, item in enumerate(passwords, start = 1):
                
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
                btn_edit = ctk.CTkButton(
                    self.scrollable_frame, text = "✏️", width = 35, command = lambda item = item, i = idx-1: self.open_edit_dialog(item,i)
            
                )
                btn_edit.grid(row = idx,column = 5,padx = 2, pady = 5)

                btn_delete = ctk.CTkButton(
                    self.scrollable_frame, text = "❌", width = 35, command = lambda i = idx-1: self.confirm_delete_dialog(i) 
                )
                btn_delete.grid(row = idx, column = 6, padx = 2, pady = 5)

            self.update_idletasks()
    
    def open_edit_dialog(self,item,idx):
        edit_window = ctk.CTkToplevel(self)
        edit_window.title("Modifica credenziali")
        edit_window.geometry("350x300")
        edit_window.grab_set()

        ctk.CTkLabel(edit_window, text="Nuovo Username:").pack(pady=(15, 5))
        entry_user = ctk.CTkEntry(edit_window, width=220)
        entry_user.insert(0, item["username"])
        entry_user.pack(pady=5)

        ctk.CTkLabel(edit_window, text="Nuova Password:").pack(pady=(10, 5))
        entry_pass = ctk.CTkEntry(edit_window, width=220)
        entry_pass.insert(0, item["password"])
        entry_pass.pack(pady=5)

        err_label = ctk.CTkLabel(
            edit_window, text = "", text_color ="#e74c3c", font =("Arial",11)
        )
        err_label.pack(pady = 2)

        def save_changes():
            new_user = entry_user.get().strip()
            new_pwd = entry_pass.get().strip()

            if not new_user or not new_pwd:
                err_label.configure(text = "All fields are neccessary")
                return 
            if new_user and new_pwd:
                if db.update_password(idx, new_user, new_pwd, self.key):
                    edit_window.destroy()
                    self.load_passwords()
                    self.show_status("Credentials succesfully updated",is_error = False)
                else:
                    err_label.configure(text = "Error editing fields")
        def cancel_changes():
            edit_window.destroy()
        save = ctk.CTkButton(edit_window, text = "Save changes", command = save_changes)
        save.pack(pady = (15,5))
        cancel = ctk.CTkButton(edit_window, text = "Cancel",command = cancel_changes)
        cancel.pack(pady = (0,15))

    def confirm_delete_dialog(self,idx):
        delete_window = ctk.CTkToplevel(self)
        delete_window.title("Confirm deletion")
        delete_window.geometry("320x180")
        delete_window.grab_set()

        ctk.CTkLabel(
            delete_window,
            text = "Confirm deletion of this password?",
            font = ("Arial",13,"bold")
        ).pack(pady=(20,15))
        btn_frame = ctk.CTkFrame(delete_window, fg_color = "transparent")
        btn_frame.pack(pady = 10)

        def delete_password_entry():
            if db.delete_password_index(idx):
                delete_window.destroy()
                self.load_passwords()
                self.show_status("Deleted password",is_error = False)
            else:
                delete_window.destroy()
                self.show_status("Error occurred during deletion",is_error = True)

        btn_confirm = ctk.CTkButton(
            btn_frame,
            text="Delete",
            fg_color="#c0392b",
            hover_color="#e74c3c",
            width=100,
            command=delete_password_entry,
        )
        btn_confirm.pack(side="left", padx=10)

        btn_cancel = ctk.CTkButton(
            btn_frame,
            text="Cancel",
            fg_color="#7f8c8d",
            hover_color="#95a5a6",
            width=100,
            command=delete_window.destroy,
        )
        btn_cancel.pack(side="right", padx=10)


    def handle_password(self):

        user = self.entry_user.get().strip()
        pwd = self.entry_pass.get().strip()

        if not user or not pwd:
            self.show_status("Insert both username and password",is_error = True)
            return

        if user and pwd:
            if db.add_password(user,pwd,self.key):

                self.entry_user.delete(0, "end")
                self.entry_pass.delete(0, "end")
                self.update_strength_meter()
                self.load_passwords()
                self.show_status("Password addedd succesfully",is_error = False)
            else:
                self.show_status("Error saving password",is_error = True)


    def toggle_password(self,entry_widget):
        if entry_widget.cget("show") == "*":
            entry_widget.configure(show = "")
        else:
            entry_widget.configure(show = "*")

    def copy_to_clipboard(self, password):
        pyperclip.copy(password)

        self.show_status(
            "Password copied successfully. "
            "Deletion from clipboard in 30 seconds",
            is_error=False
        )
        if self.clear_timer is not None:
            try:
                self.after_cancel(self.clear_timer)
            except Exception:
                pass

        self.clear_timer = self.after(
            30_000,
            self.clear_clipboard
        )


    def clear_clipboard(self):
        self.clear_timer = None

        try:
            pyperclip.copy("")

            if self.winfo_exists():
                self.show_status(
                    "Clipboard was emptied",
                    is_error=False
                )
        except Exception:
            pass


    def close_app(self):
        if self.clear_timer is not None:
            try:
                self.after_cancel(self.clear_timer)
            except Exception:
                pass

            self.clear_timer = None

        if self.master and self.master.winfo_exists():
            self.master.destroy()
        else:
            self.destroy()


class loginWindow(ctk.CTk):

    def __init__(self):
        super().__init__()

        self._dashboard_opening = False

        self.title("Password manager - Login")
        self.geometry("400x380")

        self.protocol("WM_DELETE_WINDOW",self.close_login)

        db.initialize_db()
        self.encrypted_master = self.manage_master_password()


        self.is_first_setup = self.encrypted_master is None
        text_title = (
            "Create Master Password"
            if self.is_first_setup
            else "Insert Master Password"
        )
        self.title_label = ctk.CTkLabel(
            self,
            text = text_title,
            font = ("Arial",18,"bold")
        )
        self.title_label.pack(pady=20)

        self.hint_label = ctk.CTkLabel(
            self,
            text = "",
            text_color = "gray70",
            font = ("Arial",12,"bold"),
        )
        self.hint_label.pack(padx = 10)

        self.entry_password = ctk.CTkEntry(
            self, placeholder_text = "Type password...", show = "*",width = 250
        )
        self.entry_password.pack(pady = 8)

        self.entry_password.bind("<Return>", lambda event: self.verify_login())

        if self.is_first_setup:
            self.entry_hint = ctk.CTkEntry(
            self, placeholder_text = "Type hint...(optional)", width = 250
            )
            self.entry_hint.pack(pady = 8)
            self.entry_hint.bind("<Return>", lambda event: self.verify_login())


        btn_text = ("Create and Log In" if self.is_first_setup else "Log in")
        self.login_button = ctk.CTkButton(
            self,text = btn_text,command = self.verify_login
        )

        self.login_button.pack(pady = (12,10))

        if self.is_first_setup:
            self.info_label = ctk.CTkLabel(
                self,
                text = "Do not forget you password!\nYou will not be able to recover it in any way!",
                text_color = "orange",
                font = ("Arial",11),
            )
            self.info_label.pack(pady = (10,0))
        

    def manage_master_password(self):
        key_path = MASTER_PASSWORD_FILE
        if os.path.exists(key_path):
            with open(key_path,"r",encoding="utf-8") as infile:
                return infile.read()
        return None 
    def verify_login(self):
        if self._dashboard_opening:
            return
        password_input = self.entry_password.get().strip()

        if not password_input:
            self.title_label.configure(
                text="Insert a valid password", text_color="red"
            )
            return
        
        if self.is_first_setup:
            from crypto_utils import setup_master_password

            with open(HINT_FILE,"w",encoding = "utf-8") as outfile:
                outfile.write(self.entry_hint.get())

            key = setup_master_password(password_input)
            self.title_label.configure(
                text = "Created Mater Password", text_color = "green"
            )
            self._schedule_dashboard_open(key)

        else:
            hashed_input = hashlib.sha256(password_input.encode()).hexdigest()

            if hashed_input == self.encrypted_master:
                key = handle_key(password_input)
                if key is not None:
                    self.title_label.configure(
                        text="Access granted", text_color="green"
                    )
                    self._schedule_dashboard_open(key)
                else:
                    self.title_label.configure(
                        text="Key error", text_color="red"
                    )
            else:
                self.title_label.configure(
                    text="Incorrect Password. Try again", text_color="red"
                )
                self.entry_password.delete(0, "end")
                if os.path.exists(HINT_FILE):
                    with open(HINT_FILE,"r",encoding="utf-8") as infile:
                        hint_text = infile.read() 
                    if hint_text:
                        self.hint_label.configure(
                            text = f"Hint for the password: {hint_text}"
                        )
                    self.hint_label.pack(pady = 5)
    def close_login(self):
        self.quit()
        self.destroy()
        sys.exit(0)

    def _schedule_dashboard_open(self,key):
        if self._dashboard_opening:
            return
        self._dashboard_opening = True
        self.login_button.configure(state = "disabled")
        self.entry_password.configure(state = "disabled")

        if hasattr(self,"entry_hint"):
            self.entry_hint.configure(state = "disabled")

        self.after(
            300,
            lambda: self.open_main_dashboard(key)
        )

    def open_main_dashboard(self, key):
            self.withdraw()
            self.dashboard = dashBoardWindow(self,key)
            

#if __name__ == "__main__":
#    app = loginWindow()
#    app.mainloop()

if __name__ == "__main__":
    _t_gui = time.perf_counter()
    app = loginWindow()


    app.mainloop()