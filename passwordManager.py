import csv
import os
from cryptography.fernet import Fernet
import datetime as d
import hashlib


def chooseMasterPassword():
    while True:
        password = input("Scegliere una nuova master password:")
        confirm_password = input("Confermare la master password:")
        if password == confirm_password:
            return password
        print("Le password non coincidono,ritentare")

def manageMasterPassword():
    if not os.path.exists("masterpassword.key"):
        password = chooseMasterPassword()
        with open("masterpassword.key","w") as password_file:
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            password_file.write(password_hash)
    with open("masterpassword.key","r") as password_file:
        return password_file.read()



def askForPassword(encrypted_Master_Password):
    passwordUser = input("Inserire Master Password:")
    if (hashlib.sha256(passwordUser.encode()).hexdigest()==encrypted_Master_Password):
        print("Accesso Garantito")
        return True
    print("Accesso Negato")
    return False

def curr_date():
    insertion_date = d.datetime.now()
    formatted_date = (f"{str(insertion_date.day).zfill(2)}/{str(insertion_date.month).zfill(2)}/{str(insertion_date.year)}")
    return formatted_date

def inizializza():
    file_esiste = os.path.exists("passwords.csv")

    with open("passwords.csv", "a", newline="") as outfile:
        fieldnames = ["Nome_Utente", "Password", "Data"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        if not file_esiste:
            writer.writeheader()
    return file_esiste

def aggiungiPassword(chiave):
    #data automatica
    with open("passwords.csv", "a",newline = "") as outfile:
        Nome_Utente = input("Inserisci Nome Utente: \n")
        Password = input("Inserisci password: \n")
        Data = curr_date()
        Password = (encrypt_message(Password,chiave)).decode()
        writer = csv.DictWriter(outfile, fieldnames=["Nome_Utente", "Password", "Data"])
        data = {"Nome_Utente": Nome_Utente, "Password": Password, "Data": Data}
        writer.writerow(data)


def visualizzaPassword(chiave):
    with open("passwords.csv", "r") as infile:
        reader = csv.DictReader(infile, delimiter=",")
        for entry in reader:
            print(entry["Nome_Utente"],decrypt_message(entry["Password"],chiave),entry["Data"])


def selezionaPassword(username,chiave):
    with open("passwords.csv", "r") as infile:
        reader = csv.DictReader(infile, delimiter=",")
        found = False
        for entry in reader:
            lower_entry_name = entry["Nome_Utente"].lower()
            if lower_entry_name == username:
                print(entry["Nome_Utente"],decrypt_message(entry["Password"],chiave),entry["Data"])
                found = True
        if not found:
            print("Non ho trovato questo username")


def encrypt_message(message,chiave):
    f = Fernet(chiave)
    messaggio_cifrato = f.encrypt(message.encode())
    return messaggio_cifrato

def decrypt_message(message,chiave):
    f = Fernet(chiave)
    messaggio_decifrato = f.decrypt(message.encode()).decode()
    return messaggio_decifrato

def handle_key(master_password):
    import base64
    master_hash = hashlib.sha256(master_password.encode()).digest()
    key_protector = Fernet(base64.urlsafe_b64encode(master_hash))
    if not os.path.exists("chiave.key"):
        chiave_base = Fernet.generate_key()
        chiave = key_protector.encrypt(chiave_base)
        with open("chiave.key","wb") as file_chiave:
            file_chiave.write(chiave)
        print("Nuova chiave di sicurezza generata e salvata")

    with open("chiave.key","rb") as file_chiave:
        encrypted_key = file_chiave.read()
    try:
        real_key = key_protector.decrypt(encrypted_key)
        return real_key
    except Exception:
        print("\n[ERRORE FATALE] Impossibile sbloccare la chiave dei dati!")
        print("La Master Password inserita non corrisponde a quella usata per cifrare i dati.")
        return None

def main():
    inizializza()
    encrypted_Master_Password = manageMasterPassword()

    password_utente = input("Inserire master Password:")
    if hashlib.sha256(password_utente.encode()).hexdigest() == encrypted_Master_Password:
        print("Accesso Garantito")

        chiave = handle_key(password_utente)
        if chiave is None:
            return
        while True:
            print("Scegliere l'operazione desiderata:")
            print("E: esci, A: aggiungi password, V: visualizza password:, U: visualizza passowrd per username")
            selezione = input("")
            selezione = selezione.lower()
            if selezione == "e":
                break
            elif selezione == "a":
                aggiungiPassword(chiave)
            elif selezione == "v":
                visualizzaPassword(chiave)
            elif selezione == "u":
                username = input("Inserire username desiderato: ")
                username = username.lower()
                selezionaPassword(username,chiave)
            else:
                print("Selezione non valida")
    else:
        print("Accesso Negato")

main()