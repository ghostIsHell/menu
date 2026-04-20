import streamlit as st
import random
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="Menù Salute", page_icon="🥗", layout="wide")

FILE_SALVATAGGIO = "menu_stato.csv"
EMOJI_PROT = {'Pesce': '🔵', 'Legumi': '🟢', 'Carne Bianca': '🟡', 'Uova': '🔴', 'Formaggio': '⚪', 'Carne Rossa': '🟣'}
OPZIONI_PROT = list(EMOJI_PROT.keys())
OPZIONI_CARBO = ['Pasta Integrale', 'Riso', 'Farro', 'Gnocchi', 'Cous Cous', 'Pane Integrale', 'Patate']
OPZIONI_VERD = ['Zucchine', 'Asparagi', 'Spinaci', 'Bieta', 'Finocchi', 'Carote', 'Piselli', 'Insalata', 'Pomodori', 'Peperoni', 'Broccoli', 'Melanzane', 'Fagiolini', 'Carciofi']

giorni_it = {0: "Lunedì", 1: "Martedì", 2: "Mercoledì", 3: "Giovedì", 4: "Venerdì", 5: "Sabato", 6: "Domenica"}
oggi = giorni_it[datetime.now().weekday()]

# --- FUNZIONI PERSISTENZA ---
def salva_su_disco():
    pd.DataFrame(st.session_state.pasti).to_csv(FILE_SALVATAGGIO, index=False)

def carica_da_disco():
    if os.path.exists(FILE_SALVATAGGIO):
        try:
            df = pd.read_csv(FILE_SALVATAGGIO)
            df['locked'] = df['locked'].astype(bool)
            return df.to_dict('records')
        except:
            return None
    return None

# --- INIZIALIZZAZIONE STATI ---
if 'scambio_id' not in st.session_state:
    st.session_state.scambio_id = None

if 'pasti' not in st.session_state:
    dati = carica_da_disco()
    if dati: 
        st.session_state.pasti = dati
    else:
        giorni_l = ['Lunedì', 'Martedì', 'Mercoledì', 'Giovedì', 'Venerdì', 'Sabato', 'Domenica']
        prots = (['Legumi'] * 4 + ['Pesce'] * 3 + ['Carne Bianca'] * 3 + ['Uova'] * 2 + ['Formaggio'] * 1 + ['Carne Rossa'] * 1)
        c_p = ['Pasta Integrale']*3 + ['Riso', 'Farro', 'Gnocchi', 'Cous Cous']
        c_c = ['Pane Integrale']*4 + ['Patate']*3
        v = random.sample(OPZIONI_VERD * 2, 14)
        random.shuffle(prots); random.shuffle(c_p); random.shuffle(c_c)
        st.session_state.pasti = [{"id": i, "giorno": giorni_l[i//2], "tipo": "Pranzo" if i%2==0 else "Cena", "prot": prots[i], "carbo": c_p[i//2] if i%2==0 else c_c[i//2], "verd": v[i], "locked": False} for i in range(14)]
        salva_su_disco()

# --- LOGICA SCAMBIO ---
def esegui_scambio(id_cliccato):
    if st.session_state.scambio_id is None:
        st.session_state.scambio_id = id_cliccato
    else:
        id1, id2 = st.session_state.scambio_id, id_cliccato
        if id1 != id2:
            for attr in ['prot', 'carbo', 'verd']:
                st.session_state.pasti[id1][attr], st.session_state.pasti[id2][attr] = \
                st.session_state.pasti[id2][attr], st.session_state.pasti[id1][attr]
            salva_su_disco()
        st.session_state.scambio_id = None

# --- FUNZIONE RESET DEFINITIVA ---
def reset_totale_sicuro():
    if os.path.exists(FILE_SALVATAGGIO):
        os.remove(FILE_SALVATAGGIO)
    # Pulizia profonda della sessione
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

st.title("🥗 Il Mio Menù Benessere")

# --- INTERFACCIA ---
for i in range(0, 14, 2):
    giorno = st.session_state.pasti[i]['giorno']
    with st.expander(f"📅 {giorno.upper()}" + (" 📍 OGGI" if giorno == oggi else ""), expanded=(giorno == oggi)):
        for j in range(2):
            idx = i + j
            pasto = st.session_state.pasti[idx]
            is_sel = (st.session_state.scambio_id == idx)
            
            st.markdown(f"""<div style="border: 2px solid {'#FF4B4B' if is_sel else '#eee'}; padding:10px; border-radius:10px; margin-bottom:5px;">
                <small>{'☀️' if j==0 else '🌙'} {pasto['tipo']}</small></div>""", unsafe_allow_html=True)
            
            c1, c2, c3 = st.columns(3)
            # Caricamento dinamico indici per evitare errori se le liste opzioni cambiano
            idx_c = OPZIONI_CARBO.index(pasto['carbo']) if pasto['carbo'] in OPZIONI_CARBO else 0
            idx_p = OPZIONI_PROT.index(pasto['prot']) if pasto['prot'] in OPZIONI_PROT else 0
            idx_v = OPZIONI_VERD.index(pasto['verd']) if pasto['verd'] in OPZIONI_VERD else 0

            new_c = c1.selectbox("Cereale", OPZIONI_CARBO, index=idx_c, key=f"c_{idx}")
            new_p = c2.selectbox("Proteina", OPZIONI_PROT, index=idx_p, key=f"p_{idx}")
            new_v = c3.selectbox("Verdura", OPZIONI_VERD, index=idx_v, key=f"v_{idx}")
            
            if new_c != pasto['carbo'] or new_p != pasto['prot'] or new_v != pasto['verd']:
                st.session_state.pasti[idx].update({"carbo": new_c, "prot": new_p, "verd": new_v})
                salva_su_disco()
                st.rerun()

            ca1, ca2 = st.columns(2)
            ca1.button("SPOSTA / SCAMBIA", key=f"m_{idx}", on_click=esegui_scambio, args=(idx,), use_container_width=True)
            st.session_state.pasti[idx]['locked'] = ca2.checkbox("Blocca", value=pasto['locked'], key=f"l_{idx}", on_change=salva_su_disco)

# --- CONTROLLO NUTRIZIONALE ---
st.divider()
all_p = [p['prot'] for p in st.session_state.pasti]
target = {"Pesce": 3, "Legumi": 4, "Carne Bianca": 3, "Uova": 2}
cols = st.columns(4)
for i, (p_nome, p_count) in enumerate(target.items()):
    attuale = all_p.count(p_nome)
    delta_val = attuale - p_count
    cols[i].metric(p_nome, f"{attuale}/{p_count}", delta=delta_val, delta_color="normal" if delta_val == 0 else "inverse")

# Pulsante Reset con la nuova funzione sicura
st.button("🔄 Reset Totale / Nuova Settimana", use_container_width=True, on_click=reset_totale_sicuro)
