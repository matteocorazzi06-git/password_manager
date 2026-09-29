import csv
import datetime as dt
import os
import shutil
from crypto_utils import decrypt_message, encrypt_message

from config import PSW_FILE

def export_csv_backup(destination_path):
    if os.path.exists(PSW_FILE):
        shutil.copy(PSW_FILE,destination_path)
        return True
    return False 

def get_current_date():
    today = dt.datetime.now()
    return f"{str(today.day).zfill(2)}/{str(today.month).zfill(2)}/{today.year}"


def initialize_db():
    file_exists = os.path.exists(PSW_FILE)
    with open(PSW_FILE, "a", newline="") as outfile:
        writer = csv.DictWriter(
            outfile, fieldnames=["username", "password", "date"]
        )
        if not file_exists:
            writer.writeheader()


def add_password(username, password, key):
    initialize_db()
    encrypted_pwd = encrypt_message(password, key).decode()
    with open(PSW_FILE, "a", newline="") as outfile:
        writer = csv.DictWriter(
            outfile, fieldnames=["username", "password", "date"]
        )
        writer.writerow(
            {
                "username": username,
                "password": encrypted_pwd,
                "date": get_current_date(),
            }
        )


def get_all_passwords(key):
    results = []
    if not os.path.exists(PSW_FILE):
        return results

    with open(PSW_FILE, "r") as infile:
        reader = csv.DictReader(infile)
        for entry in reader:
            try:
                decrypted_pwd = decrypt_message(entry["password"], key)
                results.append(
                    {
                        "username": entry["username"],
                        "password": decrypted_pwd,
                        "date": entry["date"],
                    }
                )
            except Exception:
                print("Not managed exception")


    return results


def update_password(target_index, new_username, new_password, key):
    if not os.path.exists(PSW_FILE):
        return
    rows = []
    with open(PSW_FILE, "r", encoding="utf-8") as infile:
        reader = list(csv.DictReader(infile))
        if 0<= target_index < len(reader):
            for idx,entry in enumerate(reader):
                if idx == target_index:
                    entry["username"] = new_username
                    entry["password"] = encrypt_message(new_password, key).decode()
                    entry["date"] = get_current_date()
                rows.append(entry)

        with open(PSW_FILE, "w", newline="",encoding="utf-8") as outfile:
            writer = csv.DictWriter(
                outfile, fieldnames=["username", "password", "date"]
            )
            writer.writeheader()
            writer.writerows(rows)

def delete_password_index(target_index):
    if not os.path.exists(PSW_FILE):
        return
    rows = []

    with open(PSW_FILE, "r",encoding="utf-8") as infile:
        reader = list(csv.DictReader(infile))
        if 0<= target_index < len(reader):
            rows = [entry for (index,entry) in enumerate(reader) if index != target_index]

        with open(PSW_FILE, "w", newline="",encoding="utf-8") as outfile:
            writer = csv.DictWriter(
                outfile, fieldnames=["username", "password", "date"]
            )
            writer.writeheader()
            writer.writerows(rows)
