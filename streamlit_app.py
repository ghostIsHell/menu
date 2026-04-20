import streamlit as st
import random

st.set_page_config(page_title="Menù Salute", page_icon="🥗", layout="wide")

# Emoji per identificare le proteine
EMOJI_PROT = {
    'Pesce': '🔵', 'Legumi': '🟢', 'Carne Bianca': '🟡',
    'Uova': '🔴', 'Formaggio': '⚪', 'Carne Rossa': '🟣'
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

st.title("🥗 Il Mio Menù Benessere")

# --- LOGICA SCAMBIO ---
if st.session_state.scambio_id is not None:
    p_sel = st.session_state.pasti[st.session_state.scambio_id]
    st.warning(f"🔄 Scambio: **{p_sel['giorno']} {p_sel['tipo']}** selezionato. Clicca 'Sposta' su un altro pasto.")
    if st.button("Annulla"):
        st.session_state.scambio_id = None
        st.rerun()

# --- INTERFACCIA (Tendine Chiuse di Default) ---
for i in range(0, 14, 2):
    giorno_nome = st.session_state.pasti[i]['giorno']
    # expanded=False imposta le tendine chiuse all'avvio
    with st.expander(f"📅 {giorno_nome}", expanded=False):
        for j in range(2):
            idx = i + j
            pasto = st.session_state.pasti[idx]
            emoji = EMOJI_PROT.get(pasto['prot'], '🔹')
            icona_tipo = "☀️" if j == 0 else "🌙"
            
            col_testo, col_sposta, col_lock = st.columns([0.65, 0.18, 0.17])
            
            with col_testo:
                st.markdown(f"""
                <div style="line-height: 1.2; color: #31333F;">
                    <span style="font-size: 0.85em; opacity: 0.6;">{icona_tipo} {pasto['tipo'].upper()}</span><br>
                    <span style="font-size: 1.15em; font-weight: bold;">{pasto['carbo']}</span> 
                    <span style="font-size: 1em;">con {emoji} {pasto['prot']} e {pasto['verd']}</span>
                </div>
                """, unsafe_allow_html=True)
            
            with col_sposta:
                if st.button("Sposta", key=f"m_{idx}"):
                    if st.session_state.scambio_id is None:
                        st.session_state.scambio_id = idx
                    else:
                        id1, id2 = st.session_state.scambio_id, idx
                        st.session_state.pasti[id1]['prot'], st.session_state.pasti[id2]['prot'] = st.session_state.pasti[id2]['prot'], st.session_state.pasti[id1]['prot']
                        st.session_state.pasti[id1]['verd'], st.session_state.pasti[id2]['verd'] = st.session_state.pasti[id2]['verd'], st.session_state.pasti[id1]['verd']
                        st.session_state.scambio_id = None
                    st.rerun()
            
            with col_lock:
                st.session_state.pasti[idx]['locked'] = st.checkbox("Blocca", value=pasto['locked'], key=f"l_{idx}")

# --- CONTROLLO NUTRIZIONALE ---
st.divider()
all_prots = [p['prot'] for p in st.session_state.pasti]
st.subheader("📊 Bilancio Settimanale")
cols_m = st.columns(4)
obiettivi = [("Pesce", 3), ("Legumi", 4), ("Carne Bianca", 3), ("Uova", 2)]
for i, (nome, target) in enumerate(obiettivi):
    attuale = all_prots.count(nome)
    cols_m[i].metric(nome, f"{attuale}/{target}")

# --- LISTA DELLA SPESA ---
with st.expander("🛒 Lista della Spesa (x2 persone)", expanded=False):
    st.write("Proteine:")
    st.write(f"- 🐟 Pesce: {all_prots.count('Pesce')*300}g")
    st.write(f"- 🌿 Legumi: {all_prots.count('Legumi')*300}g (cotti)")
    st.write(f"- 🥩 Carne Bianca: {all_prots.count('Carne Bianca')*250}g")
    st.write(f"- 🥚 Uova: {all_prots.count('Uova')*4} unità")
    st.write(f"- 🧀 Formaggio: {all_prots.count('Formaggio')*200}g")
    st.write(f"- 🥩 Carne Rossa: {all_prots.count('Carne Rossa')*250}g")

# --- BOTTONI FINALI ---
st.divider()
c_b1, c_b2 = st.columns(2)
if c_b1.button("🎲 Rimescola Liberi", use_container_width=True):
    lib_idx = [k for k, p in enumerate(st.session_state.pasti) if not p['locked']]
    for attr in ['prot', 'verd']:
        vals = [st.session_state.pasti[k][attr] for k in lib_idx]
        random.shuffle(vals)
        for idx_val, k in enumerate(lib_idx): st.session_state.pasti[k][attr] = vals[idx_val]
    st.rerun()

if c_b2.button("🔄 Nuova Base / Reset", use_container_width=True):
    st.session_state.clear()
    st.rerun()
