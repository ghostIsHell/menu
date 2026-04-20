import streamlit as st
import random
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="Menù Salute Pro", page_icon="🥗", layout="wide")

FILE_SALVATAGGIO = "menu_stato.csv"
EMOJI_PROT = {'Pesce': '🔵', 'Legumi': '🟢', 'Carne Bianca': '🟡', 'Uova': '🔴', 'Formaggio': '⚪', 'Carne Rossa': '🟣'}
OPZIONI_CARBO = ['Pasta Integrale', 'Riso', 'Farro', 'Gnocchi', 'Cous Cous', 'Pane Integrale', 'Patate']
OPZIONI_PROT = list(EMOJI_PROT.keys())
OPZIONI_VERD = ['Zucchine', 'Asparagi', 'Spinaci', 'Bieta', 'Finocchi', 'Carote', 'Piselli', 'Insalata', 'Pomodori', 'Peperoni', 'Broccoli', 'Melanzane', 'Fagiolini', 'Carciofi']

giorni_it = {0: "Lunedì", 1: "Martedì", 2: "Mercoledì", 3: "Giovedì", 4: "Venerdì", 5: "Sabato", 6: "Domenica"}
oggi_nome = giorni_it[datetime.now().weekday()]

# --- FUNZIONI CORE ---
def genera_nuova_settimana():
    giorni_l = ['Lunedì', 'Martedì', 'Mercoledì', 'Giovedì', 'Venerdì', 'Sabato', 'Domenica']
    prots = (['Legumi'] * 4 + ['Pesce'] * 3 + ['Carne Bianca'] * 3 + ['Uova'] * 2 + ['Formaggio'] * 1 + ['Carne Rossa'] * 1)
    c_p = ['Pasta Integrale']*3 + ['Riso', 'Farro', 'Gnocchi', 'Cous Cous']
    c_c = ['Pane Integrale']*4 + ['Patate']*3
    v = random.sample(OPZIONI_VERD, 14)
    
    # Anti-ripetizione
    for _ in range(100):
        random.shuffle(prots)
        if all(prots[i] != prots[i+1] for i in range(len(prots)-1)): break
    
    random.shuffle(c_p); random.shuffle(c_c); random.shuffle(v)
    return [{"id": i, "giorno": giorni_l[i//2], "tipo": "Pranzo" if i%2==0 else "Cena",
             "prot": prots[i], "carbo": c_p[i//2] if i%2==0 else c_c[i//2],
             "verd": v[i], "locked": False} for i in range(14)]

# --- GESTIONE LOGICA RESET ---
if st.sidebar.button("🗑️ RESET TOTALE"):
    if os.path.exists(FILE_SALVATAGGIO): os.remove(FILE_SALVATAGGIO)
    st.session_state.clear()
    st.rerun()

# --- CARICAMENTO DATI ---
if 'pasti' not in st.session_state:
    if os.path.exists(FILE_SALVATAGGIO):
        df = pd.read_csv(FILE_SALVATAGGIO)
        df['locked'] = df['locked'].astype(bool)
        st.session_state.pasti = df.to_dict('records')
    else:
        st.session_state.pasti = genera_nuova_settimana()
        pd.DataFrame(st.session_state.pasti).to_csv(FILE_SALVATAGGIO, index=False)

if 'scambio_id' not in st.session_state:
    st.session_state.scambio_id = None

# --- UI ---
st.title("🥗 Menù Salute Pro")

# Griglia Pasti
for i in range(0, 14, 2):
    giorno = st.session_state.pasti[i]['giorno']
    is_oggi = (giorno == oggi_nome)
    with st.expander(f"📅 {giorno.upper()}" + (" 📍 OGGI" if is_oggi else ""), expanded=is_oggi):
        for j in range(2):
            idx = i + j
            pasto = st.session_state.pasti[idx]
            
            # Scambio
            is_sel = (st.session_state.scambio_id == idx)
            border = "3px solid #FF4B4B" if is_sel else "1px solid #eee"
            st.markdown(f'<div style="border-left: {border}; padding-left: 10px; margin-bottom: 5px;"><small>{"☀️" if j==0 else "🌙"} {pasto["tipo"]}</small></div>', unsafe_allow_html=True)
            
            c1, c2, c3 = st.columns(3)
            n_c = c1.selectbox("Cereale", OPZIONI_CARBO, index=OPZIONI_CARBO.index(pasto['carbo']) if pasto['carbo'] in OPZIONI_CARBO else 0, key=f"c_{idx}")
            n_p = c2.selectbox("Proteina", OPZIONI_PROT, index=OPZIONI_PROT.index(pasto['prot']) if pasto['prot'] in OPZIONI_PROT else 0, key=f"p_{idx}")
            n_v = c3.selectbox("Verdura", OPZIONI_VERD, index=OPZIONI_VERD.index(pasto['verd']) if pasto['verd'] in OPZIONI_VERD else 0, key=f"v_{idx}")
            
            # Rileva cambiamenti manuali
            if n_c != pasto['carbo'] or n_p != pasto['prot'] or n_v != pasto['verd']:
                st.session_state.pasti[idx].update({"carbo": n_c, "prot": n_p, "verd": n_v})
                pd.DataFrame(st.session_state.pasti).to_csv(FILE_SALVATAGGIO, index=False)
                st.rerun()

            ca1, ca2 = st.columns(2)
            if ca1.button("SPOSTA", key=f"m_{idx}", use_container_width=True):
                if st.session_state.scambio_id is None:
                    st.session_state.scambio_id = idx
                else:
                    id1, id2 = st.session_state.scambio_id, idx
                    if id1 != id2:
                        for attr in ['prot', 'carbo', 'verd']:
                            st.session_state.pasti[id1][attr], st.session_state.pasti[id2][attr] = st.session_state.pasti[id2][attr], st.session_state.pasti[id1][attr]
                        pd.DataFrame(st.session_state.pasti).to_csv(FILE_SALVATAGGIO, index=False)
                    st.session_state.scambio_id = None
                st.rerun()
            
            # Lock
            lock_val = ca2.checkbox("Blocca", value=pasto['locked'], key=f"l_{idx}")
            if lock_val != pasto['locked']:
                st.session_state.pasti[idx]['locked'] = lock_val
                pd.DataFrame(st.session_state.pasti).to_csv(FILE_SALVATAGGIO, index=False)
                st.rerun()

st.divider()

# Rimescola (Logica integrata)
if st.button("🎲 Rimescola Liberi", use_container_width=True):
    lib_idx = [k for k, p in enumerate(st.session_state.pasti) if not p['locked']]
    if len(lib_idx) > 1:
        # Rimescola Prot e Verd
        for attr in ['prot', 'verd']:
            vals = [st.session_state.pasti[k][attr] for k in lib_idx]
            random.shuffle(vals)
            for enum_i, k in enumerate(lib_idx): st.session_state.pasti[k][attr] = vals[enum_i]
        
        # Rimescola Carbo divisi
        lib_p = [k for k in lib_idx if k % 2 == 0]
        lib_c = [k for k in lib_idx if k % 2 != 0]
        for g in [lib_p, lib_c]:
            if g:
                vals = [st.session_state.pasti[k]['carbo'] for k in g]
                random.shuffle(vals)
                for enum_i, k in enumerate(g): st.session_state.pasti[k]['carbo'] = vals[enum_i]
        
        pd.DataFrame(st.session_state.pasti).to_csv(FILE_SALVATAGGIO, index=False)
        st.rerun()

# Statistiche
all_p = [p['prot'] for p in st.session_state.pasti]
cols = st.columns(4)
for i, (name, goal) in enumerate([("Pesce", 3), ("Legumi", 4), ("Carne Bianca", 3), ("Uova", 2)]):
    cols[i].metric(name, f"{all_p.count(name if name!='Carne Bianca' else 'Carne Bianca')}/{goal}")
