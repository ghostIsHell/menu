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

# --- TRADUZIONE OGGI ---
giorni_it = {0: "Lunedì", 1: "Martedì", 2: "Mercoledì", 3: "Giovedì", 4: "Venerdì", 5: "Sabato", 6: "Domenica"}
oggi_nome = giorni_it[datetime.now().weekday()]

# --- FUNZIONI CORE ---
def salva_su_disco():
    pd.DataFrame(st.session_state.pasti).to_csv(FILE_SALVATAGGIO, index=False)

def genera_nuova_settimana():
    giorni_l = ['Lunedì', 'Martedì', 'Mercoledì', 'Giovedì', 'Venerdì', 'Sabato', 'Domenica']
    prots = (['Legumi'] * 4 + ['Pesce'] * 3 + ['Carne Bianca'] * 3 + ['Uova'] * 2 + ['Formaggio'] * 1 + ['Carne Rossa'] * 1)
    c_p = ['Pasta Integrale']*3 + ['Riso', 'Farro', 'Gnocchi', 'Cous Cous']
    c_c = ['Pane Integrale']*4 + ['Patate']*3
    v = random.sample(OPZIONI_VERD, 14)
    
    random.shuffle(prots); random.shuffle(c_p); random.shuffle(c_c); random.shuffle(v)
    
    nuovi_pasti = []
    for i in range(14):
        nuovi_pasti.append({
            "id": i, "giorno": giorni_l[i//2], "tipo": "Pranzo" if i%2==0 else "Cena",
            "prot": prots[i], "carbo": c_p[i//2] if i%2==0 else c_c[i//2],
            "verd": v[i], "locked": False
        })
    return nuovi_pasti

# --- INIZIALIZZAZIONE ---
if 'pasti' not in st.session_state:
    if os.path.exists(FILE_SALVATAGGIO):
        try:
            df = pd.read_csv(FILE_SALVATAGGIO)
            df['locked'] = df['locked'].astype(bool)
            st.session_state.pasti = df.to_dict('records')
        except:
            st.session_state.pasti = genera_nuova_settimana()
    else:
        st.session_state.pasti = genera_nuova_settimana()
        salva_su_disco()

if 'scambio_id' not in st.session_state:
    st.session_state.scambio_id = None

# --- LOGICA SCAMBIO MANUALE ---
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

# --- LOGICA RIMESCOLA AUTOMATICO BILANCIATO ---
def rimescola_bilanciato():
    liberi_idx = [i for i, p in enumerate(st.session_state.pasti) if not p['locked']]
    liberi_pranzo = [i for i in liberi_idx if i % 2 == 0]
    liberi_cena = [i for i in liberi_idx if i % 2 != 0]

    # 1. Rimescola Proteine e Verdure ovunque sia libero
    for attr in ['prot', 'verd']:
        vals = [st.session_state.pasti[i][attr] for i in liberi_idx]
        random.shuffle(vals)
        for idx_val, i in enumerate(liberi_idx):
            st.session_state.pasti[i][attr] = vals[idx_val]

    # 2. Rimescola Carboidrati mantenendo Pasta a Pranzo e Pane a Cena
    for gruppo in [liberi_pranzo, liberi_cena]:
        c_vals = [st.session_state.pasti[i]['carbo'] for i in gruppo]
        random.shuffle(c_vals)
        for idx_val, i in enumerate(gruppo):
            st.session_state.pasti[i]['carbo'] = c_vals[idx_val]
    
    salva_su_disco()

st.title("🥗 Menù Salute Intelligente")

if st.session_state.scambio_id is not None:
    st.warning(f"🔄 SPOSTAMENTO: Clicca su un altro pasto per scambiare.")
    if st.button("Annulla"):
        st.session_state.scambio_id = None
        st.rerun()

for i in range(0, 14, 2):
    giorno = st.session_state.pasti[i]['giorno']
    is_oggi = (giorno == oggi_nome)
    with st.expander(f"📅 {giorno.upper()}" + (" 📍 OGGI" if is_oggi else ""), expanded=is_oggi):
        for j in range(2):
            idx = i + j
            pasto = st.session_state.pasti[idx]
            border = "3px solid #FF4B4B" if st.session_state.scambio_id == idx else "1px solid #eee"
            
            st.markdown(f"""<div style="border-left: {border}; padding-left: 10px; margin-bottom: 5px;">
                <small>{'☀️' if j==0 else '🌙'} {pasto['tipo']}</small></div>""", unsafe_allow_html=True)
            
            c1, c2, c3 = st.columns(3)
            n_c = c1.selectbox("Cereale", OPZIONI_CARBO, index=OPZIONI_CARBO.index(pasto['carbo']) if pasto['carbo'] in OPZIONI_CARBO else 0, key=f"c_{idx}")
            n_p = c2.selectbox("Proteina", OPZIONI_PROT, index=OPZIONI_PROT.index(pasto['prot']) if pasto['prot'] in OPZIONI_PROT else 0, key=f"p_{idx}")
            n_v = c3.selectbox("Verdura", OPZIONI_VERD, index=OPZIONI_VERD.index(pasto['verd']) if pasto['verd'] in OPZIONI_VERD else 0, key=f"v_{idx}")
            
            if n_c != pasto['carbo'] or n_p != pasto['prot'] or n_v != pasto['verd']:
                st.session_state.pasti[idx].update({"carbo": n_c, "prot": n_p, "verd": n_v})
                salva_su_disco()
                st.rerun()

            ca1, ca2 = st.columns(2)
            ca1.button("SPOSTA", key=f"m_{idx}", on_click=esegui_scambio, args=(idx,), use_container_width=True)
            st.session_state.pasti[idx]['locked'] = ca2.checkbox("Blocca", value=pasto['locked'], key=f"l_{idx}", on_change=salva_su_disco)

# --- CONTROLLI E RESET ---
st.divider()
all_p = [p['prot'] for p in st.session_state.pasti]
target = {"Pesce": 3, "Legumi": 4, "Carne Bianca": 3, "Uova": 2}
cols = st.columns(4)
for i, (name, goal) in enumerate(target.items()):
    count = all_p.count(name)
    cols[i].metric(name, f"{count}/{goal}", delta=count-goal, delta_color="normal" if count==goal else "inverse")

c1, c2 = st.columns(2)
c1.button("🎲 Rimescola Bilanciato", use_container_width=True, on_click=rimescola_bilanciato)
c2.button("🗑️ Reset / Nuova Settimana", use_container_width=True, on_click=lambda: (os.remove(FILE_SALVATAGGIO) if os.path.exists(FILE_SALVATAGGIO) else None, st.session_state.clear()))
