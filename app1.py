import re
import streamlit as st
import requests

# Configurazione pagina
st.set_page_config(
    page_title="Password Manager",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# URL del backend
BACKEND_URL = "http://127.0.0.1:8000"

def is_valid_password(password):
    """Valida la forza della password"""
    if len(password) < 8:
        return False, "La password deve essere di almeno 8 caratteri."
    if not re.search("[A-Z]", password):
        return False, "La password deve contenere almeno una lettera maiuscola."
    if not re.search("[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "La password deve contenere almeno un carattere speciale."
    return True, ""

# Inizializza sessione
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'master_password' not in st.session_state:
    st.session_state.master_password = None
if 'is_initialized' not in st.session_state:
    try:
        response = requests.get(f"{BACKEND_URL}/status/")
        if response.status_code == 200:
            st.session_state.is_initialized = response.json()["is_initialized"]
        else:
            st.session_state.is_initialized = False
    except:
        st.error("⚠️ Impossibile connettersi al backend. Assicurati che sia in esecuzione.")
        st.stop()

# SCHERMATA AUTENTICAZIONE
if not st.session_state.authenticated:

    with st.sidebar:
        st.markdown("## 📖 Guida Rapida")
        
        with st.expander("🚀 Come Iniziare", expanded=False):
            st.markdown("""
            **Primo Accesso:**
            1. Crea una Master Password sicura
            2. Confermala
            3. Inizia ad aggiungere credenziali!
            """)
        
        with st.expander("➕ Aggiungere Credenziali", expanded=False):
            st.markdown("""
            **Nella colonna sinistra:**
            1. Inserisci nome applicazione (es. "instagram")
            2. Username o email
            3. Il tuo nome
            4. Password (opzionale - se vuoto viene generata)
            
            💡 **Nota**: App e Nome avranno automaticamente la prima lettera maiuscola.
            """)
        
        with st.expander("🔍 Cercare Credenziali", expanded=False):
            st.markdown("""
            **Nella colonna destra:**
            1. Seleziona "Tutte" o un'app specifica
            2. Clicca su "🔎 Cerca"
            3. Espandi i risultati per vedere le password
            """)
        
        with st.expander("🔄 Gestione Duplicati", expanded=False):
            st.markdown("""
            Se inserisci **stessa App + Username**:
            - Vedrai un avviso giallo
            - Puoi **aggiornare** la password esistente
            - Oppure **annullare** l'operazione
            
            ⚠️ Il sistema controlla duplicati solo su **App + Username**, non sul nome autore.
            """)
        
        with st.expander("🔒 Sicurezza", expanded=False):
            st.markdown("""
            **Password Sicure:**
            - Minimo 8 caratteri
            - Almeno 1 maiuscola
            - Almeno 1 carattere speciale
            
            **Crittografia:**
            - Tutte le password sono crittografate con AES-128
            - La Master Password è hashata con PBKDF2
            
            ⚠️ **Non perdere la Master Password!** Non è recuperabile.
            """)
        
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if not st.session_state.is_initialized:
            # PRIMO ACCESSO
            st.markdown("### 👋 Benvenuto!")
            st.info("È il tuo primo accesso. Crea una Master Password sicura.")
            
            with st.form("init_form"):
                new_master_pw = st.text_input(
                    "🔑 Crea la tua Master Password", 
                    type="password",
                    help="Almeno 8 caratteri, una maiuscola e un carattere speciale"
                )
                confirm_master_pw = st.text_input(
                    "🔑 Conferma Master Password", 
                    type="password"
                )
                
                st.markdown("<br>", unsafe_allow_html=True)
                submit = st.form_submit_button("🚀 Inizializza Sistema", use_container_width=True)
                
                if submit:
                    if new_master_pw != confirm_master_pw:
                        st.error("❌ Le password non coincidono!")
                    else:
                        valida, messaggio = is_valid_password(new_master_pw)
                        if not valida:
                            st.error(f"❌ {messaggio}")
                        else:
                            try:
                                response = requests.post(
                                    f"{BACKEND_URL}/initialize/",
                                    json={"master_password": new_master_pw}
                                )
                                if response.status_code == 200:
                                    st.success("✅ Master Password creata con successo!")
                                    st.session_state.is_initialized = True
                                    st.session_state.master_password = new_master_pw
                                    st.session_state.authenticated = True
                                    st.rerun()
                                else:
                                    st.error(f"❌ {response.json().get('detail', 'Errore sconosciuto')}")
                            except Exception as e:
                                st.error(f"⚠️ Errore: {str(e)}")
        else:
            # LOGIN
            st.markdown("### 🔐 Accesso")
            st.info("Inserisci la tua Master Password")
            
            with st.form("login_form"):
                master_pw = st.text_input("🔑 Master Password", type="password")
                
                st.markdown("<br>", unsafe_allow_html=True)
                submit = st.form_submit_button("🔓 Accedi", use_container_width=True)
                
                if submit:
                    try:
                        response = requests.post(
                            f"{BACKEND_URL}/verify/",
                            json={"master_password": master_pw}
                        )
                        if response.status_code == 200:
                            st.success("✅ Accesso effettuato!")
                            st.session_state.authenticated = True
                            st.session_state.master_password = master_pw
                            st.rerun()
                        else:
                            st.error("❌ Master Password errata!")
                    except Exception as e:
                        st.error(f"⚠️ Errore: {str(e)}")

# SCHERMATA PRINCIPALE
else:
    # SIDEBAR CON ISTRUZIONI
    with st.sidebar:
        st.markdown("## 📖 Guida Rapida")
        
        with st.expander("🚀 Come Iniziare", expanded=False):
            st.markdown("""
            **Primo Accesso:**
            1. Crea una Master Password sicura
            2. Confermala
            3. Inizia ad aggiungere credenziali!
            """)
        
        with st.expander("➕ Aggiungere Credenziali", expanded=False):
            st.markdown("""
            **Nella colonna sinistra:**
            1. Inserisci nome applicazione (es. "instagram")
            2. Username o email
            3. Il tuo nome
            4. Password (opzionale - se vuoto viene generata)
            
            💡 **Nota**: App e Nome avranno automaticamente la prima lettera maiuscola.
            """)
        
        with st.expander("🔍 Cercare Credenziali", expanded=False):
            st.markdown("""
            **Nella colonna destra:**
            1. Seleziona "Tutte" o un'app specifica
            2. Clicca su "🔎 Cerca"
            3. Espandi i risultati per vedere le password
            """)
        
        with st.expander("🔄 Gestione Duplicati", expanded=False):
            st.markdown("""
            Se inserisci **stessa App + Username**:
            - Vedrai un avviso giallo
            - Puoi **aggiornare** la password esistente
            - Oppure **annullare** l'operazione
            
            ⚠️ Il sistema controlla duplicati solo su **App + Username**, non sul nome autore.
            """)
        
        with st.expander("🔒 Sicurezza", expanded=False):
            st.markdown("""
            **Password Sicure:**
            - Minimo 8 caratteri
            - Almeno 1 maiuscola
            - Almeno 1 carattere speciale
            
            **Crittografia:**
            - Tutte le password sono crittografate con AES-128
            - La Master Password è hashata con PBKDF2
            
            ⚠️ **Non perdere la Master Password!** Non è recuperabile.
            """)
        

    
    # Header
    col1, col2, col3 = st.columns([2, 3, 1])
    with col3:
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.master_password = None
            st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Layout a due colonne
    col_left, col_right = st.columns([1, 1])
    
    # COLONNA SINISTRA - Aggiungi credenziale
    with col_left:
        st.markdown("### ➕ Aggiungi Credenziale")
        
        # Inizializza variabile per gestione duplicati
        if 'duplicate_detected' not in st.session_state:
            st.session_state.duplicate_detected = None
        
        with st.form("add_credential_form", clear_on_submit=False):
            app_name = st.text_input("📱 Nome Applicazione", placeholder="es. Gmail, Instagram...")
            username = st.text_input("👤 Username / Email", placeholder="esempio@email.com")
            created_by = st.text_input("✍️ Tuo Nome", placeholder="Mario Rossi")
            custom_password = st.text_input(
                "🔒 Password (opzionale)", 
                type="password",
                help="Lascia vuoto per generarla automaticamente. Se la inserisci, deve rispettare i requisiti di sicurezza."
            )
            st.markdown("""
            <div class='password-hint'>
                💡 <b>Se lasci vuoto questo campo, il sistema genererà automaticamente una password sicura.</b><br>
                Se vuoi inserire la tua password, deve rispettare questi criteri:<br>
                • Minimo 8 caratteri<br>
                • Almeno una lettera maiuscola (A-Z)<br>
                • Almeno un carattere speciale (!@#$%^&*(),.?\":{}|&lt;&gt;)
            </div>
            """, unsafe_allow_html=True)
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                submit_cred = st.form_submit_button("💾 Salva", use_container_width=True)
            
            if submit_cred:
                if not app_name or not username or not created_by:
                    st.error("❌ Compila tutti i campi obbligatori!")
                else:
                    # VALIDAZIONE PASSWORD SE FORNITA
                    if custom_password:
                        valida, messaggio = is_valid_password(custom_password)
                        if not valida:
                            st.error(f"❌ {messaggio}")
                        else:
                            # Password valida, procedi
                            try:
                                headers = {"master-password": st.session_state.master_password}
                                payload = {
                                    "app_name": app_name,
                                    "username": username,
                                    "created_by": created_by,
                                    "password": custom_password
                                }
                                
                                response = requests.post(
                                    f"{BACKEND_URL}/credentials/",
                                    headers=headers,
                                    json=payload
                                )
                                
                                if response.status_code == 200:
                                    result = response.json()
                                    
                                    if result.get("message") == "exists":
                                        # SALVA INFO DUPLICATO NEL SESSION_STATE
                                        st.session_state.duplicate_detected = {
                                            "existing_id": result['existing_id'],
                                            "app_name": result['app_name'],
                                            "username": result['username'],
                                            "password": custom_password
                                        }
                                        st.rerun()
                                    
                                    else:
                                        st.success("✅ Credenziale salvata con successo!")
                                        st.session_state.duplicate_detected = None
                                        st.rerun()
                                
                                elif response.status_code == 401:
                                    st.error("❌ Sessione scaduta.")
                                    st.session_state.authenticated = False
                                    st.rerun()
                                else:
                                    st.error(f"❌ Errore: {response.json().get('detail', 'Errore sconosciuto')}")
                            except Exception as e:
                                st.error(f"⚠️ Errore: {str(e)}")
                    else:
                        # Nessuna password fornita, genera automaticamente
                        try:
                            headers = {"master-password": st.session_state.master_password}
                            payload = {
                                "app_name": app_name,
                                "username": username,
                                "created_by": created_by
                            }
                            
                            response = requests.post(
                                f"{BACKEND_URL}/credentials/",
                                headers=headers,
                                json=payload
                            )
                            
                            if response.status_code == 200:
                                result = response.json()
                                
                                if result.get("message") == "exists":
                                    # SALVA INFO DUPLICATO NEL SESSION_STATE (password autogenerata)
                                    st.session_state.duplicate_detected = {
                                        "existing_id": result['existing_id'],
                                        "app_name": result['app_name'],
                                        "username": result['username'],
                                        "password": None  # None = genera automaticamente
                                    }
                                    st.rerun()
                                
                                else:
                                    st.success("✅ Credenziale salvata!")
                                    if result.get("generated_password"):
                                        st.code(result['generated_password'], language=None)
                                        st.warning("⚠️ Copia questa password ora!")
                                    st.session_state.duplicate_detected = None
                                    st.rerun()
                            
                            elif response.status_code == 401:
                                st.error("❌ Sessione scaduta.")
                                st.session_state.authenticated = False
                                st.rerun()
                            else:
                                st.error(f"❌ Errore: {response.json().get('detail', 'Errore')}")
                        except Exception as e:
                            st.error(f"⚠️ Errore: {str(e)}")
        
        # GESTIONE DUPLICATI FUORI DAL FORM
        if st.session_state.duplicate_detected:
            dup = st.session_state.duplicate_detected
            st.warning(f"⚠️ Credenziale già esistente per **{dup['app_name']}** / **{dup['username']}**")
            
            col_update, col_cancel = st.columns(2)
            
            with col_update:
                if st.button("🔄 Aggiorna Password", use_container_width=True, type="primary"):
                    try:
                        headers = {"master-password": st.session_state.master_password}
                        update_payload = {"password": dup['password']} if dup['password'] else {}
                        
                        update_response = requests.put(
                            f"{BACKEND_URL}/credentials/{dup['existing_id']}",
                            headers=headers,
                            json=update_payload
                        )
                        
                        if update_response.status_code == 200:
                            update_result = update_response.json()
                            st.success("✅ Password aggiornata con successo!")
                            if update_result.get("generated_password"):
                                st.code(update_result['generated_password'], language=None)
                                st.warning("⚠️ Copia questa password ora!")
                            st.session_state.duplicate_detected = None
                            st.rerun()
                        else:
                            st.error("❌ Errore nell'aggiornamento")
                    except Exception as e:
                        st.error(f"⚠️ Errore: {str(e)}")
            
            with col_cancel:
                if st.button("❌ Annulla", use_container_width=True):
                    st.session_state.duplicate_detected = None
                    st.rerun()
            
            st.info("💡 Per aggiungerne una nuova con dati diversi, clicca Annulla e cambia username o nome autore")
    
# COLONNA DESTRA - Cerca
    with col_right:
        st.markdown("### 🔍 Cerca Credenziali")
        
        # Inizializza lo stato per i risultati se non esiste
        if 'search_results' not in st.session_state:
            st.session_state.search_results = None

        try:
            # Header per la richiesta iniziale delle app
            headers = {"master-password": st.session_state.master_password}
            apps_response = requests.get(f"{BACKEND_URL}/apps/", headers=headers)
            
            if apps_response.status_code == 200:
                apps_data = apps_response.json()
                app_list = apps_data.get("apps", [])
                
                if app_list:
                    # --- FORM DI RICERCA ---
                    with st.form("search_form"):
                        selected_app = st.selectbox(
                            "📱 Seleziona Applicazione",
                            options=["Tutte"] + app_list,
                            help="Filtra per applicazione"
                        )
                        search_btn = st.form_submit_button("🔎 Cerca", use_container_width=True)
                        st.markdown("<div class='footer'>🔒 Tutte le password sono crittografate end-to-end con AES-128</div>", unsafe_allow_html=True)

                    # --- GESTIONE CLICK "CERCA" ---
                    if search_btn:
                        search_params = {}
                        if selected_app != "Tutte":
                            search_params["app_name"] = selected_app
                        
                        search_response = requests.get(
                            f"{BACKEND_URL}/credentials/",
                            headers=headers,
                            params=search_params
                        )
                        
                        if search_response.status_code == 200:
                            # Salviamo i risultati nel session_state
                            st.session_state.search_results = search_response.json()
                            if not st.session_state.search_results:
                                if selected_app == "Tutte":
                                    st.info("📭 Nessuna credenziale salvata.")
                                else:
                                    st.info(f"📭 Nessuna credenziale per {selected_app}.")
                        elif search_response.status_code == 401:
                            st.error("❌ Sessione scaduta.")
                            st.session_state.authenticated = False
                            st.rerun()

                    # --- VISUALIZZAZIONE ED ELIMINAZIONE ---
                    if st.session_state.search_results:
                        st.success(f"✅ Trovate {len(st.session_state.search_results)} credenziali")
                        
                        # Iteriamo sui risultati
                        for i, cred in enumerate(st.session_state.search_results):
                            with st.expander(f"🔐 {cred['app_name']} - {cred['username']}", expanded=False):
                                st.markdown(f"**👤 Username:** `{cred['username']}`")
                                st.markdown(f"**🔑 Password:**")
                                st.code(cred['encrypted_password'], language=None)
                                st.markdown(f"**✍️ Creato da:** {cred['created_by']}")
                                
                                # --- NUOVO BLOCCO ELIMINAZIONE ---
                                if st.button("🗑️ Elimina", key=f"delete_{cred['id']}"):
                                    # Usiamo lo stesso nome header che si aspetta FastAPI: "master-password"
                                    headers = {"master-password": st.session_state.master_password}
                                    
                                    delete_response = requests.delete(
                                        f"{BACKEND_URL}/credentials/{cred['id']}",
                                        headers=headers
                                    )
                                    
                                    if delete_response.status_code == 200:
                                        st.success("✅ Eliminata correttamente!")
                                        # Rimuoviamo dalla cache locale filtrando via l'ID eliminato
                                        st.session_state.search_results = [c for c in st.session_state.search_results if c['id'] != cred['id']]
                                        st.rerun()
                                    else:
                                        # Mostriamo l'errore esatto che ci dà il server
                                        errore_server = delete_response.json().get('detail', 'Errore sconosciuto')
                                        st.error(f"❌ Errore: {errore_server}")

                else:
                    st.info("📭 Nessuna applicazione salvata. Aggiungi la prima credenziale!")
        
        except Exception as e:
            st.error(f"⚠️ Errore: {str(e)}")