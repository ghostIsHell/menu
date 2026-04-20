import streamlit as st
import random

st.set_page_config(page_title="Menù Salute Interattivo", page_icon="🥗", layout="wide")

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
    st.session_state.scambio_id = None # Reset indice di scambio

st.title("🥗 Menù Salute Interattivo")

# --- LOGICA DI SCAMBIO AL TOCCO ---
if st.session_state.scambio_id is not None:
    p_selezionato = st.session_state.pasti[st.session_state.scambio_id]
    st.info(f"🔄 Selezionato: **{p_selezionato['giorno']} {p_selezionato['tipo']}**. Clicca su un altro pasto per scambiarlo.")
    if st.button("Annulla scambio"):
        st.session_state.scambio_id = None
        st.rerun()

# --- GRIGLIA SETTIMANALE ---
for i in range(0, 14, 2):
    st.markdown(f"### 📅 {st.session_state.pasti[i]['giorno']}")
    cols = st.columns(2)
    for j in range(2):
        idx = i + j
        pasto = st.session_state.pasti[idx]
        with cols[j]:
            # Grafica a colori
            colore = COLORI.get(pasto['prot'], '#fff')
            bordo = "3px solid #000" if st.session_state.scambio_id == idx else "1px solid #ccc"
            lucchetto = "🔒" if pasto['locked'] else "🔓"
            
            st.markdown(f"""
                <div style="background-color:{colore}; padding:20px; border-radius:15px; border:{bordo}; color: black; margin-bottom: 10px;">
                    <div style="font-size: 0.8em; font-weight: bold; opacity: 0.7;">{lucchetto} {pasto['tipo'].upper()}</div>
                    <div style="font-size: 1.2em; margin: 5px 0;"><strong>{pasto['carbo']}</strong></div>
                    <div style="font-size: 1.1em;">con {pasto['prot']}</div>
                    <div style="font-size: 0.9em; font-style: italic;">+ {pasto['verd']}</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Pulsante invisibile o piccolo per attivare lo scambio
            if st.button(f"Sposta/Scambia", key=f"btn_{idx}"):
                if st.session_state.scambio_id is None:
                    st.session_state.scambio_id = idx
                    st.rerun()
                else:
                    id1, id2 = st.session_state.scambio_id, idx
                    # Scambio Proteina e Verdura
                    st.session_state.pasti[id1]['prot'], st.session_state.pasti[id2]['prot'] = st.session_state.pasti[id2]['prot'], st.session_state.pasti[id1]['prot']
                    st.session_state.pasti[id1]['verd'], st.session_state.pasti[id2]['verd'] = st.session_state.pasti[id2]['verd'], st.session_state.pasti[id1]['verd']
                    st.session_state.scambio_id = None
                    st.rerun()
            
            st.session_state.pasti[idx]['locked'] = st.checkbox("Blocca", value=pasto['locked'], key=f"l_{idx}")

st.divider()

# Bottoni di controllo
c1, c2 = st.columns(2)
if c1.button("🎲 Rimescola Liberi"):
    idx_liberi = [i for i, p in enumerate(st.session_state.pasti) if not p['locked']]
    for attr in ['prot', 'verd']:
        vals = [st.session_state.pasti[k][attr] for k in idx_liberi]
        random.shuffle(vals)
        for i, k in enumerate(idx_liberi): st.session_state.pasti[k][attr] = vals[i]
    st.rerun()

if c2.button("🗑️ Reset Totale"):
    del st.session_state.pasti
    st.rerun()
