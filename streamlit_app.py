import streamlit as st
import random

st.set_page_config(page_title="Menù Salute Completo", page_icon="🥗", layout="wide")

# Palette colori Ministero/Salute
COLORI = {
    'Pesce': '#D1E8FF', 'Legumi': '#D4EDDA', 'Carne Bianca': '#FFF3CD',
    'Uova': '#F8D7DA', 'Formaggio': '#E2E3E5', 'Carne Rossa': '#FCE4EC'
}

# --- LOGICA DI INIZIALIZZAZIONE ---
if 'pasti' not in st.session_state:
    giorni = ['Lunedì', 'Martedì', 'Mercoledì', 'Giovedì', 'Venerdì', 'Sabato', 'Domenica']
    
    # Pool Dati
    prots = (['Legumi'] * 4 + ['Pesce'] * 3 + ['Carne Bianca'] * 3 + ['Uova'] * 2 + ['Formaggio'] * 1 + ['Carne Rossa'] * 1)
    carbo_p = ['Pasta Integrale', 'Pasta Integrale', 'Pasta Integrale', 'Riso', 'Farro', 'Gnocchi', 'Cous Cous']
    carbo_c = ['Pane Integrale', 'Pane Integrale', 'Pane Integrale', 'Patate', 'Patate', 'Pane Integrale', 'Pane Integrale']
    verdure = ['Zucchine', 'Asparagi', 'Spinaci', 'Bieta', 'Finocchi', 'Carote', 'Piselli', 'Insalata', 'Pomodori', 'Peperoni', 'Broccoli', 'Melanzane', 'Fagiolini', 'Carciofi']
    
    random.shuffle(prots); random.shuffle(carbo_p); random.shuffle(carbo_c); random.shuffle(verdure)
    
    st.session_state.pasti = []
    for i in range(14):
        g_idx = i // 2
        is_pranzo = (i % 2 == 0)
        st.session_state.pasti.append({
            "id": i,
            "giorno": giorni[g_idx],
            "tipo": "Pranzo" if is_pranzo else "Cena",
            "prot": prots[i],
            "carbo": carbo_p[g_idx] if is_pranzo else carbo_c[g_idx],
            "verd": verdure[i],
            "locked": False
        })

# --- INTERFACCIA ---
st.title("🥗 Il Mio Menù Completo")

# Area Scambio
with st.expander("🔄 Scambia Pasti"):
    opzioni = [f"{p['id']}: {p['giorno']} {p['tipo']} ({p['prot']})" for p in st.session_state.pasti]
    c1, c2 = st.columns(2)
    src = c1.selectbox("Sposta:", opzioni, key="src")
    dst = c2.selectbox("Al posto di:", opzioni, key="dst")
    if st.button("Conferma Scambio"):
        idx1, idx2 = int(src.split(":")[0]), int(dst.split(":")[0])
        # Scambiamo tutto il pacchetto tranne l'ID e il Giorno/Tipo
        st.session_state.pasti[idx1]['prot'], st.session_state.pasti[idx2]['prot'] = st.session_state.pasti[idx2]['prot'], st.session_state.pasti[idx1]['prot']
        st.session_state.pasti[idx1]['carbo'], st.session_state.pasti[idx2]['carbo'] = st.session_state.pasti[idx2]['carbo'], st.session_state.pasti[idx1]['carbo']
        st.session_state.pasti[idx1]['verd'], st.session_state.pasti[idx2]['verd'] = st.session_state.pasti[idx2]['verd'], st.session_state.pasti[idx1]['verd']
        st.rerun()

# Griglia Giornaliera
for i in range(0, 14, 2):
    st.markdown(f"### 📅 {st.session_state.pasti[i]['giorno']}")
    cols = st.columns(2)
    for j in range(2):
        idx = i + j
        pasto = st.session_state.pasti[idx]
        with cols[j]:
            st.session_state.pasti[idx]['locked'] = st.checkbox(f"Blocca {pasto['tipo']}", value=pasto['locked'], key=f"l_{idx}")
            lucchetto = "🔒" if pasto['locked'] else "🔓"
            colore = COLORI.get(pasto['prot'], '#fff')
            
            st.markdown(f"""
                <div style="background-color:{colore}; padding:20px; border-radius:15px; border:2px solid {'#333' if pasto['locked'] else '#eee'}; color: black;">
                    <div style="font-size: 0.8em; text-transform: uppercase; font-weight: bold; opacity: 0.7;">{lucchetto} {pasto['tipo']}</div>
                    <div style="font-size: 1.2em; margin: 10px 0;"><strong>{pasto['carbo']}</strong></div>
                    <div style="font-size: 1.1em;">con {pasto['prot']}</div>
                    <div style="font-size: 0.9em; font-style: italic; margin-top: 5px;">+ {pasto['verd']}</div>
                </div>
                """, unsafe_allow_html=True)

st.divider()

# Bottoni Controllo
c_b1, c_b2 = st.columns(2)
if c_b1.button("🎲 Rimescola Liberi", use_container_width=True):
    idx_liberi = [i for i, p in enumerate(st.session_state.pasti) if not p['locked']]
    for attr in ['prot', 'carbo', 'verd']:
        vals = [st.session_state.pasti[i][attr] for i in idx_liberi]
        random.shuffle(vals)
        for i, idx in enumerate(idx_liberi):
            st.session_state.pasti[idx][attr] = vals[i]
    st.rerun()

if c_b2.button("🗑️ Reset Totale", use_container_width=True):
    del st.session_state.pasti
    st.rerun()
