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

# Pool per generazione automatica
POOL_CARBO_P = ['Pasta Integrale', 'Pasta Integrale', 'Pasta Integrale', 'Riso', 'Farro', 'Gnocchi', 'Cous Cous']
POOL_CARBO_C = ['Pane Integrale', 'Pane Integrale', 'Pane Integrale', 'Patate', 'Patate', 'Pane Integrale', 'Pane Integrale']

def salva_su_disco():
    pd.DataFrame(st.session_state.pasti).to_csv(FILE_SALVATAGGIO, index=False)

def carica_da_disco():
    if os.path.exists(FILE_SALVATAGGIO):
        df = pd.read_csv(FILE_SALVATAGGIO)
        df['locked'] = df['locked'].astype(bool)
        return df.to_dict('records')
    return None

def clicca_pasto(id_cliccato):
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

# --- INIZIALIZZAZIONE ---
if 'pasti' not in st.session_state:
    dati_salvati = carica_da_disco()
    if dati_salvati:
        st.session_state.pasti = dati_salvati
    else:
        giorni_lista = ['Lunedì', 'Martedì', 'Mercoledì', 'Giovedì', 'Venerdì', 'Sabato', 'Domenica']
        prots = (['Legumi'] * 4 + ['Pesce'] * 3 + ['Carne Bianca'] * 3 + ['Uova'] * 2 + ['Formaggio'] * 1 + ['Carne Rossa'] * 1)
        verdure = ['Zucchine', 'Asparagi', 'Spinaci', 'Bieta', 'Finocchi', 'Carote', 'Piselli', 'Insalata', 'Pomodori', 'Peperoni', 'Broccoli', 'Melanzane', 'Fagiolini', 'Carciofi']
        c_p, c_c = POOL_CARBO_P.copy(), POOL_CARBO_C.copy()
        random.shuffle(prots); random.shuffle(c_p); random.shuffle(c_c); random.shuffle(verdure)
        st.session_state.pasti = []
        for i in range(14):
            st.session_state.pasti.append({
                "id": i, "giorno": giorni_lista[i//2], "tipo": "Pranzo" if i%2==0 else "Cena",
                "prot": prots[i], "carbo": c_p[i//2] if i%2==0 else c_c[i//2],
                "verd": verdure[i], "locked": False
            })
        salva_su_disco()

if 'scambio_id' not in st.session_state:
    st.session_state.scambio_id = None

st.title("🥗 Il Mio Menù Benessere")

if st.session_state.scambio_id is not None:
    st.info("🔄 Modalità spostamento: clicca sul pasto di destinazione.")
    if st.button("Annulla Spostamento"):
        st.session_state.scambio_id = None
        st.rerun()

# --- INTERFACCIA ---
for i in range(0, 14, 2):
    giorno = st.session_state.pasti[i]['giorno']
    label = f"📅 {giorno.upper()} (OGGI)" if giorno == oggi else f"📅 {giorno}"
    with st.expander(label, expanded=(giorno == oggi)):
        for j in range(2):
            idx = i + j
            pasto = st.session_state.pasti[idx]
            emoji = EMOJI_PROT.get(pasto['prot'], '🔹')
            icona = '☀️ PRANZO' if j==0 else '🌙 CENA'
            
            # Creiamo l'etichetta del bottone
            testo_bottone = f"{icona}: {pasto['carbo']} + {emoji} {pasto['prot']} + {pasto['verd']}"
            
            # Se selezionato, aggiungiamo un indicatore visivo nel testo
            if st.session_state.scambio_id == idx:
                testo_bottone = f"➡️ SELEZIONATO: {testo_bottone}"

            # Pulsante che contiene tutto il testo
            st.button(testo_bottone, key=f"btn_{idx}", on_click=clicca_pasto, args=(idx,), use_container_width=True)
            st.session_state.pasti[idx]['locked'] = st.checkbox("Blocca pasto", value=pasto['locked'], key=f"l_{idx}", on_change=salva_su_disco)

# --- BOTTONI AZIONE ---
def rimescola_bilanciato():
    idx_p_lib = [k for k in range(0, 14, 2) if not st.session_state.pasti[k]['locked']]
    idx_c_lib = [k for k in range(1, 14, 2) if not st.session_state.pasti[k]['locked']]
    idx_tutti = [k for k, p in enumerate(st.session_state.pasti) if not p['locked']]
    for a in ['prot', 'verd']:
        v = [st.session_state.pasti[k][a] for k in idx_tutti]
        random.shuffle(v)
        for x, k in enumerate(idx_tutti): st.session_state.pasti[k][a] = v[x]
    for g in [idx_p_lib, idx_c_lib]:
        v = [st.session_state.pasti[k]['carbo'] for k in g]
        random.shuffle(v)
        for x, k in enumerate(g): st.session_state.pasti[k]['carbo'] = v[x]
    salva_su_disco()

st.divider()
c1, c2 = st.columns(2)
c1.button("🎲 Rimescola Bilanciato", use_container_width=True, on_click=rimescola_bilanciato)
c2.button("🔄 Reset Totale", use_container_width=True, on_click=lambda: (os.remove(FILE_SALVATAGGIO) if os.path.exists(FILE_SALVATAGGIO) else None, st.session_state.clear()))
