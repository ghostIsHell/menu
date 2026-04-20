import streamlit as st
import random

st.set_page_config(page_title="Menù Salute", page_icon="🥗", layout="wide")

# Palette colori originale
COLORI = {
    'Pesce': '#D1E8FF', 'Legumi': '#D4EDDA', 'Carne Bianca': '#FFF3CD',
    'Uova': '#F8D7DA', 'Formaggio': '#E2E3E5', 'Carne Rossa': '#FCE4EC'
}

# --- INIZIALIZZAZIONE ---
if 'pasti' not in st.session_state:
    giorni = ['Lunedì', 'Martedì', 'Mercoledì', 'Giovedì', 'Venerdì', 'Sabato', 'Domenica']
    prots = (['Legumi'] * 4 + ['Pesce'] * 3 + ['Carne Bianca'] * 3 + ['Uova'] * 2 + ['Formaggio'] * 1 + ['Carne Rossa'] * 1)
    carbo_p = ['Pasta Integrale', 'Pasta Integrale', 'Pasta Integrale', 'Riso', 'Farro', 'Gnocchi', 'Cous Cous']
    carbo_c = ['Pane Integrale', 'Pane Integrale', 'Pane Integrale', 'Patate', 'Patate', 'Pane Integrale', 'Pane Integrale']
    verdure = ['Zucchine', 'Asparagi', 'Spinaci', 'Bieta', 'Finocchi', 'Carote', 'Piselli', 'Insalata', 'Pomodori', 'Peperoni', 'Broccoli', 'Melanzane', 'Fagiolini', 'Carciofi']
    
    random.shuffle(prots); random.shuffle(carbo_p); random.shuffle(carbo_c); random.shuffle(verdure)
    
    st.session_state.pasti = []
    for i in range(14):
        is_pranzo = (i % 2 == 0)
        st.session_state.pasti.append({
            "id": i, "giorno": giorni[i//2], "tipo": "Pranzo" if is_pranzo else "Cena",
            "prot": prots[i], "carbo": carbo_p[i//2] if is_pranzo else carbo_c[i//2],
            "verd": verdure[i], "locked": False
        })
    st.session_state.scambio_id = None

st.title("🥗 Il Mio Menù Modificabile")

# --- LOGICA SCAMBIO AL TOCCO ---
if st.session_state.scambio_id is not None:
    p_sel = st.session_state.pasti[st.session_state.scambio_id]
    st.info(f"🔄 Selezionato: **{p_sel['giorno']} {p_sel['tipo']}**. Clicca su un altro pasto per scambiare condimenti e verdure.")
    if st.button("Annulla scambio"):
        st.session_state.scambio_id = None
        st.rerun()

# --- INTERFACCIA A EXPANDER ---
for i in range(0, 14, 2):
    giorno_nome = st.session_state.pasti[i]['giorno']
    with st.expander(f"📅 {giorno_nome}", expanded=True):
        col1, col2 = st.columns(2)
        
        for j, col in enumerate([col1, col2]):
            idx = i + j
            pasto = st.session_state.pasti[idx]
            colore = COLORI.get(pasto['prot'], '#fff')
            bordo = "3px solid #000" if st.session_state.scambio_id == idx else "1px solid #eee"
            
            with col:
                # Box Grafico Colorato
                st.markdown(f"""
                    <div style="background-color:{colore}; padding:15px; border-radius:10px; border:{bordo}; color: black; margin-bottom:10px;">
                        <div style="font-size: 0.8em; font-weight: bold; opacity: 0.7;">{'🔒' if pasto['locked'] else '🔓'} {pasto['tipo'].upper()}</div>
                        <div style="font-size: 1.1em; margin: 5px 0;"><strong>{pasto['carbo']}</strong></div>
                        <div style="font-size: 1em;">con {pasto['prot']}</div>
                        <div style="font-size: 0.85em; font-style: italic;">+ {pasto['verd']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Pulsanti di controllo
                c_btn1, c_btn2 = st.columns(2)
                if c_btn1.button("Sposta", key=f"mov_{idx}"):
                    if st.session_state.scambio_id is None:
                        st.session_state.scambio_id = idx
                    else:
                        id1, id2 = st.session_state.scambio_id, idx
                        st.session_state.pasti[id1]['prot'], st.session_state.pasti[id2]['prot'] = st.session_state.pasti[id2]['prot'], st.session_state.pasti[id1]['prot']
                        st.session_state.pasti[id1]['verd'], st.session_state.pasti[id2]['verd'] = st.session_state.pasti[id2]['verd'], st.session_state.pasti[id1]['verd']
                        st.session_state.scambio_id = None
                    st.rerun()
                
                st.session_state.pasti[idx]['locked'] = c_btn2.checkbox("Blocca", value=pasto['locked'], key=f"l_{idx}")

# --- CONTROLLO NUTRIZIONALE E BOTTONI ---
st.divider()
all_prots = [p['prot'] for p in st.session_state.pasti]
st.subheader("📊 Controllo Frequenze")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Pesce", f"{all_prots.count('Pesce')}/3")
m2.metric("Legumi", f"{all_prots.count('Legumi')}/4")
m3.metric("Carne Bianca", f"{all_prots.count('Carne Bianca')}/3")
m4.metric("Uova", f"{all_prots.count('Uova')}/2")

c_b1, c_b2, c_b3 = st.columns(3)
if c_b1.button("🎲 Rimescola Liberi", use_container_width=True):
    lib_idx = [i for i, p in enumerate(st.session_state.pasti) if not p['locked']]
    for attr in ['prot', 'verd']:
        vals = [st.session_state.pasti[k][attr] for k in lib_idx]
        random.shuffle(vals)
        for i, k in enumerate(lib_idx): st.session_state.pasti[k][attr] = vals[i]
    st.rerun()

if c_b2.button("🔄 Nuova Base Totale", use_container_width=True):
    del st.session_state.pasti
    st.rerun()

if c_b3.button("🗑️ Reset Blocchi", use_container_width=True):
    for p in st.session_state.pasti: p['locked'] = False
    st.rerun()
