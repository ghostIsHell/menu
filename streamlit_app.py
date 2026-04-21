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
    "CARBO_PRANZO": ['Pasta Integrale', 'Riso', 'Farro', 'Gnocchi', 'Cous Cous'],
    "CARBO_CENA": ['Pane Integrale', 'Patate'],
    "OPZIONI_VERD": ['Zucchine', 'Asparagi', 'Spinaci', 'Bieta', 'Finocchi', 'Carote', 'Piselli', 
                     'Insalata', 'Pomodori', 'Peperoni', 'Broccoli', 'Melanzane', 'Fagiolini'],
    "TARGET_PROTEINE": {"Legumi": 4, "Pesce": 3, "Carne Bianca": 3, "Uova": 2},
    "TITOLO": "🥗 Menù Settimanale Salute",
    "BOTTONE_RESET": "🗑️ GENERA NUOVA SETTIMANA"
}
CONFIG["TUTTI_CARBO"] = sorted(list(set(CONFIG["CARBO_PRANZO"] + CONFIG["CARBO_CENA"])))

# --- 2. LOGICA DI BUSINESS ---
def get_index_safe(lista, valore):
    try: return lista.index(valore)
    except: return 0

def build_protein_pool():
    pool = []
    for prot, count in CONFIG["TARGET_PROTEINE"].items():
        pool.extend([prot] * count)
    pool.extend(random.choices(list(CONFIG["EMOJI_PROT"].keys()), k=(14-len(pool))))
    random.shuffle(pool)
    return pool

