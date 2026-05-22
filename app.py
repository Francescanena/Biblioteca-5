import streamlit as st
import pandas as pd

# 1. Configurazione della pagina web
st.set_page_config(
    page_title="Gestione Biblioteca - Moduli Sincronizzati",
    page_icon="📚",
    layout="wide"
)

# 2. Inizializzazione dello stato della memoria (Session State)
# Centralizziamo i dati dei moduli in un dizionario globale per la sincronizzazione automatica
if 'database_moduli' not in st.session_state:
    # Struttura: {"Nome Modulo": ["Tipologia", Peso]}
    st.session_state.database_moduli = {
        "Modulo 1": ["Tipologia A (Enciclopedie)", 40.0],
        "Modulo 2": ["Tipologia B (Riviste)", 25.0],
        "Modulo 3": ["Tipologia E (Fascicoli)", 120.0],
        "Modulo 4": ["Tipologia H (Archivio)", 300.0],
    }

if 'flotta_scaffali' not in st.session_state:
    # Ogni scaffale definisce quanti ripiani ha e l'elenco dei NOMI dei moduli associati a ogni colonna
    st.session_state.flotta_scaffali = {
        'Scaffale "Libri Storici"': {
            'ripiani': 4,
            'lunghezza_modulo': 2.0,
            'tara': 80.0,
            # Lista dei moduli assegnati alle colonne (dalla colonna 1 alla colonna N)
            'moduli_assegnati': ["Modulo 1", "Modulo 2", "Modulo 3"]
        },
        'Scaffale "Narrativa Moderna"': {
            'ripiani': 3,
            'lunghezza_modulo': 1.5,
            'tara': 60.0,
            # Questo scaffale riutilizza "Modulo 2" e "Modulo 1", sincronizzandoli!
            'moduli_assegnati': ["Modulo 2", "Modulo 1", "Modulo 4"]
        }
    }

# Funzione di utilità per garantire che un modulo esista nel database globale
def garantisci_esistenza_modulo(nome_mod):
    if nome_mod not in st.session_state.database_moduli:
        st.session_state.database_moduli[nome_mod] = ["Vuoto", 0.0]


# 3. BARRA LATERALE (Sidebar) - CREAZIONE NUOVI SCAFFALI
st.sidebar.header("➕ Aggiungi Nuovo Scaffale")
with st.sidebar.form("form_nuovo_scaffale", clear_on_submit=True):
    nuovo_nome = st.text_input("Nome dello scaffale")
    nuovo_ripiani = st.number_input("Numero di Ripiani (Uguale per tutti i moduli di questo scaffale)", min_value=1, max_value=20, value=4)
    nuova_lunghezza = st.number_input("Lunghezza modulo (m)", min_value=0.5, value=2.0, step=0.5)
    nuova_tara = st.number_input("Tara struttura (kg)", min_value=0.0, value=80.0, step=5.0)
    
    st.markdown("**Assegnazione Moduli:** Spiega quali moduli compongono le colonne (separati da virgola)")
    moduli_input = st.text_input("Es: Modulo 1, Modulo 2, Modulo 5", value="Modulo 1, Modulo 2")
    
    crea_scaffale = st.form_submit_button("Crea Scaffale")
    if crea_scaffale:
        lista_moduli = [m.strip() for m in moduli_input.split(",") if m.strip()]
        
        if not nuovo_nome.strip():
            st.sidebar.error("Inserisci un nome valido per lo scaffale!")
        elif nuovo_nome in st.session_state.flotta_scaffali:
            st.sidebar.error("Uno scaffale con questo nome esiste già!")
        elif not lista_moduli:
            st.sidebar.error("Devi inserire almeno un modulo!")
        else:
            # Assicurati che tutti i moduli inseriti esistano nel database globale
            for m in lista_moduli:
                garantisci_esistenza_modulo(m)
                
            st.session_state.flotta_scaffali[nuovo_nome] = {
                'ripiani': nuovo_ripiani,
                'lunghezza_modulo': nuova_lunghezza,
                'tara': nuova_tara,
                'moduli_assegnati': lista_moduli
            }
            st.sidebar.success(f"✓ '{nuovo_nome}' creato con successo!")
            st.rerun()

st.sidebar.markdown("---")
st.sidebar.subheader("🗑️ Elimina Scaffale")
scaffale_da_eliminare = st.sidebar.selectbox("Seleziona scaffale da rimuovere", ["---"] + list(st.session_state.flotta_scaffali.keys()))
if scaffale_da_eliminare != "---":
    if st.sidebar.button("Conferma Eliminazione", type="primary"):
        del st.session_state.flotta_scaffali[scaffale_da_eliminare]
        st.sidebar.success(f"Eliminato {scaffale_da_eliminare}")
        st.rerun()


# 4. CORPO PRINCIPALE
st.title("📚 Gestione Scaffalature con Moduli Sincronizzati")
st.caption("I moduli con lo stesso nome condividono automaticamente lo stesso materiale e lo stesso peso su tutta la flotta.")

