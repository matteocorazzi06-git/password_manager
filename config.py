import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(BASE_DIR,"data")

os.makedirs(DATA_DIR, exist_ok =True)

DB_PATH = os.path.join(DATA_DIR, "passwords.db")

FILE_KEY = os.path.join(DATA_DIR, "key.key")
MASTER_PASSWORD_FILE = os.path.join(DATA_DIR, "masterpassword.key")
HINT_FILE = os.path.join(DATA_DIR, "hint.txt")