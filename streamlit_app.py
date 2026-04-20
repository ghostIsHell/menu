import streamlit as st
import random
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="Menù Salute", page_icon="🥗", layout="wide")

# Configurazione file salvataggio
FILE_SALVATAGGIO = "menu_stato.csv"

EMOJI_PROT = {
    'Pesce': '🔵', 'Legumi': '🟢', 'Carne Bianca': '🟡',
    'Uova': '🔴', 'Formaggio': '⚪', 'Carne Rossa': '🟣'
}

giorni_it = {0: "Lunedì", 1: "Martedì", 2: "Mercoledì", 3: "Giovedì", 4: "Venerdì", 5: "Sabato", 6: "Domenica"}
oggi = giorni_it[datetime.now().weekday()]

# --- FUNZIONI DI PERSISTENZA ---
def salva_su_disco(pasti):
    df = pd.DataFrame(pasti)
    df.to_csv(FILE_SALVATAGGIO, index=False)

def carica_da_disco():
    if os.path.exists(FILE_SALVATAGGIO):
        df = pd.read_csv(FILE_SALVATAGGIO)
        # Convertiamo la stringa 'True'/'False' in booleani reali
        df['locked'] = df['locked'].astype(bool)
        return df.to_dict('records')
    return None

# --- INIZIALIZZAZIONE ---
if 'pasti' not in st.session_state:
    dati_salvati = carica_da_disco()
    if dati_salvati:
        st.session_state.pasti = dati_salvati
    else:
        # Generazione da zero se non c'è file
        giorni_lista = ['Lunedì', 'Martedì', 'Mercoledì', 'Giovedì', 'Venerdì', 'Sabato', 'Domenica']
        prots = (['Legumi'] * 4 + ['Pesce'] * 3 + ['Carne Bianca'] * 3 + ['Uova'] * 2 + ['Formaggio'] * 1 + ['Carne Rossa'] * 1)
        carbo_p = ['Pasta Integrale', 'Pasta Integrale', 'Pasta Integrale', 'Riso', 'Farro', 'Gnocchi', 'Cous Cous']
        carbo_c = ['Pane Integrale', 'Pane Integrale', 'Pane Integrale', 'Patate', 'Patate', 'Pane Integrale', 'Pane Integrale']
        verdure = ['Zucchine', 'Asparagi', 'Spinaci', 'Bieta', 'Finocchi', 'Carote', 'Piselli', 'Insalata', 'Pomodori', 'Peperoni', 'Broccoli', 'Melanzane', 'Fagiolini', 'Carciofi']
        
        random.shuffle(prots); random.shuffle(carbo_p); random.shuffle(carbo_c); random.shuffle(verdure)
        
        st.session_state.pasti = []
        for i in range(14):
            is_pranzo = (i % 2 == 0)
            st.session_state.pasti.append({
                "id": i, "giorno": giorni_lista[i//2], "tipo": "Pranzo" if is_pranzo else "Cena",
                "prot": prots[i], "carbo": carbo_p[i//2] if is_pranzo else carbo_c[i//2],
                "verd": verdure[i], "locked": False
            })
        salva_su_disco(st.session_state.pasti)

if 'scambio_id' not in st.session_state:
    st.session_state.scambio_id = None

st.title("🥗 Il Mio Menù Benessere (Salvato)")

# --- LOGICA SCAMBIO ---
if st.session_state.scambio_id is not None:
    p_sel = st.session_state.pasti[st.session_state.scambio_id]
    st.warning(f"🔄 Scambio: **{p_sel['giorno']} {p_sel['tipo']}** selezionato.")
    if st.button("Annulla"):
        st.session_state.scambio_id = None
        st.rerun()

# --- INTERFACCIA ---
for i in range(0, 14, 2):
    giorno_nome = st.session_state.pasti[i]['giorno']
    es_oggi = (giorno_nome == oggi)
    label_giorno = f"📅 {giorno_nome.upper()} 📍 (OGGI)" if es_oggi else f"📅 {giorno_nome}"
    
    with st.expander(label_giorno, expanded=es_oggi):
        for j in range(2):
            idx = i + j
            pasto = st.session_state.pasti[idx]
            emoji = EMOJI_PROT.get(pasto['prot'], '🔹')
            icona_tipo = "☀️" if j == 0 else "🌙"
            
            col_testo, col_sposta, col_lock = st.columns([0.65, 0.18, 0.17])
            
            with col_testo:
                st.markdown(f"""
                <div style="line-height: 1.2; color: #31333F;">
                    <span style="font-size: 0.85em; opacity: 0.6;">{icona_tipo} {pasto['tipo'].upper()}</span><br>
                    <span style="font-size: 1.15em; font-weight: bold;">{pasto['carbo']}</span> 
                    <span style="font-size: 1em;">con {emoji} {pasto['prot']} e {pasto['verd']}</span>
                </div>
                """, unsafe_allow_html=True)
            
            with col_sposta:
                if st.button("Sposta", key=f"m_{idx}"):
                    if st.session_state.scambio_id is None:
                        st.session_state.scambio_id = idx
                    else:
                        id1, id2 = st.session_state.scambio_id, idx
                        st.session_state.pasti[id1]['prot'], st.session_state.pasti[id2]['prot'] = st.session_state.pasti[id2]['prot'], st.session_state.pasti[id1]['prot']
                        st.session_state.pasti[id1]['verd'], st.session_state.pasti[id2]['verd'] = st.session_state.pasti[id2]['verd'], st.session_state.pasti[id1]['verd']
                        st.session_state.scambio_id = None
                        salva_su_disco(st.session_state.pasti) # SALVA DOPO SCAMBIO
                    st.rerun()
            
            with col_lock:
                nuovo_lock = st.checkbox("Blocca", value=pasto['locked'], key=f"l_{idx}")
                if nuovo_lock != pasto['locked']:
                    st.session_state.pasti[idx]['locked'] = nuovo_lock
                    salva_su_disco(st.session_state.pasti) # SALVA DOPO LOCK

# --- CONTROLLO NUTRIZIONALE E RESET ---
st.divider()
all_prots = [p['prot'] for p in st.session_state.pasti]
cols_m = st.columns(4)
for i, (nome, target) in enumerate([("Pesce", 3), ("Legumi", 4), ("Carne Bianca", 3), ("Uova", 2)]):
    cols_m[i].metric(nome, f"{all_prots.count(nome if nome!='Carne Bianca' else 'Carne Bianca')}/{target}")

if st.button("🎲 Rimescola Liberi", use_container_width=True):
    lib_idx = [k for k, p in enumerate(st.session_state.pasti) if not p['locked']]
    for attr in ['prot', 'verd']:
        vals = [st.session_state.pasti[k][attr] for k in lib_idx]
        random.shuffle(vals)
        for idx_val, k in enumerate(lib_idx): st.session_state.pasti[k][attr] = vals[idx_val]
    salva_su_disco(st.session_state.pasti) # SALVA DOPO RIMESCOLA
    st.rerun()

if st.button("🔄 Nuova Base / Reset Totale", use_container_width=True):
    if os.path.exists(FILE_SALVATAGGIO):
        os.remove(FILE_SALVATAGGIO)
    st.session_state.clear()
    st.rerun()
