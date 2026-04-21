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
    # Suddividiamo i carboidrati per pasto
    "CARBO_PRANZO": ['Pasta Integrale', 'Riso', 'Farro', 'Gnocchi', 'Cous Cous'],
    "CARBO_CENA": ['Pane Integrale', 'Patate'],
    "OPZIONI_VERD": ['Zucchine', 'Asparagi', 'Spinaci', 'Bieta', 'Finocchi', 'Carote', 'Piselli', 
                     'Insalata', 'Pomodori', 'Peperoni', 'Broccoli', 'Melanzane', 'Fagiolini'],
    "TARGET_PROTEINE": {"Legumi": 4, "Pesce": 3, "Carne Bianca": 3, "Uova": 2},
    "TITOLO": "🥗 Menù Settimanale Salute",
    "BOTTONE_RESET": "🗑️ GENERA NUOVA SETTIMANA"
}

# Uniamo le liste per le selectbox manuali (così l'utente può comunque scegliere tutto)
CONFIG["TUTTI_CARBO"] = sorted(list(set(CONFIG["CARBO_PRANZO"] + CONFIG["CARBO_CENA"])))

# --- 2. LOGICA DI BUSINESS (PURE FUNCTIONS) ---
def get_index_safe(lista, valore):
    try:
        return lista.index(valore)
    except (ValueError, KeyError):
        return 0

def build_protein_pool():
    pool = []
    for prot, count in CONFIG["TARGET_PROTEINE"].items():
        pool.extend([prot] * count)
    mentre_mancano = 14 - len(pool)
    pool.extend(random.choices(list(CONFIG["EMOJI_PROT"].keys()), k=mentre_mancano))
    random.shuffle(pool)
    return pool

