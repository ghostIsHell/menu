import streamlit as st
import random

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Menù Salute Smart", page_icon="🎨")

# Definizione colori per proteine
COLORI = {
    'Pesce': '#D1E8FF',      # Blu chiaro
    'Legumi': '#D4EDDA',     # Verde chiaro
    'Carne Bianca': '#FFF3CD', # Giallo chiaro
    'Uova': '#F8D7DA',       # Rosso chiaro (rosa)
    'Formaggio': '#E2E3E5',  # Grigio chiaro
    'Carne Rossa': '#FCE4EC' # Rosa/Viola
}

if 'pasti' not in st.session_state:
    prots = (['Legumi'] * 4 + ['Pesce'] * 3 + ['Carne Bianca'] * 3 + 
             ['Uova'] * 2 + ['Formaggio'] * 1 + ['Carne Rossa'] * 1)
    random.shuffle(prots)
    giorni = ['Lunedì', 'Martedì', 'Mercoledì', 'Giovedì', 'Venerdì', 'Sabato', 'Domenica']
    st.session_state.pasti = [{"id": i, "giorno": giorni[i//2], "tipo": "Pranzo" if i%2==0 else "Cena", "prot": prots[i]} for i in range(14)]

st.title("🥗 Menù Smart a Colori")
st.write("Usa lo scambio per bilanciare i colori nella settimana!")

# --- AREA DI SCAMBIO ---
with st.expander("🔄 Strumento di Scambio Rapido", expanded=True):
    col1, col2, col3 = st.columns([2, 2, 1])
    opzioni = [f"{p['id']}: {p['giorno']} {p['tipo']} ({p['prot']})" for p in st.session_state.pasti]
    
    with col1:
        src = st.selectbox("Sposta questo:", opzioni)
    with col2:
        dst = st.selectbox("Al posto di:", opzioni)
    with col3:
        st.write(" ") # Spazio estetico
        if st.button("SCAMBIA"):
            idx1 = int(src.split(":")[0])
            idx2 = int(dst.split(":")[0])
            # Swap
            st.session_state.pasti[idx1]['prot'], st.session_state.pasti[idx2]['prot'] = \
            st.session_state.pasti[idx2]['prot'], st.session_state.pasti[idx1]['prot']
            st.rerun()

# --- VISUALIZZAZIONE SETTIMANALE ---
for i in range(0, 14, 2):
    p_pranzo = st.session_state.pasti[i]
    p_cena = st.session_state.pasti[i+1]
    
    st.subheader(f"📅 {p_pranzo['giorno']}")
    c1, c2 = st.columns(2)
    
    # BOX PRANZO
    c1.markdown(f"""
        <div style="background-color:{COLORI.get(p_pranzo['prot'], '#fff')}; padding:15px; border-radius:10px; border:1px solid #ccc; color: black;">
            <strong>☀️ PRANZO</strong><br>{p_pranzo['prot']}
        </div>
        """, unsafe_allow_html=True)
    
    # BOX CENA
    c2.markdown(f"""
        <div style="background-color:{COLORI.get(p_cena['prot'], '#fff')}; padding:15px; border-radius:10px; border:1px solid #ccc; color: black;">
            <strong>🌙 CENA</strong><br>{p_cena['prot']}
        </div>
        """, unsafe_allow_html=True)

st.divider()
if st.button("🗑️ Reset Totale"):
    del st.session_state.pasti
    st.rerun()
