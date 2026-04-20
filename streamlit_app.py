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
def salva_su_disco(pasti):
    pd.DataFrame(pasti).to_csv(FILE_SALVATAGGIO, index=False)

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
        salva_su_disco(st.session_state.pasti)

if 'scambio_id' not in st.session_state:
    st.session_state.scambio_id = None

st.title("🥗 Il Mio Menù Benessere")

# --- AVVISO SCAMBIO ATTIVO ---
if st.session_state.scambio_id is not None:
    st.error(f"⚠️ SELEZIONATO: Pasto da spostare individuato. Clicca 'Sposta' su un altro pasto per scambiarli.")
    if st.button("Annulla Scambio"):
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
            
            # EVIDENZIAZIONE SE SELEZIONATO
            is_selected = (st.session_state.scambio_id == idx)
            bg_color = "#FFEBEE" if is_selected else "transparent"
            border_style = "2px solid #D32F2F" if is_selected else "none"

            col_testo, col_sposta, col_lock = st.columns([0.60, 0.20, 0.20])
            
            with col_testo:
                st.markdown(f"""
                <div style="line-height: 1.2; color: #31333F; background-color: {bg_color}; border: {border_style}; padding: 5px; border-radius: 5px;">
                    <span style="font-size: 0.85em; opacity: 0.6;">{icona_tipo} {pasto['tipo'].upper()}</span><br>
                    <span style="font-size: 1.15em; font-weight: bold;">{pasto['carbo']}</span> 
                    <span style="font-size: 1em;">con {emoji} {pasto['prot']} e {pasto['verd']}</span>
                </div>
                """, unsafe_allow_html=True)
            
            with col_sposta:
                if st.button("Sposta", key=f"btn_mov_{idx}"):
                    if st.session_state.scambio_id is None:
                        st.session_state.scambio_id = idx
                        st.rerun()
                    else:
                        id1, id2 = st.session_state.scambio_id, idx
                        # Scambio proteine e verdure
                        st.session_state.pasti[id1]['prot'], st.session_state.pasti[id2]['prot'] = st.session_state.pasti[id2]['prot'], st.session_state.pasti[id1]['prot']
                        st.session_state.pasti[id1]['verd'], st.session_state.pasti[id2]['verd'] = st.session_state.pasti[id2]['verd'], st.session_state.pasti[id1]['verd']
                        st.session_state.scambio_id = None
                        salva_su_disco(st.session_state.pasti)
                        st.rerun()
            
            with col_lock:
                # Gestione lock con salvataggio immediato
                val_lock = st.checkbox("Blocca", value=pasto['locked'], key=f"chk_l_{idx}")
                if val_lock != pasto['locked']:
                    st.session_state.pasti[idx]['locked'] = val_lock
                    salva_su_disco(st.session_state.pasti)
                    st.rerun()

# --- CONTROLLO NUTRIZIONALE E RESET ---
st.divider()
all_prots = [p['prot'] for p in st.session_state.pasti]
st.subheader("📊 Bilancio Settimanale")
cols_m = st.columns(4)
for i, (nome, target) in enumerate([("Pesce", 3), ("Legumi", 4), ("Carne Bianca", 3), ("Uova", 2)]):
    cols_m[i].metric(nome, f"{all_prots.count(nome if nome!='Carne Bianca' else 'Carne Bianca')}/{target}")

with st.expander("🛒 Lista della Spesa (x2 persone)", expanded=False):
    st.write(f"- 🐟 Pesce: {all_prots.count('Pesce')*300}g\n- 🌿 Legumi: {all_prots.count('Legumi')*300}g\n- 🥩 Carne Bianca: {all_prots.count('Carne Bianca')*250}g\n- 🥚 Uova: {all_prots.count('Uova')*4} unità")

if st.button("🎲 Rimescola Liberi", use_container_width=True):
    lib_idx = [k for k, p in enumerate(st.session_state.pasti) if not p['locked']]
    for attr in ['prot', 'verd']:
        vals = [st.session_state.pasti[k][attr] for k in lib_idx]
        random.shuffle(vals)
        for idx_val, k in enumerate(lib_idx): st.session_state.pasti[k][attr] = vals[idx_val]
    salva_su_disco(st.session_state.pasti)
    st.rerun()

if st.button("🔄 Nuova Base / Reset Totale", use_container_width=True):
    if os.path.exists(FILE_SALVATAGGIO): os.remove(FILE_SALVATAGGIO)
    st.session_state.clear()
    st.rerun()
