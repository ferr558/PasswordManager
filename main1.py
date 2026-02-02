import re
from cryptography.fernet import InvalidToken
from fastapi import FastAPI, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from pydantic import BaseModel, field_validator
from typing import Optional
import database1
import security1
import os

app = FastAPI()

# Inizializzazione del salt al primo avvio
db = database1.SessionLocal()
try:
    db_config = db.query(database1.Config).filter(database1.Config.key == "encryption_salt").first()
    if not db_config:
        SALT = os.urandom(16)
        new_config = database1.Config(key="encryption_salt", value=SALT)
        db.add(new_config)
        db.commit()
    else:
        SALT = db_config.value
finally:
    db.close()

# Dependency per il database
def get_db():
    db = database1.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Modelli Pydantic
class MasterPasswordCreate(BaseModel):
    master_password: str
    
    @field_validator('master_password')
    @classmethod
    def check_password_strength(cls, v: str):
        if len(v) < 8:
            raise ValueError('La Master Password deve essere di almeno 8 caratteri')
        if not re.search("[A-Z]", v):
            raise ValueError('La Master Password deve contenere almeno una lettera maiuscola')
        if not re.search("[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError('La Master Password deve contenere almeno un carattere speciale')
        return v

class CredentialBase(BaseModel):
    app_name: str
    username: str
    created_by: str
    password: Optional[str] = None

class CredentialUpdate(BaseModel):
    password: Optional[str] = None

# ENDPOINT: Verifica se il sistema è inizializzato
@app.get("/status/")
def check_initialization(db: Session = Depends(get_db)):
    """Controlla se la master password è già stata impostata"""
    master_pw = db.query(database1.MasterPassword).first()
    return {
        "is_initialized": master_pw is not None,
        "message": "Sistema già inizializzato" if master_pw else "Nessuna master password configurata"
    }

# ENDPOINT: Inizializza la master password (solo al primo avvio)
@app.post("/initialize/")
def initialize_master_password(data: MasterPasswordCreate, db: Session = Depends(get_db)):
    """Crea la master password al primo accesso"""
    # Verifica che non sia già inizializzato
    existing = db.query(database1.MasterPassword).first()
    if existing:
        raise HTTPException(status_code=400, detail="Master password già configurata")
    
    # Crea l'hash della master password
    password_hash = security1.hash_master_password(data.master_password)
    
    # Salva nel database
    master_pw = database1.MasterPassword(
        password_hash=password_hash,
        is_initialized=True
    )
    db.add(master_pw)
    db.commit()
    
    return {
        "message": "Master password creata con successo",
        "success": True
    }

# ENDPOINT: Verifica la master password
@app.post("/verify/")
def verify_master_password(data: MasterPasswordCreate, db: Session = Depends(get_db)):
    """Verifica se la master password inserita è corretta"""
    master_pw = db.query(database1.MasterPassword).first()
    
    if not master_pw:
        raise HTTPException(status_code=404, detail="Master password non configurata")
    
    is_valid = security1.verify_master_password(data.master_password, master_pw.password_hash)
    
    if not is_valid:
        raise HTTPException(status_code=401, detail="Master password errata")
    
    return {
        "message": "Master password corretta",
        "success": True
    }

# NUOVO ENDPOINT: Ottieni lista app
@app.get("/apps/")
def get_app_list(
    master_password: str = Header(...),
    db: Session = Depends(get_db)
):
    """Restituisce la lista di tutte le app per cui ci sono credenziali salvate"""
    # Verifica la master password
    master_pw = db.query(database1.MasterPassword).first()
    if not master_pw:
        raise HTTPException(status_code=404, detail="Sistema non inizializzato")
    
    if not security1.verify_master_password(master_password, master_pw.password_hash):
        raise HTTPException(status_code=401, detail="Master password errata")
    
    # Query per ottenere le app uniche
    apps = db.query(database1.Credential.app_name).distinct().all()
    app_list = [app[0] for app in apps]
    
    return {"apps": sorted(app_list)}

# ENDPOINT: Crea una nuova credenziale
@app.post("/credentials/")
def create_credential(
    cred: CredentialBase, 
    master_password: str = Header(...),
    db: Session = Depends(get_db)
):
    """Aggiunge una nuova credenziale al database"""
    # Verifica la master password
    master_pw = db.query(database1.MasterPassword).first()
    if not master_pw:
        raise HTTPException(status_code=404, detail="Sistema non inizializzato")
    
    if not security1.verify_master_password(master_password, master_pw.password_hash):
        raise HTTPException(status_code=401, detail="Master password errata")
    
    # Controlla se esiste già una credenziale con stessi app_name e username
    existing = db.query(database1.Credential).filter(
        database1.Credential.app_name == cred.app_name.capitalize(),
        database1.Credential.username == cred.username
    ).first()
    
    if existing:
        return {
            "message": "exists",
            "existing_id": existing.id,
            "app_name": existing.app_name,
            "username": existing.username,
            "created_by": existing.created_by
        }
    
    # Recupera il salt
    db_config = db.query(database1.Config).filter(database1.Config.key == "encryption_salt").first()
    salt = db_config.value
    
    # Deriva la chiave di crittografia
    user_key = security1.derive_key(master_password, salt)
    
    # Usa la password fornita o ne genera una nuova
    pw_to_encrypt = cred.password if cred.password else security1.generate_strong_password()
    
    # Cripta la password
    encrypted_pw = security1.encrypt_password(pw_to_encrypt, user_key)
    
    # Salva nel database (con prima lettera maiuscola)
    db_cred = database1.Credential(
        app_name=cred.app_name.capitalize(),
        username=cred.username,
        created_by=cred.created_by.capitalize(),
        encrypted_password=encrypted_pw
    )
    db.add(db_cred)
    db.commit()
    db.refresh(db_cred)
    
    return {
        "message": "created",
        "id": db_cred.id,
        "generated_password": pw_to_encrypt if not cred.password else None
    }

# NUOVO ENDPOINT: Aggiorna credenziale esistente
@app.put("/credentials/{credential_id}")
def update_credential(
    credential_id: int,
    cred_update: CredentialUpdate,
    master_password: str = Header(...),
    db: Session = Depends(get_db)
):
    """Aggiorna la password di una credenziale esistente"""
    # Verifica la master password
    master_pw = db.query(database1.MasterPassword).first()
    if not master_pw:
        raise HTTPException(status_code=404, detail="Sistema non inizializzato")
    
    if not security1.verify_master_password(master_password, master_pw.password_hash):
        raise HTTPException(status_code=401, detail="Master password errata")
    
    # Trova la credenziale
    credential = db.query(database1.Credential).filter(database1.Credential.id == credential_id).first()
    if not credential:
        raise HTTPException(status_code=404, detail="Credenziale non trovata")
    
    # Recupera il salt e deriva la chiave
    db_config = db.query(database1.Config).filter(database1.Config.key == "encryption_salt").first()
    salt = db_config.value
    user_key = security1.derive_key(master_password, salt)
    
    # Usa la password fornita o ne genera una nuova
    pw_to_encrypt = cred_update.password if cred_update.password else security1.generate_strong_password()
    
    # Cripta la nuova password
    encrypted_pw = security1.encrypt_password(pw_to_encrypt, user_key)
    
    # Aggiorna nel database
    credential.encrypted_password = encrypted_pw
    db.commit()
    
    return {
        "message": "updated",
        "id": credential.id,
        "generated_password": pw_to_encrypt if not cred_update.password else None
    }

# ENDPOINT: Lista le credenziali
@app.get("/credentials/")
def list_credentials(
    master_password: str = Header(...),
    app_name: Optional[str] = None, 
    db: Session = Depends(get_db)
):
    """Recupera tutte le credenziali (o filtra per app_name)"""
    # Verifica la master password
    master_pw = db.query(database1.MasterPassword).first()
    if not master_pw:
        raise HTTPException(status_code=404, detail="Sistema non inizializzato")
    
    if not security1.verify_master_password(master_password, master_pw.password_hash):
        raise HTTPException(status_code=401, detail="Master password errata")
    
    # Recupera il salt e deriva la chiave
    db_config = db.query(database1.Config).filter(database1.Config.key == "encryption_salt").first()
    salt = db_config.value
    user_key = security1.derive_key(master_password, salt)
    
    # Query al database
    query = db.query(database1.Credential)
    if app_name:
        query = query.filter(database1.Credential.app_name == app_name)
    
    results = query.all()
    
    # Decripta le password
    try:
        for item in results:
            item.encrypted_password = security1.decrypt_password(item.encrypted_password, user_key)
    except InvalidToken:
        raise HTTPException(status_code=401, detail="Errore nella decrittazione")
    
    return results

@app.delete("/credentials/{credential_id}")
def delete_credential(
    credential_id: int,
    master_password: str = Header(...),
    db: Session = Depends(get_db)
):
    # 1. Verifica la Master Password
    master_pw = db.query(database1.MasterPassword).first()
    if not security1.verify_master_password(master_password, master_pw.password_hash):
        raise HTTPException(status_code=401, detail="Master password errata")
    
    # 2. Trova la credenziale
    credential = db.query(database1.Credential).filter(database1.Credential.id == credential_id).first()
    if not credential:
        raise HTTPException(status_code=404, detail="Credenziale non trovata")
    
    # 3. ELIMINA E CONFERMA
    try:
        db.delete(credential)
        db.commit()  # <--- FONDAMENTALE
        return {"message": "Credenziale eliminata con successo"}
    except Exception as e:
        db.rollback() # In caso di errore, annulla
        raise HTTPException(status_code=500, detail=f"Errore database: {str(e)}")