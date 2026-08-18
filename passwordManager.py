import csv
import os
from cryptography.fernet import Fernet
import datetime as d
import hashlib
import secrets
import string
import pyperclip 

def genera_password(lunghezza = 16):
    lettere_minuscole = string.ascii_lowercase
    lettere_maiuscole = string.ascii_uppercase
    numeri = string.digits
    simboli = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    tutti_i_caratteri = lettere_minuscole + lettere_maiuscole +simboli + numeri
    password = [secrets.choice(lettere_minuscole),secrets.choice(lettere_maiuscole),secrets.choice(simboli),secrets.choice(numeri)]
    password += [secrets.choice(tutti_i_caratteri) for _ in range(lunghezza-4)]
    secrets.SystemRandom().shuffle(password)

    return "".join(password)



def selectDateRange(date1,date2,chiave):
    with open("passwords.csv", "r") as infile:
        reader = csv.DictReader(infile, delimiter=",")
        found = False
        
        # Converti le date di input in datetime per il confronto
        # Se date2 è None, cerca solo la data esatta date1
        date1_obj = date1
        date2_obj = date2
        
        for entry in reader:
            try:
                # Converti la data del CSV da stringa a datetime
                entry_date = d.datetime.strptime(entry["Data"], "%d/%m/%Y")
                
                if date2_obj is None:
                    # Cerca solo la data esatta
                    if entry_date == date1_obj:
                        print(entry["Nome_Utente"], decrypt_message(entry["Password"], chiave), entry["Data"])
                        found = True
                else:
                    # Cerca nel range di date
                    if date1_obj <= entry_date <= date2_obj:
                        print(entry["Nome_Utente"], decrypt_message(entry["Password"], chiave), entry["Data"])
                        found = True
            except ValueError as e:
                print(f"Errore nel parsing della data: {entry['Data']}")
                continue
                
        if not found:
            if date2_obj is None:
                print(f"Non ho trovato nulla in data {date1_obj.strftime('%d/%m/%Y')}")
            else:
                print(f"Non ho trovato nulla nel range {date1_obj.strftime('%d/%m/%Y')} - {date2_obj.strftime('%d/%m/%Y')}")

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

def modificaPassword(username,chiave):
    righe = []
    trovato = False

    with open("passwords.csv","r")as infile:
        reader = csv.DictReader(infile)
        for entry in reader:
            if entry["Nome_Utente"].lower() == username.lower():
                trovato = True
                nuova_password = input(f"Inserisci la nuova password per {entry['Nome_Utente']}")
                entry["Password"] = encrypt_message(nuova_password,chiave).decode()
                entry["Data"] = curr_date()
                print("Password aggiornata correttamente")
            righe.append(entry)
    if not trovato:
        print("Username non trovato.")
        return
    with open("passwords.csv","w") as outfile:
        fieldnames = ["Nome_Utente","Password","Data"]
        writer = csv.DictWriter(outfile,fieldnames = fieldnames)
        writer.writeheader()
        writer.writerows(righe)

def eliminaPassword(username):
    righe = []
    trovato = False

    with open("passwords.csv","r")as infile:
        reader = csv.DictReader(infile)
        for entry in reader:
            if entry["Nome_Utente"].lower() == username.lower():
                trovato = True 
            else:
                righe.append(entry)
            
    if not trovato:
        print("Username non trovato.")
        return
    with open("passwords.csv","w") as outfile:
        fieldnames = ["Nome_Utente","Password","Data"]
        writer = csv.DictWriter(outfile,fieldnames = fieldnames)
        writer.writeheader()
        writer.writerows(righe)        

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
            print("E: esci, A: aggiungi password, V: visualizza password:, U: visualizzare passowrd per username, D: visualizza in range di date, M: modificare password,G: generare password,X: eliminare password")
            selezione = input("")
            selezione = selezione.lower()
            if selezione == "e":
                break
            elif selezione == "a":
                aggiungiPassword(chiave)
            elif selezione == "v":
                visualizzaPassword(chiave)
            elif selezione == "d":
                f1 = "%d/%m/%Y"
                
                date1_str = input("Inserire data 1 (formato: gg/mm/aaaa):\n")
                date1 = d.datetime.strptime(date1_str, f1)
                
                date2_str = input("Inserire data 2 (premi invio per cercare solo la data 1):\n")
                
                if date2_str.strip() == "":
                    # Se non viene inserita la seconda data, cerca solo la prima data
                    date2 = None
                    print(f"Cerco solo le password in data {date1_str}")
                else:
                    date2 = d.datetime.strptime(date2_str, f1)
                
                selectDateRange(date1, date2, chiave)
            elif selezione == "u":
                username = input("Inserire username desiderato: ")
                username = username.lower()
                selezionaPassword(username,chiave)
            elif selezione == "g":
                nuova_psw = genera_password()
                pyperclip.copy(nuova_psw)
                print("Password copiata nella clipboard")
            elif selezione == "x":
                nome_utente = input("Inserire nome utente per cui rimouvere password:")
                eliminaPassword(nome_utente)
            elif selezione == "m":
                username = input("Selezionare lo username per cui modificare password:")
                modificaPassword(username, chiave)
            else:
                print("Selezione non valida")
            
    else:
        print("Accesso Negato")

if __name__ == "__main__":
    main()