def genera_pasti(pasti_esistenti=None):
    giorni = ['Lunedì', 'Martedì', 'Mercoledì', 'Giovedì', 'Venerdì', 'Sabato', 'Domenica']
    prot_pool = build_protein_pool()
    
    nuovi_pasti = []
    for i in range(14):
        tipo_pasto = "Pranzo" if i%2 == 0 else "Cena"
        
        if pasti_esistenti and i < len(pasti_esistenti) and pasti_esistenti[i].get('locked'):
            nuovi_pasti.append(pasti_esistenti[i])
            if pasti_esistenti[i]['prot'] in prot_pool:
                prot_pool.remove(pasti_esistenti[i]['prot'])
        else:
            # SCELTA AUTOMATICA: Pasta/Cereali a pranzo, Pane/Patate a cena
            if tipo_pasto == "Pranzo":
                carbo_scelto = random.choice(CONFIG["CARBO_PRANZO"])
            else:
                carbo_scelto = random.choice(CONFIG["CARBO_CENA"])

            nuovi_pasti.append({
                "id": i,
                "giorno": giorni[i//2],
                "tipo": tipo_pasto,
                "prot": prot_pool.pop() if prot_pool else random.choice(list(CONFIG["EMOJI_PROT"].keys())),
                "carbo": carbo_scelto,
                "verd": random.choice(CONFIG["OPZIONI_VERD"]),
                "locked": False
            })
    return nuovi_pasti

def scambia_pasti(idx1, idx2):
    campi = ['prot', 'carbo', 'verd', 'locked']
    for campo in campi:
        st.session_state.pasti[idx1][campo], st.session_state.pasti[idx2][campo] = \
        st.session_state.pasti[idx2][campo], st.session_state.pasti[idx1][campo]
    st.session_state.scambio_idx = None
    save_data(st.session_state.pasti)

# --- 3. DATA PERSISTENCE ---
def load_data():
    if os.path.exists(CONFIG["FILE_SALVATAGGIO"]):
        try:
            return pd.read_csv(CONFIG["FILE_SALVATAGGIO"]).to_dict('records')
        except:
            return genera_pasti()
    return genera_pasti()

def save_data(pasti):
    pd.DataFrame(pasti).to_csv(CONFIG["FILE_SALVATAGGIO"], index=False)

# --- 4. COMPONENTI UI ---
def render_header():
    st.title(CONFIG["TITOLO"])
    if st.session_state.scambio_idx is not None:
        p1 = st.session_state.pasti[st.session_state.scambio_idx]
        st.warning(f"🔄 Selezionato: **{p1['giorno']} ({p1['tipo']})**. Clicca 'SPOSTA QUI' su un altro pasto.")
        if st.button("Annulla Spostamento"):
            st.session_state.scambio_idx = None
            st.rerun()
    
    if st.button(CONFIG["BOTTONE_RESET"], use_container_width=True):
        st.session_state.pasti = genera_pasti(st.session_state.pasti)
        st.session_state.menu_key = str(uuid.uuid4())
        save_data(st.session_state.pasti)
        st.rerun()

def render_pasto_editor(idx):
    pasto = st.session_state.pasti[idx]
    is_selezionato = (st.session_state.scambio_idx == idx)
    
    with st.container(border=True):
        st.markdown(f"**{'☀️' if pasto['tipo'] == 'Pranzo' else '🌙'} {pasto['tipo']}**")
        
        new_p = st.selectbox("Proteina", list(CONFIG["EMOJI_PROT"].keys()), 
                             index=get_index_safe(list(CONFIG["EMOJI_PROT"].keys()), pasto['prot']),
                             key=f"p_{idx}_{st.session_state.menu_key}")
        
        # Qui usiamo TUTTI_CARBO perché manualmente l'utente deve poter scegliere tutto
        new_c = st.selectbox("Cereale", CONFIG["TUTTI_CARBO"], 
                             index=get_index_safe(CONFIG["TUTTI_CARBO"], pasto['carbo']),
                             key=f"c_{idx}_{st.session_state.menu_key}")
        
        new_v = st.selectbox("Verdura", CONFIG["OPZIONI_VERD"], 
                             index=get_index_safe(CONFIG["OPZIONI_VERD"], pasto['verd']),
                             key=f"v_{idx}_{st.session_state.menu_key}")
        
        c1, c2 = st.columns(2)
        new_l = c1.checkbox("Blocca", value=bool(pasto['locked']), key=f"l_{idx}_{st.session_state.menu_key}")
        
        label_sposta = "📍 QUI" if is_selezionato else "↔️ SPOSTA"
        if c2.button(label_sposta, key=f"mv_{idx}_{st.session_state.menu_key}", use_container_width=True):
            if st.session_state.scambio_idx is None:
                st.session_state.scambio_idx = idx
                st.rerun()
            elif st.session_state.scambio_idx == idx:
                st.session_state.scambio_idx = None
                st.rerun()
            else:
                scambia_pasti(st.session_state.scambio_idx, idx)
                st.rerun()

        if (new_p != pasto['prot'] or new_c != pasto['carbo'] or 
            new_v != pasto['verd'] or new_l != pasto['locked']):
            st.session_state.pasti[idx].update({"prot": new_p, "carbo": new_c, "verd": new_v, "locked": new_l})
            save_data(st.session_state.pasti)

def render_statistiche():
    st.divider()
    st.subheader("📊 Bilancio Settimanale Target")
    all_prots = [p['prot'] for p in st.session_state.pasti]
    cols = st.columns(len(CONFIG["TARGET_PROTEINE"]))
    for i, (nome, target) in enumerate(CONFIG["TARGET_PROTEINE"].items()):
        attuale = all_prots.count(nome)
        delta = attuale - target
        emoji = CONFIG["EMOJI_PROT"][nome]
        cols[i].metric(f"{emoji} {nome}", f"{attuale}/{target}", delta=delta)

# --- 5. MAIN APP ---
def main():
    st.set_page_config(page_title="Menù Salute", page_icon="🥗", layout="wide")
    
    if 'menu_key' not in st.session_state:
        st.session_state.menu_key = str(uuid.uuid4())
    if 'pasti' not in st.session_state:
        st.session_state.pasti = load_data()
    if 'scambio_idx' not in st.session_state:
        st.session_state.scambio_idx = None

    render_header()

    giorni_it = ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"]
    oggi_nome = giorni_it[datetime.now().weekday()]

    for g_nome in giorni_it:
        is_oggi = (g_nome == oggi_nome)
        with st.expander(f"{'📍 ' if is_oggi else ''}{g_nome.upper()}", expanded=is_oggi):
            idx_pasti = [i for i, p in enumerate(st.session_state.pasti) if p['giorno'] == g_nome]
            col_sx, col_dx = st.columns(2)
            with col_sx: render_pasto_editor(idx_pasti[0])
            with col_dx: render_pasto_editor(idx_pasti[1])

    render_statistiche()

if __name__ == "__main__":
    main()
