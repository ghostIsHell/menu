import streamlit as st
import random
import pandas as pd
import os
import uuid
from datetime import datetime

# --- 1. COSTANTI E CONFIGURAZIONE ---
CONFIG = {
    "FILE_SALVATAGGIO": "menu_stato.csv",
    "EMOJI_PROT": {
        'Pesce': '🔵', 'Legumi': '🟢', 'Carne Bianca': '🟡', 
        'Uova': '🔴', 'Formaggio': '⚪', 'Carne Rossa': '🟣'
    },
    "OPZIONI_CARBO": ['Pasta Integrale', 'Riso', 'Farro', 'Gnocchi', 'Cous Cous', 'Pane Integrale', 'Patate'],
    "OPZIONI_VERD": ['Zucchine', 'Asparagi', 'Spinaci', 'Bieta', 'Finocchi', 'Carote', 'Piselli', 
                     'Insalata', 'Pomodori', 'Peperoni', 'Broccoli', 'Melanzane', 'Fagiolini'],
    "TARGET_PROTEINE": {"Legumi": 4, "Pesce": 3, "Carne Bianca": 3, "Uova": 2},
    "TITOLO": "🥗 Menù Settimanale",
    "BOTTONE_RESET": "🗑️ RESET SETTIMANA"
}

# --- 2. LOGICA DI BUSINESS (PURE FUNCTIONS) ---
def build_protein_pool():
    """Crea la lista di proteine basata sui target settimanali."""
    pool = []
    for prot, count in CONFIG["TARGET_PROTEINE"].items():
        pool.extend([prot] * count)
    # Aggiungiamo extra per coprire i 14 pasti
    mentre_mancano = 14 - len(pool)
    pool.extend(random.choices(list(CONFIG["EMOJI_PROT"].keys()), k=mentre_mancano))
    random.shuffle(pool)
    return pool

def genera_pasti(pasti_esistenti=None):
    """Genera la struttura della settimana rispettando i blocchi."""
    giorni = ['Lunedì', 'Martedì', 'Mercoledì', 'Giovedì', 'Venerdì', 'Sabato', 'Domenica']
    prot_pool = build_protein_pool()
    
    nuovi_pasti = []
    for i in range(14):
        # Se il pasto è bloccato, lo manteniamo così com'è
        if pasti_esistenti and i < len(pasti_esistenti) and pasti_esistenti[i].get('locked'):
            nuovi_pasti.append(pasti_esistenti[i])
            # Rimuoviamo la proteina usata dal pool se presente per bilanciare le rimanenti
            if pasti_esistenti[i]['prot'] in prot_pool:
                prot_pool.remove(pasti_esistenti[i]['prot'])
        else:
            nuovi_pasti.append({
                "id": i,
                "giorno": giorni[i//2],
                "tipo": "Pranzo" if i%2 == 0 else "Cena",
                "prot": prot_pool.pop() if prot_pool else random.choice(list(CONFIG["EMOJI_PROT"].keys())),
                "carbo": random.choice(CONFIG["OPZIONI_CARBO"]),
                "verd": random.choice(CONFIG["OPZIONI_VERD"]),
                "locked": False
            })
    return nuovi_pasti

# --- 3. DATA PERSISTENCE (STORAGE) ---
def load_data():
    if os.path.exists(CONFIG["FILE_SALVATAGGIO"]):
        return pd.read_csv(CONFIG["FILE_SALVATAGGIO"]).to_dict('records')
    return genera_pasti()

def save_data(pasti):
    pd.DataFrame(pasti).to_csv(CONFIG["FILE_SALVATAGGIO"], index=False)

# --- 4. COMPONENTI UI (UI MODULES) ---
def render_header():
    st.title(CONFIG["TITOLO"])
    if st.button(CONFIG["BOTTONE_RESET"], use_container_width=True):
        st.session_state.pasti = genera_pasti(st.session_state.pasti)
        st.session_state.menu_key = str(uuid.uuid4())
        save_data(st.session_state.pasti)
        st.rerun()

def render_pasto_editor(idx):
    pasto = st.session_state.pasti[idx]
    with st.container():
        st.markdown(f"**{'☀️' if pasto['tipo'] == 'Pranzo' else '🌙'} {pasto['tipo']}**")
        
        # Widget compatti
        c1, c2 = st.columns(2)
        new_p = c1.selectbox("Proteina", list(CONFIG["EMOJI_PROT"].keys()), 
                             index=list(CONFIG["EMOJI_PROT"].keys()).index(pasto['prot']),
                             key=f"p_{idx}_{st.session_state.menu_key}")
        new_c = c2.selectbox("Carbo", CONFIG["OPZIONI_CARBO"], 
                             index=CONFIG["OPZIONI_CARBO"].index(pasto['carbo']),
                             key=f"c_{idx}_{st.session_state.menu_key}")
        
        new_v = st.selectbox("Verdura", CONFIG["OPZIONI_VERD"], 
                             index=CONFIG["OPZIONI_VERD"].index(pasto['verd']),
                             key=f"v_{idx}_{st.session_state.menu_key}")
        
        new_l = st.checkbox("Blocca", value=pasto['locked'], key=f"l_{idx}_{st.session_state.menu_key}")

        # Sync se i dati cambiano
        if (new_p != pasto['prot'] or new_c != pasto['carbo'] or 
            new_v != pasto['verd'] or new_l != pasto['locked']):
            st.session_state.pasti[idx].update({"prot": new_p, "carbo": new_c, "verd": new_v, "locked": new_l})
            save_data(st.session_state.pasti)

def render_statistiche():
    st.divider()
    st.subheader("📊 Bilancio Settimanale")
    all_prots = [p['prot'] for p in st.session_state.pasti]
    cols = st.columns(len(CONFIG["TARGET_PROTEINE"]))
    
    for i, (nome, target) in enumerate(CONFIG["TARGET_PROTEINE"].items()):
        attuale = all_prots.count(nome)
        delta = attuale - target
        emoji = CONFIG["EMOJI_PROT"][nome]
        cols[i].metric(f"{emoji} {nome}", f"{attuale}/{target}", delta=delta)

# --- 5. MAIN APP CYCLE ---
def main():
    st.set_page_config(page_title="Menù Salute", page_icon="🥗", layout="wide")
    
    # Inizializzazione Session State
    if 'menu_key' not in st.session_state:
        st.session_state.menu_key = str(uuid.uuid4())
    if 'pasti' not in st.session_state:
        st.session_state.pasti = load_data()

    render_header()

    # Layout Giorni
    giorni = {p['giorno'] for p in st.session_state.pasti}
    oggi = giorni_it = {0: "Lunedì", 1: "Martedì", 2: "Mercoledì", 3: "Giovedì", 4: "Venerdì", 5: "Sabato", 6: "Domenica"}[datetime.now().weekday()]

    for g_nome in ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"]:
        with st.expander(f"📅 {g_nome.upper()}", expanded=(g_nome == oggi)):
            # Filtriamo i pasti per quel giorno
            idx_pasti = [i for i, p in enumerate(st.session_state.pasti) if p['giorno'] == g_nome]
            col_sx, col_dx = st.columns(2)
            with col_sx: render_pasto_editor(idx_pasti[0])
            with col_dx: render_pasto_editor(idx_pasti[1])

    render_statistiche()

if __name__ == "__main__":
    main()
