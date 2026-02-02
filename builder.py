import PyInstaller.__main__
import os
import sys
from PyInstaller.utils.hooks import collect_all

def build():
    # 1. Rileva il sistema operativo per il separatore dei percorsi
    # Windows usa ';', Linux/Mac usano ':'
    sep = ';' if sys.platform == "win32" else ':'

    # 2. Raccoglie tutti i file necessari di Streamlit, Altair, ecc.
    # Streamlit ha bisogno di molti file statici (html, js, css) che PyInstaller non vede
    tmp_ret = collect_all('streamlit')
    datas = tmp_ret[0]
    binaries = tmp_ret[1]
    hiddenimports = tmp_ret[2]

    # Aggiungi anche i dati per altre librerie critiche se necessario
    # tmp_ret_uvicorn = collect_all('uvicorn') ... (spesso non serve collect_all per uvicorn, basta hiddenimport)

    # 3. Aggiungi il tuo file frontend (app1.py) come dato
    # Sintassi: ('file_origine', 'cartella_destinazione_interna')
    datas.append(('app1.py', '.'))
    datas.append(('.streamlit/config.toml', '.streamlit'))

    # 4. Aggiungi import nascosti che PyInstaller potrebbe perdere
    hiddenimports += [
        'uvicorn.logging',
        'uvicorn.loops',
        'uvicorn.loops.auto',
        'uvicorn.protocols',
        'uvicorn.protocols.http',
        'uvicorn.protocols.http.auto',
        'uvicorn.protocols.websockets',
        'uvicorn.protocols.websockets.auto',
        'uvicorn.lifespan',
        'uvicorn.lifespan.on',
        'fastapi.applications',
        'sqlalchemy.sql.default_comparator',
        'sqlite3'
    ]

    # 5. Costruisci i comandi per PyInstaller
    args = [
        'launcher.py',                  # Il file principale da avviare
        '--onefile',                    # Crea un unico file .exe
        '--name=PasswordManager',       # Nome del file finale
        '--clean',                      # Pulisci la cache prima di costruire
        '--icon=icona.ico',               # Icona dell'applicazione
        
        # Opzione windowed: nasconde la console nera su Windows.
        # Rimuovilo se vuoi vedere i log di errore (utile per il debug iniziale)
        # '--windowed', 
    ]

    # Aggiungi i dati raccolti (risorse di streamlit + app1.py)
    for src, dest in datas:
        args.append(f'--add-data={src}{sep}{dest}')

    # Aggiungi gli import nascosti
    for hidden in hiddenimports:
        args.append(f'--hidden-import={hidden}')

    # Esegui PyInstaller
    print("🚀 Avvio compilazione... Potrebbe richiedere qualche minuto.")
    PyInstaller.__main__.run(args)

if __name__ == "__main__":
    build()