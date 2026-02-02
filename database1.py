import os
import sys
from sqlalchemy import create_engine, Column, Integer, String, LargeBinary, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker

# Questa funzione serve a trovare la cartella dove si trova l'EXE
def get_application_path():
    # Se il programma è "congelato" (cioè è un EXE)
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    # Se stiamo eseguendo il file .py normalmente
    return os.path.dirname(os.path.abspath(__file__))

# Costruiamo il percorso assoluto per il database
# Così verrà creato sempre ACCANTO al file .exe
db_path = os.path.join(get_application_path(), "passwords.db")

# Configurazione del Database usando il percorso calcolato
DATABASE_URL = f"sqlite:///{db_path}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
# 2. Creiamo la sessione (il canale di comunicazione)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 3. La base per i nostri modelli
Base = declarative_base()

# 4. DEFINIZIONE DELLA TABELLA CREDENTIALS
class Credential(Base):
    __tablename__ = "credentials"
    id = Column(Integer, primary_key=True, index=True)
    
    # app_name, username, created_by, encrypted_password
    app_name = Column(String, index=True)
    username = Column(String, index=True)
    created_by = Column(String, index=True)
    encrypted_password = Column(String)

# 5. TABELLA CONFIG (per salt e altre configurazioni)
class Config(Base):
    __tablename__ = "config"
    key = Column(String, primary_key=True, index=True)
    value = Column(LargeBinary)

# 6. NUOVA TABELLA PER LA MASTER PASSWORD
class MasterPassword(Base):
    __tablename__ = "master_password"
    id = Column(Integer, primary_key=True, index=True)
    password_hash = Column(LargeBinary)  # Hash della master password
    is_initialized = Column(Boolean, default=True)

Base.metadata.create_all(bind=engine)