import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(BASE_DIR,"data")

os.makedirs(DATA_DIR, exist_ok =True)

PSW_FILE = os.path.join(DATA_DIR, "passwords.csv")
FILE_KEY = os.path.join(DATA_DIR, "key.key")
MASTER_PASSWORD_FILE = os.path.join(DATA_DIR, "masterpassword.key")
HINT_FILE = os.path.join(DATA_DIR, "hint.txt")