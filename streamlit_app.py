import streamlit as st
import random
import pandas as pd
import os
import uuid
from datetime import datetime

# --- 1. COSTANTI E CONFIGURAZIONE SECONDO LINEE GUIDA CREA/MINISTERO ---
CONFIG = {
    "FILE_SALVATAGGIO": "menu_salute_crea.csv",
    "EMOJI_PROT": {
        'Legumi': '🟢', 'Pesce': '🔵', 'Carne Bianca': '🟡', 
        'Uova': '🔴', 'Formaggio': '⚪', 'Carne Rossa': '🟣'
    },
    "CARBO_PRANZO": ['Pasta Integrale', 'Riso Integrale', 'Farro', 'Orzo', 'Gnocchi'],
    "CARBO_CENA": ['Pane Integrale', 'Patate', 'Cous Cous Integrale'],
    "OPZIONI_VERD": ['Zucchine', 'Asparagi', 'Spinaci', 'Bieta', 'Finocchi', 'Carote', 'Piselli', 
                     'Insalata', 'Pomodori', 'Peperoni', 'Broccoli', 'Melanzane', 'Fagiolini'],
    # Frequenze ottimizzate sui 14 pasti settimanali
    "TARGET_PROTEINE": {
        "Legumi": 4,       # Linee guida: 3-5 volte
        "Pesce": 3,        # Linee guida: 2-3 volte
        "Carne Bianca": 3, # Linee guida: fino a 3 totali (prediligendo bianche)
        "Uova": 2,         # Linee guida: 1-4 uova (2 pasti da 2 uova o 1 da 2)
        "Formaggio": 1,    # Linee guida: 2 volte (teniamo 1 per spazio a carne rossa)
        "Carne Rossa": 1   # Linee guida: massimo 1 volta
    },
    "PORZIONI": {
        "Cereali (Pasta, Riso)": "80g (a crudo)",
        "Pane": "50g (una fetta/rosetta)",
        "Carne/Pesce": "100g",
        "Legumi secchi": "50g",
        "Legumi cotti/scatola": "150g",
        "Verdura foglia": "80-100g",
        "Altre verdure": "200g"
    }
}
CONFIG["TUTTI_CARBO"] = sorted(list(set(CONFIG["CARBO_PRANZO"] + CONFIG["CARBO_CENA"])))

# --- 2. LOGICA DI BUSINESS ---
def get_index_safe(lista, valore):
    try: return lista.index(valore)
    except: return 0

def build_protein_pool():
    """Genera il pool esatto basato sulle frequenze del Ministero."""
    pool = []
    for prot, count in CONFIG["TARGET_PROTEINE"].items():
        pool.extend([prot] * count)
    # Se per qualche motivo il pool non è di 14, riempiamo con legumi (scelta più sana)
    while len(pool) < 14:
        pool.append("Legumi")
    random.shuffle(pool)
    return pool

