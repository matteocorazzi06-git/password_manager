import hashlib
import os
import pyperclip
from crypto_utils import generate_password, handle_key
import database as db


def manage_master_password():
    if not os.path.exists("masterpassword.key"):
        while True:
            password = input("Choose a new master password: ")
            confirm = input("Confirm master password: ")
            if password == confirm:
                with open("masterpassword.key", "w") as f:
                    f.write(hashlib.sha256(password.encode()).hexdigest())
                break
            print("Passwords do not match. Please try again.")

    with open("masterpassword.key", "r") as f:
        return f.read()


def main():
    db.initialize_db()
    encrypted_master = manage_master_password()

    user_password = input("Enter Master Password: ")
    if (
        hashlib.sha256(user_password.encode()).hexdigest()
        != encrypted_master
    ):
        print("Access Denied")
        return

    key = handle_key(user_password)
    if key is None:
        return

    print("\nAccess Granted!")

    while True:
        print("\n--- PASSWORD MANAGER ---")
        print(
            "E: Exit | A: Add | V: View All | U: Search User | D: Date Range | M: Modify | X: Delete | G: Generate"
        )
        choice = input("Select operation: ").lower()

        if choice == "e":
            print("Goodbye!")
            break
        elif choice == "a":
            username = input("Username: ")
            password = input("Password: ")
            db.add_password(username, password, key)
            print("Password saved successfully!")
        elif choice == "v":
            passwords = db.get_all_passwords(key)
            for p in passwords:
                print(
                    f"User: {p['username']} | Pwd: {p['password']} | Date: {p['date']}"
                )
        elif choice == "u":
            target = input("Enter username to search: ").lower()
            passwords = db.get_all_passwords(key)
            found = False
            for p in passwords:
                if p["username"].lower() == target:
                    print(
                        f"User: {p['username']} | Pwd: {p['password']} | Date: {p['date']}"
                    )
                    found = True
            if not found:
                print("Username not found.")
        elif choice == "d":
            date1 = input("Enter Start Date (DD/MM/YYYY): ")
            if not db.is_valid_date(date1):
                print("Invalid start date.")
                continue

            date2 = input("Enter End Date (press Enter for single date): ")
            if date2.strip() != "" and not db.is_valid_date(date2):
                print("Invalid end date.")
                continue

            results = db.get_passwords_by_date_range(
                date1, date2 if date2.strip() else None, key
            )
            for p in results:
                print(
                    f"User: {p['username']} | Pwd: {p['password']} | Date: {p['date']}"
                )
        elif choice == "m":
            username = input("Enter username to modify: ")
            new_pwd = input("Enter new password: ")
            if db.update_password(username, new_pwd, key):
                print("Password updated successfully!")
            else:
                print("Username not found.")
        elif choice == "x":
            username = input("Enter username to delete: ")
            if db.delete_password(username):
                print("Password deleted successfully!")
            else:
                print("Username not found.")
        elif choice == "g":
            new_pass = generate_password()
            pyperclip.copy(new_pass)
            print(f"Generated and copied to clipboard: {new_pass}")
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    main()