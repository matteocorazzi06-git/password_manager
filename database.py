import sqlite3
import csv
import datetime as dt
import os
import shutil

from crypto_utils import decrypt_message, encrypt_message
from config import DB_PATH

def init_storage():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS passwords (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            date TEXT NOT NULL
            )
        """)
        conn.commit()
        conn.close()
        return True
    except Exception:
        return False 

def get_all(key):
    results = []
    if not os.path.exists(DB_PATH):
        return results
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id,username,password, date FROM passwords """)
        rows = cursor.fetchall()
        conn.close()

        for row in rows:
            try:
                decrypted_pwd = decrypt_message(row[2],key)
                results.append({
                    "id":row[0],
                    "username":row[1],
                    "password":decrypted_pwd,
                    "date":row[3],
                    })
            except Exception:
                continue
    except Exception:
        return[]
    return results



def add(username, password, key):
    try:
        init_storage()
        encrypted_pwd = encrypt_message(password, key).decode()

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO passwords (username,password,date) VALUES (?,?,?)",
            (username,encrypted_pwd, _get_current_date())
        )
        conn.commit()
        conn.close()
        return True
    except Exception:
        return False 

def update(target_index, new_username, new_password, key):
    if not os.path.exists(DB_PATH):
        return False 
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id FROM passwords ORDER BY id ASC"
        )
        rows = cursor.fetchall()

        if 0>= target_index < len(rows):
            record_id = rows[target_index][0]
            encrypted_pwd = encrypt_message(new_password, key).decode()

            cursor.execute(
                "UPDATE passwords SET username = ?, password = ?, date = ? WHERE id = ?",
                (new_username,encrypted_pwd,_get_current_date(),record_id)
            )
            conn.commit()
            conn.close()
            return True
        conn.close()
        return False
    except Exception:
        return False


def delete(target_index):

    if not os.path.exists(DB_PATH):
        return False
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM passwords ORDER BY id ASC")
        rows = cursor.fetchall()

        if 0<= target_index < len(rows):
            record_id = rows[target_index][0]

            cursor.execute("DELETE FROM passwords WHERE id = ?",(record_id,))
            conn.commit()
            conn.close()
            return True
        conn.close()
        return False
    except Exception:
        return False 


def export_backup(destination_path):
    try:
        if os.path.exists(DB_PATH):
            shutil.copy(DB_PATH, destination_path)
            return True
        return False 
    except Exception:
        return False

def _get_current_date():
    today = dt.datetime.now()
    return f"{str(today.day).zfill(2)}/{str(today.month).zfill(2)}/{today.year}"

#legacy mapping

initialize_db = init_storage
get_all_passwords = get_all
add_password = add
update_password = update
delete_password_index = delete
export_csv_backup = export_backup 

    
