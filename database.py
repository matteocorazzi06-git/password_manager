import csv
import datetime as dt
import os
from crypto_utils import decrypt_message, encrypt_message

def get_current_date():
    today = dt.datetime.now()
    return f"{str(today.day).zfill(2)}/{str(today.month).zfill(2)}/{today.year}"


def is_valid_date(date_string):
    try:
        dt.datetime.strptime(date_string, "%d/%m/%Y")
        return True
    except ValueError:
        return False


def initialize_db():
    file_exists = os.path.exists("passwords.csv")
    with open("passwords.csv", "a", newline="") as outfile:
        writer = csv.DictWriter(
            outfile, fieldnames=["username", "password", "date"]
        )
        if not file_exists:
            writer.writeheader()


def add_password(username, password, key):
    with open("passwords.csv", "a", newline="") as outfile:
        encrypted_pwd = encrypt_message(password, key).decode()
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
    if not os.path.exists("passwords.csv"):
        return results

    with open("passwords.csv", "r") as infile:
        reader = csv.DictReader(infile)
        for entry in reader:
            decrypted_pwd = decrypt_message(entry["password"], key)
            results.append(
                {
                    "username": entry["username"],
                    "password": decrypted_pwd,
                    "date": entry["date"],
                }
            )

    return results


def update_password(username, new_password, key):
    rows = []
    found = False

    with open("passwords.csv", "r") as infile:
        reader = csv.DictReader(infile)
        for entry in reader:
            if entry["username"].lower() == username.lower():
                found = True
                entry["password"] = encrypt_message(new_password, key).decode()
                entry["date"] = get_current_date()
            rows.append(entry)

    if found:
        with open("passwords.csv", "w", newline="") as outfile:
            writer = csv.DictWriter(
                outfile, fieldnames=["username", "password", "date"]
            )
            writer.writeheader()
            writer.writerows(rows)

    return found


def delete_password(username):
    rows = []
    found = False

    with open("passwords.csv", "r") as infile:
        reader = csv.DictReader(infile)
        for entry in reader:
            if entry["username"].lower() == username.lower():
                found = True
            else:
                rows.append(entry)

    if found:
        with open("passwords.csv", "w", newline="") as outfile:
            writer = csv.DictWriter(
                outfile, fieldnames=["username", "password", "date"]
            )
            writer.writeheader()
            writer.writerows(rows)

    return found

def delete_password_index(target_index):
    rows = []

    with open("passwords.csv", "r") as infile:
        reader = csv.DictReader(infile)
        for (index,entry) in enumerate(reader):
            if index != target_index:
                rows.append(entry)

    with open("passwords.csv", "w", newline="") as outfile:
        writer = csv.DictWriter(
            outfile, fieldnames=["username", "password", "date"]
        )
        writer.writeheader()
        writer.writerows(rows)

def get_passwords_by_date_range(start_date, end_date, key):
    results = []
    date_format = "%d/%m/%Y"

    start_obj = dt.datetime.strptime(start_date, date_format)
    end_obj = (
        dt.datetime.strptime(end_date, date_format) if end_date else None
    )

    all_entries = get_all_passwords(key)
    for entry in all_entries:
        entry_date_obj = dt.datetime.strptime(entry["date"], date_format)

        if end_obj is None:
            if entry_date_obj == start_obj:
                results.append(entry)
        else:
            if start_obj <= entry_date_obj <= end_obj:
                results.append(entry)

    return results