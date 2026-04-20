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

# Pool predefiniti per la generazione automatica
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

# --- LOGICA DI SCAMBIO ---
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
    st.info("🔄 Modalità spostamento: seleziona il pasto di destinazione cliccandoci sopra.")
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
            
            # Evidenziazione solo bordo
            is_selected = (st.session_state.scambio_id == idx)
            border_color = "#D32F2F" if is_selected else "#eee"
            border_width = "3px" if is_selected else "1px"

            # Riquadro cliccabile tramite pulsante trasparente sopra HTML
            with st.container():
                st.markdown(f"""
                    <div style="border: {border_width} solid {border_color}; border-radius:10px; padding:10px; margin-bottom: -45px; pointer-events: none;">
                        <span style="font-size:0.8em; opacity:0.6;">{'☀️' if j==0 else '🌙'} {pasto['tipo'].upper()}</span><br>
                        <b>{pasto['carbo']}</b> con {EMOJI_PROT.get(pasto['prot'], '🔹')} {pasto['prot']} e {pasto['verd']}
                    </div>
                """, unsafe_allow_html=True)
                
                # Il pulsante diventa "invisibile" ma copre l'area per permettere il click
                st.button(" ", key=f"pasto_{idx}", on_click=clicca_pasto, args=(idx,), use_container_width=True)
                st.session_state.pasti[idx]['locked'] = st.checkbox("Blocca pasto", value=pasto['locked'], key=f"l_{idx}", on_change=salva_su_disco)

# --- LOGICA AUTOMATICA ---
def rimescola_bilanciato():
    idx_p_liberi = [k for k in range(0, 14, 2) if not st.session_state.pasti[k]['locked']]
    idx_c_liberi = [k for k in range(1, 14, 2) if not st.session_state.pasti[k]['locked']]
    idx_tutti_liberi = [k for k, p in enumerate(st.session_state.pasti) if not p['locked']]

    for attr in ['prot', 'verd']:
        vals = [st.session_state.pasti[k][attr] for k in idx_tutti_liberi]
        random.shuffle(vals)
        for i, k in enumerate(idx_tutti_liberi): st.session_state.pasti[k][attr] = vals[i]

    for idx_group in [idx_p_liberi, idx_c_liberi]:
        c_vals = [st.session_state.pasti[k]['carbo'] for k in idx_group]
        random.shuffle(c_vals)
        for i, k in enumerate(idx_group): st.session_state.pasti[k]['carbo'] = c_vals[i]
    salva_su_disco()

st.divider()
c1, c2 = st.columns(2)
c1.button("🎲 Rimescola Bilanciato", use_container_width=True, on_click=rimescola_bilanciato)
c2.button("🔄 Reset Totale", use_container_width=True, on_click=lambda: (os.remove(FILE_SALVATAGGIO) if os.path.exists(FILE_SALVATAGGIO) else None, st.session_state.clear()))