lista_scaffali = list(st.session_state.flotta_scaffali.keys())
if not lista_scaffali:
    st.info("Nessuno scaffale presente. Creane uno dalla barra laterale!")
else:
    # Selezione dello scaffale attivo
    scaffale_attivo = st.selectbox("📂 Seleziona lo Scaffale da monitorare:", lista_scaffali)
    
    scaf_corrente = st.session_state.flotta_scaffali[scaffale_attivo]
    r_tot = scaf_corrente['ripiani']
    moduli_scaf = scaf_corrente['moduli_assegnati']
    m_tot = len(moduli_scaf)
    
    st.write(f"Configurazione: **{r_tot} Ripiani** × **{m_tot} Colonne Modulo** | Lunghezza modulo: **{scaf_corrente['lunghezza_modulo']}m** | Tara: **{scaf_corrente['tara']} kg**")
    
    tab_mappa, tab_modifica_moduli = st.tabs(["👁️ Mappa Scaffale & Report Pesi", "✏️ Modifica Dati dei Moduli"])
    
    with tab_mappa:
        # Costruzione della griglia visuale (righe = ripiani, colonne = moduli assegnati)
        righe_tabella = []
        # Nota: Poiché il peso e il materiale sono legati al modulo, ogni ripiano di quella colonna 
        # mostra lo stesso materiale e lo stesso peso (come richiesto)
        for r in range(r_tot - 1, -1, -1):
            info_riga = {}
            for m_idx, nome_mod in enumerate(moduli_scaf):
                tipologia, peso = st.session_state.database_moduli[nome_mod]
                info_riga[f"Colonna {m_idx+1}: {nome_mod}"] = f"[{tipologia}] {peso} kg"
            righe_tabella.append(info_riga)
            
        indici_verticali = [f"Ripiano {i}" for i in range(r_tot, 0, -1)]
        df_visivo = pd.DataFrame(righe_tabella, index=indici_verticali)
        st.dataframe(df_visivo, use_container_width=True)
        
        # --- CALCOLO DEI PESI ---
        # Peso del singolo scaffale = (Somma pesi dei suoi moduli * numero ripiani) + tara
        peso_merce_singolo = sum(st.session_state.database_moduli[nome_mod][1] for nome_mod in moduli_scaf) * r_tot
        peso_complessivo_singolo = peso_merce_singolo + scaf_corrente['tara']
        
        # Peso globale della flotta
        peso_merce_flotta = 0.0
        tara_flotta = 0.0
        for nome, s in st.session_state.flotta_scaffali.items():
            peso_merce_scaf = sum(st.session_state.database_moduli[n_mod][1] for n_mod in s['moduli_assegnati']) * s['ripiani']
            peso_merce_flotta += peso_merce_scaf
            tara_flotta += s['tara']
        peso_complessivo_flotta = peso_merce_flotta + tara_flotta
        
        st.markdown("---")
        st.subheader("📊 Report Calcolo Pesi")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Questo Scaffale ({scaffale_attivo}):**")
            st.write(f"• Peso totale merci stoccate: {peso_merce_singolo:,.1f} kg")
            st.write(f"• Peso totale struttura + merci: **{peso_complessivo_singolo:,.1f} kg**")
        with col2:
            st.markdown(f"**Flotta Intera ({len(lista_scaffali)} Scaffali attivi):**")
            st.write(f"• Peso merce complessivo in biblioteca: {peso_merce_flotta:,.1f} kg")
            st.markdown(f"<div style='background-color:#e2f0d9; padding:10px; border-radius:5px;'><b>PESO COMPLESSIVO FLOTTA: {peso_complessivo_flotta:,.1f} kg</b><br><small>Tara complessiva strutture: {tara_flotta} kg</small></div>", unsafe_allow_html=True)

    with tab_modifica_moduli:
        st.subheader("✏️ Editor dei Moduli Centralizzato")
        st.write("Modificando un modulo qui sotto, i cambiamenti si applicheranno a tutti i ripiani e a tutti gli scaffali in cui quel modulo è presente.")
        
        # Permette di scegliere quale modulo modificare tra tutti quelli esistenti nel sistema
        modulo_da_modificare = st.selectbox("Seleziona il Modulo da modificare:", list(st.session_state.database_moduli.keys()))
        
        tipo_att, peso_att = st.session_state.database_moduli[modulo_da_modificare]
        
        with st.form("form_modifica_modulo"):
            nuovo_tipo = st.text_input("Tipologia materiale / Categoria libri", value=tipo_att)
            nuovo_peso = st.number_input("Peso del materiale per singolo livello (kg)", min_value=0.0, value=float(peso_att), step=5.0)
            
            pulsante_salva = st.form_submit_button("Salva e Sincronizza Modulo")
            if pulsante_salva:
                # Aggiornamento nel database globale
                st.session_state.database_moduli[modulo_da_modificare] = [nuovo_tipo, nuovo_peso]
                st.success(f"✓ {modulo_da_modificare} aggiornato! Le modifiche sono state propagate a ogni scaffale corrispondente.")
                st.rerun()
