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

def salva_su_disco():
    pd.DataFrame(st.session_state.pasti).to_csv(FILE_SALVATAGGIO, index=False)

def carica_da_disco():
    if os.path.exists(FILE_SALVATAGGIO):
        df = pd.read_csv(FILE_SALVATAGGIO)
        df['locked'] = df['locked'].astype(bool)
        return df.to_dict('records')
    return None

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

# --- INIZIALIZZAZIONE ---
if 'pasti' not in st.session_state:
    dati_salvati = carica_da_disco()
    if dati_salvati:
        st.session_state.pasti = dati_salvati
    else:
        giorni_lista = ['Lunedì', 'Martedì', 'Mercoledì', 'Giovedì', 'Venerdì', 'Sabato', 'Domenica']
        prots = (['Legumi'] * 4 + ['Pesce'] * 3 + ['Carne Bianca'] * 3 + ['Uova'] * 2 + ['Formaggio'] * 1 + ['Carne Rossa'] * 1)
        c_p = ['Pasta Integrale']*3 + ['Riso', 'Farro', 'Gnocchi', 'Cous Cous']
        c_c = ['Pane Integrale']*3 + ['Patate']*2 + ['Pane Integrale']*2
        v = OPZIONI_VERD.copy()
        random.shuffle(prots); random.shuffle(c_p); random.shuffle(c_c); random.shuffle(v)
        st.session_state.pasti = []
        for i in range(14):
            st.session_state.pasti.append({
                "id": i, "giorno": giorni_lista[i//2], "tipo": "Pranzo" if i%2==0 else "Cena",
                "prot": prots[i], "carbo": c_p[i//2] if i%2==0 else c_c[i//2],
                "verd": v[i], "locked": False
            })
        salva_su_disco()

if 'scambio_id' not in st.session_state:
    st.session_state.scambio_id = None

st.title("🥗 Il Mio Menù Benessere")

# --- INTERFACCIA ---
for i in range(0, 14, 2):
    giorno = st.session_state.pasti[i]['giorno']
    label = f"📅 {giorno.upper()} (OGGI)" if giorno == oggi else f"📅 {giorno}"
    with st.expander(label, expanded=(giorno == oggi)):
        for j in range(2):
            idx = i + j
            pasto = st.session_state.pasti[idx]
            
            is_selected = (st.session_state.scambio_id == idx)
            border_color = "#FF4B4B" if is_selected else "#444"

            with st.container():
                st.markdown(f"""<div style="border: 2px solid {border_color}; padding: 10px; border-radius: 10px; margin-bottom: 10px;">
                    <span style="font-size: 0.85em; opacity: 0.7;">{'☀️' if j==0 else '🌙'} {pasto['tipo'].upper()}</span></div>""", unsafe_allow_html=True)
                
                # SELETTORI PER CAMBIO SINGOLO ELEMENTO
                c1, c2, c3 = st.columns(3)
                with c1:
                    new_carbo = st.selectbox("Cereale", OPZIONI_CARBO, index=OPZIONI_CARBO.index(pasto['carbo']) if pasto['carbo'] in OPZIONI_CARBO else 0, key=f"c_{idx}")
                with c2:
                    new_prot = st.selectbox("Proteina", OPZIONI_PROT, index=OPZIONI_PROT.index(pasto['prot']) if pasto['prot'] in OPZIONI_PROT else 0, key=f"p_{idx}")
                with c3:
                    new_verd = st.selectbox("Verdura", OPZIONI_VERD, index=OPZIONI_VERD.index(pasto['verd']) if pasto['verd'] in OPZIONI_VERD else 0, key=f"v_{idx}")
                
                # Aggiornamento se l'utente cambia manualmente una tendina
                if new_carbo != pasto['carbo'] or new_prot != pasto['prot'] or new_verd != pasto['verd']:
                    st.session_state.pasti[idx].update({"carbo": new_carbo, "prot": new_prot, "verd": new_verd})
                    salva_su_disco()
                    st.rerun()

                # TASTI AZIONE
                ca1, ca2 = st.columns(2)
                ca1.button("SPOSTA TUTTO", key=f"mov_{idx}", on_click=esegui_scambio, args=(idx,), use_container_width=True)
                st.session_state.pasti[idx]['locked'] = ca2.checkbox("Blocca", value=pasto['locked'], key=f"l_{idx}", on_change=salva_su_disco)

st.divider()
if st.button("🔄 Nuova Base / Reset", use_container_width=True, on_click=lambda: (os.remove(FILE_SALVATAGGIO) if os.path.exists(FILE_SALVATAGGIO) else None, st.session_state.clear())):
    st.rerun()
