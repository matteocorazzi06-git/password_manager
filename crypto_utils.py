import base64
import hashlib
import os
import secrets
import string
from cryptography.fernet import Fernet
import re

def check_strength(password):
    if not password:
        return 0.0,"Gray",""

    score = 0
    if len(password) >= 8:
        score += 1
    if len(password) >= 16:
        score+= 1
    if re.search(r"[a-z]",password):
        score+=1
    if re.search(r"[A-Z]",password):
        score+=1
    if re.search(r"[!@#$%^&*(),.?\":{}|<>]",password):
        score+=1    

    fraction = score / 5

    if score <= 2:
            return fraction, "#e74c3c", "Weak 🔴"
    elif score <= 4:
        return fraction, "#f39c12", "Mediocre 🟡"
    else:
        return fraction, "#2ecc71", "Strong 🟢"



def generate_password(length=16):
    lowercase = string.ascii_lowercase
    uppercase = string.ascii_uppercase
    digits = string.digits
    symbols = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    all_chars = lowercase + uppercase + symbols + digits

    password = [
        secrets.choice(lowercase),
        secrets.choice(uppercase),
        secrets.choice(symbols),
        secrets.choice(digits),
    ]
    password += [secrets.choice(all_chars) for _ in range(length - 4)]
    secrets.SystemRandom().shuffle(password)
    return "".join(password)


def encrypt_message(message, key):
    f = Fernet(key)
    return f.encrypt(message.encode())


def decrypt_message(message, key):
    f = Fernet(key)
    return f.decrypt(message.encode()).decode()


def handle_key(master_password):
    master_hash = hashlib.sha256(master_password.encode()).digest()
    key_protector = Fernet(base64.urlsafe_b64encode(master_hash))

    if not os.path.exists("key.key"):
        raw_key = Fernet.generate_key()
        encrypted_key = key_protector.encrypt(raw_key)
        with open("key.key", "wb") as key_file:
            key_file.write(encrypted_key)

    with open("key.key", "rb") as key_file:
        encrypted_key = key_file.read()

    try:
        return key_protector.decrypt(encrypted_key)
    except Exception:
        return None