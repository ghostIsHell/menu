import streamlit as st
import pandas as pd
import random

# Configurazione Pagina
st.set_page_config(page_title="Il Mio Menù Salute", page_icon="🥗")

st.title("🥗 Generatore Menù Settimanale")
st.write("Basato sulle linee guida ufficiali del Ministero della Salute.")

# Inizializzazione dati se non esistono (per "fissare" il menù)
if 'menu_settimanale' not in st.session_state:
    st.session_state.menu_settimanale = None

def genera_menu():
    giorni = ['Lunedì', 'Martedì', 'Mercoledì', 'Giovedì', 'Venerdì', 'Sabato', 'Domenica']
    proteine = (['Legumi'] * 4 + ['Pesce'] * 3 + ['Carne Bianca'] * 3 + 
                ['Uova'] * 2 + ['Formaggio'] * 1 + ['Carne Rossa'] * 1)
    carbo_p = ['Pasta Integrale', 'Pasta Integrale', 'Pasta Integrale', 'Riso', 'Farro', 'Gnocchi', 'Cous Cous']
    carbo_c = ['Pane Integrale', 'Pane Integrale', 'Pane Integrale', 'Patate', 'Patate', 'Pane Integrale', 'Pane Integrale']
    verdure = ['Zucchine', 'Asparagi', 'Spinaci', 'Bieta', 'Finocchi', 'Carote', 'Piselli', 
               'Insalata Mista', 'Pomodori', 'Peperoni', 'Broccoli', 'Melanzane', 'Fagiolini', 'Carciofi']

    # Logica di bilanciamento
    for _ in range(2000):
        random.shuffle(proteine); random.shuffle(carbo_p); random.shuffle(carbo_c); random.shuffle(verdure)
        valido = True
        for i in range(7):
            p_p, p_c = proteine[i*2], proteine[i*2+1]
            if p_p == p_c or (p_p == 'Pesce' and p_c == 'Pesce'): valido = False; break
            if i > 0 and p_p == 'Pesce' and proteine[(i-1)*2+1] == 'Pesce': valido = False; break
        if valido:
            res = []
            for i in range(7):
                res.append({"Giorno": giorni[i], "Pranzo": f"{carbo_p[i]} con {proteine[i*2]} e {verdure[i*2]}", 
                            "Cena": f"{proteine[i*2+1]} con {verdure[i*2+1]} e {carbo_c[i]}"})
            return pd.DataFrame(res)

# Pulsante per generare
if st.button("🔄 Genera Nuovo Menù"):
    st.session_state.menu_settimanale = genera_menu()

# Visualizzazione Menù
if st.session_state.menu_settimanale is not None:
    for index, row in st.session_state.menu_settimanale.iterrows():
        with st.expander(f"📅 {row['Giorno']}"):
            st.markdown(f"**☀️ Pranzo:** {row['Pranzo']}")
            st.markdown(f"**🌙 Cena:** {row['Cena']}")
    
    # Lista della Spesa Automatica
    if st.checkbox("🛒 Mostra Lista della Spesa (per 2 persone)"):
        all_text = " ".join(st.session_state.menu_settimanale['Pranzo']) + " " + " ".join(st.session_state.menu_settimanale['Cena'])
        st.write(f"- 🐟 Pesce: {all_text.count('Pesce') * 300}g")
        st.write(f"- 🥩 Carne Bianca: {all_text.count('Carne Bianca') * 250}g")
        st.write(f"- 🥚 Uova: {all_text.count('Uova') * 4} unità")
        st.write(f"- 🌿 Legumi: {all_text.count('Legumi') * 300}g (cotti)")
else:
    st.info("Clicca sul pulsante sopra per generare il tuo primo menù!")
