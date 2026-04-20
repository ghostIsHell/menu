import streamlit as st
import random

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Menù Salute Smart", page_icon="🥗")

COLORI = {
    'Pesce': '#D1E8FF', 'Legumi': '#D4EDDA', 'Carne Bianca': '#FFF3CD',
    'Uova': '#F8D7DA', 'Formaggio': '#E2E3E5', 'Carne Rossa': '#FCE4EC'
}

# --- INIZIALIZZAZIONE ---
if 'pasti' not in st.session_state:
    prots = (['Legumi'] * 4 + ['Pesce'] * 3 + ['Carne Bianca'] * 3 + 
             ['Uova'] * 2 + ['Formaggio'] * 1 + ['Carne Rossa'] * 1)
    random.shuffle(prots)
    giorni = ['Lunedì', 'Martedì', 'Mercoledì', 'Giovedì', 'Venerdì', 'Sabato', 'Domenica']
    # Aggiungiamo 'locked': False per ogni pasto
    st.session_state.pasti = [{"id": i, "giorno": giorni[i//2], "tipo": "Pranzo" if i%2==0 else "Cena", "prot": prots[i], "locked": False} for i in range(14)]

st.title("🥗 Menù con Funzione Blocca")

# --- AREA DI SCAMBIO ---
with st.expander("🔄 Strumento di Scambio Rapido", expanded=False):
    opzioni = [f"{p['id']}: {p['giorno']} {p['tipo']} ({p['prot']})" for p in st.session_state.pasti]
    col1, col2 = st.columns(2)
    with col1: src = st.selectbox("Sposta questo:", opzioni, key="src")
    with col2: dst = st.selectbox("Al posto di:", opzioni, key="dst")
    if st.button("SCAMBIA"):
        idx1, idx2 = int(src.split(":")[0]), int(dst.split(":")[0])
        st.session_state.pasti[idx1]['prot'], st.session_state.pasti[idx2]['prot'] = st.session_state.pasti[idx2]['prot'], st.session_state.pasti[idx1]['prot']
        st.rerun()

# --- VISUALIZZAZIONE SETTIMANALE ---
for i in range(0, 14, 2):
    st.subheader(f"📅 {st.session_state.pasti[i]['giorno']}")
    cols = st.columns(2)
    for j in range(2):
        idx = i + j
        pasto = st.session_state.pasti[idx]
        with cols[j]:
            # Checkbox per bloccare il pasto
            st.session_state.pasti[idx]['locked'] = st.checkbox("Blocca", value=pasto['locked'], key=f"lock_{idx}")
            
            lucchetto = "🔒" if st.session_state.pasti[idx]['locked'] else "🔓"
            colore = COLORI.get(pasto['prot'], '#fff')
            
            st.markdown(f"""
                <div style="background-color:{colore}; padding:15px; border-radius:10px; border:2px solid {'#333' if pasto['locked'] else '#ccc'}; color: black;">
                    <strong>{lucchetto} {pasto['tipo'].upper()}</strong><br>{pasto['prot']}
                </div>
                """, unsafe_allow_html=True)

st.divider()

# --- FUNZIONE RIMESCOLA SOLO NON BLOCCATI ---
if st.button("🎲 Rimescola Liberi"):
    # Prendi le proteine dei pasti non bloccati
    liberi_idx = [i for i, p in enumerate(st.session_state.pasti) if not p['locked']]
    prots_libere = [st.session_state.pasti[i]['prot'] for i in liberi_idx]
    random.shuffle(prots_libere)
    # Riapplica le proteine rimescolate solo ai posti liberi
    for i, idx in enumerate(liberi_idx):
        st.session_state.pasti[idx]['prot'] = prots_libere[i]
    st.rerun()

if st.button("🗑️ Reset Totale"):
    del st.session_state.pasti
    st.rerun()