def genera_pasti(pasti_esistenti=None):
    giorni = ['Lunedì', 'Martedì', 'Mercoledì', 'Giovedì', 'Venerdì', 'Sabato', 'Domenica']
    prot_pool = build_protein_pool()
    nuovi_pasti = []
    for i in range(14):
        tipo = "Pranzo" if i%2 == 0 else "Cena"
        if pasti_esistenti and i < len(pasti_esistenti) and pasti_esistenti[i].get('locked'):
            nuovi_pasti.append(pasti_esistenti[i])
            if pasti_esistenti[i]['prot'] in prot_pool: prot_pool.remove(pasti_esistenti[i]['prot'])
        else:
            carbo = random.choice(CONFIG["CARBO_PRANZO"] if tipo == "Pranzo" else CONFIG["CARBO_CENA"])
            nuovi_pasti.append({
                "id": i, "giorno": giorni[i//2], "tipo": tipo,
                "prot": prot_pool.pop() if prot_pool else random.choice(list(CONFIG["EMOJI_PROT"].keys())),
                "carbo": carbo, "verd": random.choice(CONFIG["OPZIONI_VERD"]), "locked": False
            })
    return nuovi_pasti

# --- 3. DATA PERSISTENCE ---
def load_data():
    if os.path.exists(CONFIG["FILE_SALVATAGGIO"]):
        try: return pd.read_csv(CONFIG["FILE_SALVATAGGIO"]).to_dict('records')
        except: return genera_pasti()
    return genera_pasti()

def save_data():
    pd.DataFrame(st.session_state.pasti).to_csv(CONFIG["FILE_SALVATAGGIO"], index=False)

# --- 4. COMPONENTI UI ---
def render_header():
    st.title(CONFIG["TITOLO"])
    if st.session_state.scambio_idx is not None:
        p1 = st.session_state.pasti[st.session_state.scambio_idx]
        st.warning(f"🔄 Scambio: spostando il pasto di **{p1['giorno']} {p1['tipo']}**")
        if st.button("Annulla operazione"):
            st.session_state.scambio_idx = None
            st.rerun()
    
    if st.button(CONFIG["BOTTONE_RESET"], use_container_width=True):
        st.session_state.pasti = genera_pasti(st.session_state.pasti)
        st.session_state.menu_key = str(uuid.uuid4()) # Cambia chiave per resettare i widget
        save_data()
        st.rerun()

def render_pasto_editor(idx):
    pasto = st.session_state.pasti[idx]
    is_selezionato = (st.session_state.scambio_idx == idx)
    
    # Se questo pasto è selezionato, evidenziamolo
    container_color = "red" if is_selezionato else "none"
    
    with st.container(border=True):
        st.markdown(f"**{'☀️' if pasto['tipo'] == 'Pranzo' else '🌙'} {pasto['tipo']}**")
        
        # Le selectbox devono aggiornare lo stato e salvare
        new_p = st.selectbox("Proteina", list(CONFIG["EMOJI_PROT"].keys()), 
                             index=get_index_safe(list(CONFIG["EMOJI_PROT"].keys()), pasto['prot']),
                             key=f"p_{idx}_{st.session_state.menu_key}")
        
        new_c = st.selectbox("Cereale", CONFIG["TUTTI_CARBO"], 
                             index=get_index_safe(CONFIG["TUTTI_CARBO"], pasto['carbo']),
                             key=f"c_{idx}_{st.session_state.menu_key}")
        
        new_v = st.selectbox("Verdura", CONFIG["OPZIONI_VERD"], 
                             index=get_index_safe(CONFIG["OPZIONI_VERD"], pasto['verd']),
                             key=f"v_{idx}_{st.session_state.menu_key}")
        
        # Aggiornamento immediato dello stato se l'utente cambia manualmente una selectbox
        if new_p != pasto['prot'] or new_c != pasto['carbo'] or new_v != pasto['verd']:
            st.session_state.pasti[idx].update({"prot": new_p, "carbo": new_c, "verd": new_v})
            save_data()

        c1, c2 = st.columns(2)
        pasto['locked'] = c1.checkbox("Blocca", value=bool(pasto['locked']), key=f"l_{idx}_{st.session_state.menu_key}")
        
        # LOGICA SPOSTA
        label_btn = "📍 QUI" if is_selezionato else "↔️ SPOSTA"
        if c2.button(label_btn, key=f"bt_{idx}_{st.session_state.menu_key}", use_container_width=True):
            if st.session_state.scambio_idx is None:
                st.session_state.scambio_idx = idx
                st.rerun()
            else:
                # ESECUZIONE SCAMBIO
                idx1 = st.session_state.scambio_idx
                idx2 = idx
                
                # Scambio solo i contenuti, non l'ID/Giorno/Tipo
                for campo in ['prot', 'carbo', 'verd', 'locked']:
                    st.session_state.pasti[idx1][campo], st.session_state.pasti[idx2][campo] = \
                    st.session_state.pasti[idx2][campo], st.session_state.pasti[idx1][campo]
                
                st.session_state.scambio_idx = None
                # CRITICO: Cambiamo la menu_key per forzare Streamlit a ricreare i widget con i nuovi valori scambiati
                st.session_state.menu_key = str(uuid.uuid4())
                save_data()
                st.rerun()

# --- 5. MAIN ---
def main():
    st.set_page_config(page_title="Menù Salute", layout="wide")
    
    if 'menu_key' not in st.session_state: st.session_state.menu_key = str(uuid.uuid4())
    if 'pasti' not in st.session_state: st.session_state.pasti = load_data()
    if 'scambio_idx' not in st.session_state: st.session_state.scambio_idx = None

    render_header()

    giorni_it = ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"]
    oggi_nome = giorni_it[datetime.now().weekday()]

    for g_nome in giorni_it:
        with st.expander(f"{'📍 ' if g_nome == oggi_nome else ''}{g_nome.upper()}", expanded=(g_nome == oggi_nome)):
            idx_pasti = [i for i, p in enumerate(st.session_state.pasti) if p['giorno'] == g_nome]
            col_sx, col_dx = st.columns(2)
            with col_sx: render_pasto_editor(idx_pasti[0])
            with col_dx: render_pasto_editor(idx_pasti[1])

    # Statistiche finali
    st.divider()
    all_prots = [p['prot'] for p in st.session_state.pasti]
    cols = st.columns(len(CONFIG["TARGET_PROTEINE"]))
    for i, (nome, target) in enumerate(CONFIG["TARGET_PROTEINE"].items()):
        attuale = all_prots.count(nome)
        cols[i].metric(f"{CONFIG['EMOJI_PROT'][nome]} {nome}", f"{attuale}/{target}", delta=attuale-target)

if __name__ == "__main__":
    main()
