import streamlit as st
import random
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="Menù Salute", page_icon="🥗", layout="wide")

FILE_SALVATAGGIO = "menu_stato.csv"
EMOJI_PROT = {'Pesce': '🔵', 'Legumi': '🟢', 'Carne Bianca': '🟡', 'Uova': '🔴', 'Formaggio': '⚪', 'Carne Rossa': '🟣'}
giorni_it = {0: "Lunedì", 1: "Martedì", 2: "Mercoledì", 3: "Giovedì", 4: "Venerdì", 5: "Sabato", 6: "Domenica"}
oggi = giorni_it[datetime.now().weekday()]

# --- FUNZIONI DI PERSISTENZA ---
def salva_su_disco():
    pd.DataFrame(st.session_state.pasti).to_csv(FILE_SALVATAGGIO, index=False)

def carica_da_disco():
    if os.path.exists(FILE_SALVATAGGIO):
        df = pd.read_csv(FILE_SALVATAGGIO)
        df['locked'] = df['locked'].astype(bool)
        return df.to_dict('records')
    return None

# --- INIZIALIZZAZIONE ---
if 'pasti' not in st.session_state:
    dati_salvati = carica_da_disco()
    if dati_salvati:
        st.session_state.pasti = dati_salvati
    else:
        giorni_lista = ['Lunedì', 'Martedì', 'Mercoledì', 'Giovedì', 'Venerdì', 'Sabato', 'Domenica']
        prots = (['Legumi'] * 4 + ['Pesce'] * 3 + ['Carne Bianca'] * 3 + ['Uova'] * 2 + ['Formaggio'] * 1 + ['Carne Rossa'] * 1)
        carbo_p = ['Pasta Integrale', 'Pasta Integrale', 'Pasta Integrale', 'Riso', 'Farro', 'Gnocchi', 'Cous Cous']
        carbo_c = ['Pane Integrale', 'Pane Integrale', 'Pane Integrale', 'Patate', 'Patate', 'Pane Integrale', 'Pane Integrale']
        verdure = ['Zucchine', 'Asparagi', 'Spinaci', 'Bieta', 'Finocchi', 'Carote', 'Piselli', 'Insalata', 'Pomodori', 'Peperoni', 'Broccoli', 'Melanzane', 'Fagiolini', 'Carciofi']
        random.shuffle(prots); random.shuffle(carbo_p); random.shuffle(carbo_c); random.shuffle(verdure)
        st.session_state.pasti = []
        for i in range(14):
            st.session_state.pasti.append({
                "id": i, "giorno": giorni_lista[i//2], "tipo": "Pranzo" if i%2==0 else "Cena",
                "prot": prots[i], "carbo": carbo_p[i//2] if i%2==0 else carbo_c[i//2],
                "verd": verdure[i], "locked": False
            })
        salva_su_disco()

# Inizializziamo lo stato dello scambio se non esiste
if 'scambio_id' not in st.session_state:
    st.session_state.scambio_id = None

st.title("🥗 Il Mio Menù Benessere")

# --- LOGICA DI SCAMBIO ---
def esegui_scambio(id_cliccato):
    if st.session_state.scambio_id is None:
        st.session_state.scambio_id = id_cliccato
    else:
        id1 = st.session_state.scambio_id
        id2 = id_cliccato
        if id1 != id2:
            # Scambiamo solo prot e verd, i carbo restano legati a pranzo/cena
            st.session_state.pasti[id1]['prot'], st.session_state.pasti[id2]['prot'] = st.session_state.pasti[id2]['prot'], st.session_state.pasti[id1]['prot']
            st.session_state.pasti[id1]['verd'], st.session_state.pasti[id2]['verd'] = st.session_state.pasti[id2]['verd'], st.session_state.pasti[id1]['verd']
            salva_su_disco()
            st.success(f"Scambiato!")
        st.session_state.scambio_id = None

# Banner avviso
if st.session_state.scambio_id is not None:
    st.warning(f"🔄 Selezionato pasto per lo spostamento. Clicca su 'SPOSTA' in un altro giorno per completare.")
    if st.button("Annulla Spostamento"):
        st.session_state.scambio_id = None
        st.rerun()

# --- INTERFACCIA ---
for i in range(0, 14, 2):
    giorno_nome = st.session_state.pasti[i]['giorno']
    es_oggi = (giorno_nome == oggi)
    label = f"📅 {giorno_nome.upper()} (OGGI)" if es_oggi else f"📅 {giorno_nome}"
    
    with st.expander(label, expanded=es_oggi):
        for j in range(2):
            idx = i + j
            pasto = st.session_state.pasti[idx]
            emoji = EMOJI_PROT.get(pasto['prot'], '🔹')
            
            # Grafica evidenziata se selezionato
            is_selected = (st.session_state.scambio_id == idx)
            bg = "#FFEBEE" if is_selected else "transparent"
            border = "2px solid #D32F2F" if is_selected else "none"

            st.markdown(f"""
            <div style="background-color: {bg}; border: {border}; padding: 10px; border-radius: 8px; margin-bottom: 5px;">
                <span style="font-size: 0.8em; opacity: 0.6;">{'☀️' if j==0 else '🌙'} {pasto['tipo'].upper()}</span><br>
                <span style="font-size: 1.1em; font-weight: bold;">{pasto['carbo']}</span> 
                <span style="font-size: 1em;">con {emoji} {pasto['prot']} e {pasto['verd']}</span>
            </div>
            """, unsafe_allow_html=True)
            
            c_sposta, c_lock = st.columns([1, 1])
            with c_sposta:
                st.button("SPOSTA", key=f"btn_{idx}", on_click=esegui_scambio, args=(idx,))
            with c_lock:
                st.session_state.pasti[idx]['locked'] = st.checkbox("Blocca", value=pasto['locked'], key=f"lock_{idx}", on_change=salva_su_disco)

# --- STATISTICHE E RESET ---
st.divider()
all_prots = [p['prot'] for p in st.session_state.pasti]
st.subheader("📊 Bilancio Settimanale")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Pesce", f"{all_prots.count('Pesce')}/3")
m2.metric("Legumi", f"{all_prots.count('Legumi')}/4")
m3.metric("Bianca", f"{all_prots.count('Carne Bianca')}/3")
m4.metric("Uova", f"{all_prots.count('Uova')}/2")

def rimescola():
    lib_idx = [k for k, p in enumerate(st.session_state.pasti) if not p['locked']]
    for attr in ['prot', 'verd']:
        vals = [st.session_state.pasti[k][attr] for k in lib_idx]
        random.shuffle(vals)
        for idx_val, k in enumerate(lib_idx): st.session_state.pasti[k][attr] = vals[idx_val]
    salva_su_disco()

def reset_totale():
    if os.path.exists(FILE_SALVATAGGIO): os.remove(FILE_SALVATAGGIO)
    st.session_state.clear()

c1, c2 = st.columns(2)
c1.button("🎲 Rimescola Liberi", use_container_width=True, on_click=rimescola)
c2.button("🔄 Nuova Base / Reset", use_container_width=True, on_click=reset_totale)
