import threading
import uvicorn
import sys
import os
from streamlit.web import cli as stcli
import main1  # Importa il tuo file FastAPI

def resolve_path(path):
    if getattr(sys, "frozen", False):
        basedir = sys._MEIPASS
    else:
        basedir = os.path.dirname(__file__)
    return os.path.join(basedir, path)

def run_api():
    # Avvia FastAPI su una porta specifica
    uvicorn.run(main1.app, host="127.0.0.1", port=8000, log_level="error")

def run_streamlit():
    # Costruiamo il percorso assoluto per app1.py
    app_path = resolve_path("app1.py")
    
    # Trucco: manipoliamo sys.argv per far credere a Streamlit di essere stato lanciato da terminale
    sys.argv = [
        "streamlit",
        "run",
        app_path,
        "--global.developmentMode=false",
        "--server.headless=true",
    ]
    sys.exit(stcli.main())

if __name__ == "__main__":
    # 1. Avvia il backend in un thread separato (daemon=True così si chiude quando chiudi l'app)
    api_thread = threading.Thread(target=run_api, daemon=True)
    api_thread.start()

    # 2. Avvia Streamlit nel thread principale (è bloccante)
    run_streamlit()