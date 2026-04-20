import streamlit as st
import random
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="Menù Salute Pro", page_icon="🥗", layout="wide")

FILE_SALVATAGGIO = "menu_stato.csv"
EMOJI_PROT = {'Pesce': '🔵', 'Legumi': '🟢', 'Carne Bianca': '🟡', 'Uova': '🔴', 'Formaggio': '⚪', 'Carne Rossa': '🟣'}
OPZIONI_PROT = list(EMOJI_PROT.keys())
OPZIONI_CARBO = ['Pasta Integrale', 'Riso', 'Farro', 'Gnocchi', 'Cous Cous', 'Pane Integrale', 'Patate']
OPZIONI_VERD = ['Zucchine', 'Asparagi', 'Spinaci', 'Bieta', 'Finocchi', 'Carote', 'Piselli', 'Insalata', 'Pomodori', 'Peperoni', 'Broccoli', 'Melanzane', 'Fagiolini', 'Carciofi']

giorni_it = {0: "Lunedì", 1: "Martedì", 2: "Mercoledì", 3: "Giovedì", 4: "Venerdì", 5: "Sabato", 6: "Domenica"}
oggi_nome = giorni_it[datetime.now().weekday()]

# --- FUNZIONI CORE ---
def salva_su_disco(pasti):
    pd.DataFrame(pasti).to_csv(FILE_SALVATAGGIO, index=False)

