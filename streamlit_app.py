import streamlit as st
import random

# --- CONFIGURAZIONE ---
if 'pasti' not in st.session_state:
    # Generazione iniziale bilanciata
    prots = (['Legumi'] * 4 + ['Pesce'] * 3 + ['Carne Bianca'] * 3 + ['Uova'] * 2 + ['Formaggio'] * 1 + ['Carne Rossa'] * 1)
    random.shuffle(prots)
    giorni = ['Lunedì', 'Martedì', 'Mercoledì', 'Giovedì', 'Venerdì', 'Sabato', 'Domenica']
    # Creiamo una lista piatta di 14 pasti (0=Lun Pranzo, 1=Lun Cena, etc.)
    st.session_state.pasti = [{"id": i, "giorno": giorni[i//2], "tipo": "Pranzo" if i%2==0 else "Cena", "prot": prots[i]} for i in range(14)]

st.title("🥗 Menù con Scambio Automatico")
st.write("Se sposti una proteina, quella di destinazione prenderà il suo posto per non rompere l'equilibrio.")

# --- LOGICA DI SCAMBIO ---
col_scambio1, col_scambio2 = st.columns(2)
with col_scambio1:
    sorgente = st.selectbox("Sposta il pasto di:", [f"{p['giorno']} {p['tipo']} ({p['prot']})" for p in st.session_state.pasti], key="src")
with col_scambio2:
    destinazione = st.selectbox("Al posto di:", [f"{p['giorno']} {p['tipo']} ({p['prot']})" for p in st.session_state.pasti], key="dst")

if st.button("🔄 Conferma Scambio"):
    idx1 = [f"{p['giorno']} {p['tipo']} ({p['prot']})" for p in st.session_state.pasti].index(sorgente)
    idx2 = [f"{p['giorno']} {p['tipo']} ({p['prot']})" for p in st.session_state.pasti].index(destinazione)
    
    # Lo scambio vero e proprio (Swap)
    st.session_state.pasti[idx1]['prot'], st.session_state.pasti[idx2]['prot'] = st.session_state.pasti[idx2]['prot'], st.session_state.pasti[idx1]['prot']
    st.success(f"Scambiato {st.session_state.pasti[idx2]['prot']} con {st.session_state.pasti[idx1]['prot']}!")
    st.rerun()

# --- VISUALIZZAZIONE ---
for i in range(0, 14, 2):
    with st.container():
        c1, c2 = st.columns(2)
        p1, p2 = st.session_state.pasti[i], st.session_state.pasti[i+1]
        c1.info(f"**{p1['giorno']} Pranzo**\n\n{p1['prot']}")
        c2.warning(f"**{p2['giorno']} Cena**\n\n{p2['prot']}")
