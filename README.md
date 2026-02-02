# 🔐 Modern Password Manager (Full-Stack Desktop App)

Un gestore di password robusto, sicuro e portabile, sviluppato con un'architettura **Full-Stack** moderna che unisce la velocità di **FastAPI** all'eleganza di **Streamlit**. L'intera applicazione viene distribuita come un unico file eseguibile grazie a **PyInstaller**.

---

## ✨ Caratteristiche Principali

* **Architettura Ibrida:** Utilizza un backend API (FastAPI) e un frontend reattivo (Streamlit) che comunicano localmente.
* **Sicurezza di Grado Militare:**
    * Crittografia **AES-256** simmetrica (Fernet).
    * Derivazione delle chiavi tramite **PBKDF2HMAC** (SHA-256) con 480.000 iterazioni.
    * **Salting dinamico** generato univocamente al primo avvio.
* **Zero Installazione per l'utente:** Database SQLite auto-configurato che viene creato nella stessa cartella dell'eseguibile.
* **Interfaccia Professionale:** UI pulita con supporto nativo al tema scuro (Dark Mode).
* **Portabilità Totale:** Un unico file `.exe` senza necessità di installare Python sul PC di destinazione.

---

## 📂 Struttura del Software

Il progetto è modulare per garantire massima sicurezza e facilità di manutenzione:

| File | Funzione |
| :--- | :--- |
| `launcher.py` | **Entry Point:** Avvia simultaneamente il server API e l'interfaccia grafica. |
| `main1.py` | **Backend (FastAPI):** Gestisce le rotte API, l'autenticazione e la logica core. |
| `app1.py` | **Frontend (Streamlit):** L'interfaccia utente grafica. |
| `security1.py` | **Security Layer:** Gestisce crittografia, hashing e generazione chiavi. |
| `database1.py` | **Data Layer:** Modelli SQLAlchemy e gestione del file SQLite. |
| `builder.py` | **Build Script:** Automatizza la creazione dell'eseguibile e l'inclusione delle risorse. |

---

## 🛠️ Requisiti e Dipendenze

Per eseguire o compilare il progetto, è necessario **Python 3.12+** (consigliata 3.12 per massima stabilità con PyInstaller).

### Librerie necessarie:
Installa tutte le dipendenze con un unico comando:
```bash
pip install streamlit fastapi uvicorn sqlalchemy cryptography requests pyinstaller

---

## 📦 Come Creare l'Eseguibile (.exe)

Per generare il file unico pronto all'uso, segui questi passaggi:

1. **Prepara l'icona:** Assicurati di avere il file dell'icona (`icona.ico`) nella cartella principale del progetto.
2. **Esegui lo script di compilazione:**
   ```bash
   python builder.py

---

## 🔒 Note sulla Sicurezza

* **Master Password:** Viene salvata esclusivamente come hash salato tramite l'algoritmo **PBKDF2**. Se la password viene smarrita, i dati salvati non potranno essere recuperati in alcun modo, poiché la chiave di decrittazione deriva direttamente da essa.
* **Isolamento Localhost:** Il backend FastAPI è configurato per restare in ascolto solo sull'indirizzo di loopback `127.0.0.1`. Questo garantisce che il servizio sia inaccessibile da altri dispositivi nella stessa rete locale (LAN).
* **Privacy Totale:** L'applicazione è rigorosamente offline. Nessun dato, statistica o credenziale viene inviato a server esterni. Il database SQLite rimane confinato esclusivamente sul tuo disco locale.

---
Generato con ❤️ per una gestione sicura delle credenziali.