def genera_nuova_settimana():
    giorni_l = ['Lunedì', 'Martedì', 'Mercoledì', 'Giovedì', 'Venerdì', 'Sabato', 'Domenica']
    # Pool Ministero
    prots = (['Legumi'] * 4 + ['Pesce'] * 3 + ['Carne Bianca'] * 3 + ['Uova'] * 2 + ['Formaggio'] * 1 + ['Carne Rossa'] * 1)
    c_p = ['Pasta Integrale']*3 + ['Riso', 'Farro', 'Gnocchi', 'Cous Cous']
    c_c = ['Pane Integrale']*4 + ['Patate']*3
    v = random.sample(OPZIONI_VERD, 14)
    
    # Rimescolamento con controllo anti-ripetizione consecutiva
    for _ in range(100):
        random.shuffle(prots)
        valido = True
        for i in range(len(prots)-1):
            if prots[i] == prots[i+1]: # Se due pasti di fila hanno la stessa proteina
                valido = False; break
        if valido: break

    random.shuffle(c_p); random.shuffle(c_c); random.shuffle(v)
    
    nuovi = []
    for i in range(14):
        nuovi.append({
            "id": i, "giorno": giorni_l[i//2], "tipo": "Pranzo" if i%2==0 else "Cena",
            "prot": prots[i], "carbo": c_p[i//2] if i%2==0 else c_c[i//2],
            "verd": v[i], "locked": False
        })
    return nuovi

# --- AZIONI PULSANTI ---
def action_reset():
    if os.path.exists(FILE_SALVATAGGIO):
        os.remove(FILE_SALVATAGGIO)
    st.session_state.clear()
    # Generiamo subito i nuovi dati prima del rerun
    st.session_state.pasti = genera_nuova_settimana()
    salva_su_disco(st.session_state.pasti)
    st.rerun()

def action_rimescola():
    # Prendi indici liberi (incluso il Lunedì, idx 0)
    lib_idx = [i for i, p in enumerate(st.session_state.pasti) if not p.get('locked', False)]
    if len(lib_idx) < 2: return
    
    # Rimescolamento Proteine e Verdure con logica anti-ripetizione
    for _ in range(100):
        # Copia temporanea delle proteine attuali nei posti liberi
        temp_prots = [st.session_state.pasti[i]['prot'] for i in lib_idx]
        random.shuffle(temp_prots)
        
        # Test validità
        valido = True
        test_pasti = [p['prot'] for p in st.session_state.pasti]
        for enum_i, original_idx in enumerate(lib_idx):
            test_pasti[original_idx] = temp_prots[enum_i]
        
        for i in range(len(test_pasti)-1):
            if test_pasti[i] == test_pasti[i+1]:
                valido = False; break
        
        if valido:
            for enum_i, original_idx in enumerate(lib_idx):
                st.session_state.pasti[original_idx]['prot'] = temp_prots[enum_i]
            break

    # Rimescola Verdure (liberamente)
    temp_verd = [st.session_state.pasti[i]['verd'] for i in lib_idx]
    random.shuffle(temp_verd)
    for enum_i, original_idx in enumerate(lib_idx):
        st.session_state.pasti[original_idx]['verd'] = temp_verd[enum_i]
            
    salva_su_disco(st.session_state.pasti)
    st.rerun()

# --- INIZIALIZZAZIONE ---
if 'pasti' not in st.session_state:
    if os.path.exists(FILE_SALVATAGGIO):
        df = pd.read_csv(FILE_SALVATAGGIO)
        df['locked'] = df['locked'].astype(bool)
        st.session_state.pasti = df.to_dict('records')
    else:
        st.session_state.pasti = genera_nuova_settimana()
        salva_su_disco(st.session_state.pasti)

if 'scambio_id' not in st.session_state:
    st.session_state.scambio_id = None

st.title("🥗 Menù Salute Pro")

# --- UI SETTIMANALE ---
for i in range(0, 14, 2):
    giorno = st.session_state.pasti[i]['giorno']
    es_oggi = (giorno == oggi_nome)
    with st.expander(f"📅 {giorno.upper()}" + (" 📍 OGGI" if es_oggi else ""), expanded=es_oggi):
        for j in range(2):
            idx = i + j
            pasto = st.session_state.pasti[idx]
            is_sel = (st.session_state.scambio_id == idx)
            border = "3px solid #FF4B4B" if is_sel else "1px solid #eee"
            st.markdown(f'<div style="border-left: {border}; padding-left: 10px; margin-bottom: 5px;"><small>{"☀️" if j==0 else "🌙"} {pasto["tipo"]}</small></div>', unsafe_allow_html=True)
            
            c1, c2, c3 = st.columns(3)
            n_c = c1.selectbox("Cereale", OPZIONI_CARBO, index=OPZIONI_CARBO.index(pasto['carbo']) if pasto['carbo'] in OPZIONI_CARBO else 0, key=f"c_{idx}")
            n_p = c2.selectbox("Proteina", OPZIONI_PROT, index=OPZIONI_PROT.index(pasto['prot']) if pasto['prot'] in OPZIONI_PROT else 0, key=f"p_{idx}")
            n_v = c3.selectbox("Verdura", OPZIONI_VERD, index=OPZIONI_VERD.index(pasto['verd']) if pasto['verd'] in OPZIONI_VERD else 0, key=f"v_{idx}")
            
            if n_c != pasto['carbo'] or n_p != pasto['prot'] or n_v != pasto['verd']:
                st.session_state.pasti[idx].update({"carbo": n_c, "prot": n_p, "verd": n_v})
                salva_su_disco(st.session_state.pasti)
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
                        salva_su_disco(st.session_state.pasti)
                    st.session_state.scambio_id = None
                st.rerun()
            
            st.session_state.pasti[idx]['locked'] = ca2.checkbox("Blocca", value=pasto.get('locked', False), key=f"l_{idx}", on_change=salva_su_disco)

st.divider()
c1, c2 = st.columns(2)
c1.button("🎲 Rimescola Bilanciato", use_container_width=True, on_click=action_rimescola)
c2.button("🗑️ Reset / Nuova Settimana", use_container_width=True, on_click=action_reset)

# Statistiche
all_p = [p['prot'] for p in st.session_state.pasti]
cols = st.columns(4)
for i, (name, goal) in enumerate([("Pesce", 3), ("Legumi", 4), ("Carne Bianca", 3), ("Uova", 2)]):
    count = all_p.count(name)
    cols[i].metric(name, f"{count}/{goal}")