def genera_pasti(pasti_esistenti=None):
    giorni = ['Lunedì', 'Martedì', 'Mercoledì', 'Giovedì', 'Venerdì', 'Sabato', 'Domenica']
    prot_pool = build_protein_pool()
    nuovi_pasti = []
    
    for i in range(14):
        tipo = "Pranzo" if i%2 == 0 else "Cena"
        if pasti_esistenti and i < len(pasti_esistenti) and pasti_esistenti[i].get('locked'):
            pasto_vecchio = pasti_esistenti[i]
            nuovi_pasti.append(pasto_vecchio)
            if pasto_vecchio['prot'] in prot_pool:
                prot_pool.remove(pasto_vecchio['prot'])
        else:
            carbo = random.choice(CONFIG["CARBO_PRANZO"] if tipo == "Pranzo" else CONFIG["CARBO_CENA"])
            nuovi_pasti.append({
                "id": i, "giorno": giorni[i//2], "tipo": tipo,
                "prot": prot_pool.pop() if prot_pool else "Legumi",
                "carbo": carbo, "verd": random.choice(CONFIG["OPZIONI_VERD"]), "locked": False
            })
    return nuovi_pasti

# --- 3. DATA PERSISTENCE ---
def load_data():
    if os.path.exists(CONFIG["FILE_SALVATAGGIO"]):
        try: return pd.read_csv(CONFIG["FILE_SALVATAGGIO"]).to_dict('records')
        except: return genera_pasti()
    return genera_pasti()

def save_data():
    pd.DataFrame(st.session_state.pasti).to_csv(CONFIG["FILE_SALVATAGGIO"], index=False)

# --- 4. COMPONENTI UI ---
def render_header():
    st.title("🥗 Menù Salute: Linee Guida Ministeriali")
    
    # Sezione Info Porzioni
    with st.expander("ℹ️ Visualizza Porzioni Standard (CREA)"):
        cols = st.columns(2)
        items = list(CONFIG["PORZIONI"].items())
        mid = len(items)//2
        with cols[0]:
            for k, v in items[:mid]: st.write(f"**{k}**: {v}")
        with cols[1]:
            for k, v in items[mid:]: st.write(f"**{k}**: {v}")

    if st.session_state.scambio_idx is not None:
        p1 = st.session_state.pasti[st.session_state.scambio_idx]
        st.warning(f"🔄 Spostamento: Selezionato **{p1['giorno']} {p1['tipo']}**. Dove vuoi metterlo?")
        if st.button("Annulla"):
            st.session_state.scambio_idx = None
            st.rerun()
    
    if st.button("🔄 GENERA NUOVO MENÙ BILANCIATO", use_container_width=True, type="primary"):
        st.session_state.pasti = genera_pasti(st.session_state.pasti)
        st.session_state.menu_key = str(uuid.uuid4())
        save_data()
        st.rerun()

def render_pasto_editor(idx):
    pasto = st.session_state.pasti[idx]
    is_selezionato = (st.session_state.scambio_idx == idx)
    
    with st.container(border=True):
        st.markdown(f"**{'☀️' if pasto['tipo'] == 'Pranzo' else '🌙'} {pasto['tipo']}**")
        
        new_p = st.selectbox("Proteina", list(CONFIG["EMOJI_PROT"].keys()), 
                             index=get_index_safe(list(CONFIG["EMOJI_PROT"].keys()), pasto['prot']),
                             key=f"p_{idx}_{st.session_state.menu_key}")
        
        new_c = st.selectbox("Carbo", CONFIG["TUTTI_CARBO"], 
                             index=get_index_safe(CONFIG["TUTTI_CARBO"], pasto['carbo']),
                             key=f"c_{idx}_{st.session_state.menu_key}")
        
        new_v = st.selectbox("Verdura", CONFIG["OPZIONI_VERD"], 
                             index=get_index_safe(CONFIG["OPZIONI_VERD"], pasto['verd']),
                             key=f"v_{idx}_{st.session_state.menu_key}")
        
        if new_p != pasto['prot'] or new_c != pasto['carbo'] or new_v != pasto['verd']:
            st.session_state.pasti[idx].update({"prot": new_p, "carbo": new_c, "verd": new_v})
            save_data()

        c1, c2 = st.columns(2)
        pasto['locked'] = c1.checkbox("Blocca", value=bool(pasto['locked']), key=f"l_{idx}_{st.session_state.menu_key}")
        
        if c2.button("↔️ SPOSTA", key=f"bt_{idx}_{st.session_state.menu_key}", use_container_width=True, type="secondary" if not is_selezionato else "primary"):
            if st.session_state.scambio_idx is None:
                st.session_state.scambio_idx = idx
                st.rerun()
            else:
                idx1, idx2 = st.session_state.scambio_idx, idx
                for campo in ['prot', 'carbo', 'verd', 'locked']:
                    st.session_state.pasti[idx1][campo], st.session_state.pasti[idx2][campo] = \
                    st.session_state.pasti[idx2][campo], st.session_state.pasti[idx1][campo]
                st.session_state.scambio_idx = None
                st.session_state.menu_key = str(uuid.uuid4())
                save_data()
                st.rerun()

# --- 5. MAIN ---
def main():
    st.set_page_config(page_title="Menù Salute Ministeriale", layout="wide")
    
    if 'menu_key' not in st.session_state: st.session_state.menu_key = str(uuid.uuid4())
    if 'pasti' not in st.session_state: st.session_state.pasti = load_data()
    if 'scambio_idx' not in st.session_state: st.session_state.scambio_idx = None

    render_header()

    giorni_it = ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"]
    oggi_idx = datetime.now().weekday()

    for i, g_nome in enumerate(giorni_it):
        is_oggi = (i == oggi_idx)
        with st.expander(f"{'📍 ' if is_oggi else ''}{g_nome.upper()}", expanded=is_oggi):
            idx_pasti = [idx for idx, p in enumerate(st.session_state.pasti) if p['giorno'] == g_nome]
            col_sx, col_dx = st.columns(2)
            with col_sx: render_pasto_editor(idx_pasti[0])
            with col_dx: render_pasto_editor(idx_pasti[1])

    # Statistiche con Target Ministeriali
    st.divider()
    st.subheader("📊 Verifica Frequenze Settimanali")
    all_prots = [p['prot'] for p in st.session_state.pasti]
    cols = st.columns(len(CONFIG["TARGET_PROTEINE"]))
    for i, (nome, target) in enumerate(CONFIG["TARGET_PROTEINE"].items()):
        attuale = all_prots.count(nome)
        emoji = CONFIG["EMOJI_PROT"][nome]
        # Delta colorato: verde se rispetta il range, rosso se eccessivo/scarso
        st_col = cols[i]
        st_col.metric(f"{emoji} {nome}", f"{attuale}", delta=f"Target: {target}", delta_color="off")

if __name__ == "__main__":
    main()
