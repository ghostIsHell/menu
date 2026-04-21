import streamlit as st
import random
import pandas as pd
import os
import uuid
from datetime import datetime

# --- 1. COSTANTI E STAGIONALITÀ ---
CONFIG = {
    "FILE_SALVATAGGIO": "menu_salute_crea.csv",
    "EMOJI_PROT": {
        'Legumi': '🟢', 'Pesce': '🔵', 'Carne Bianca': '🟡', 
        'Uova': '🔴', 'Formaggio': '⚪', 'Carne Rossa': '🟣'
    },
    "CARBO_PRANZO": ['Pasta Integrale', 'Riso Integrale', 'Farro', 'Orzo', 'Gnocchi'],
    "CARBO_CENA": ['Pane Integrale', 'Patate', 'Cous Cous Integrale'],
    "TARGET_PROTEINE": {
        "Legumi": 4, "Pesce": 3, "Carne Bianca": 3, "Uova": 2, "Formaggio": 1, "Carne Rossa": 1
    },
    "VERDURE_STAGIONALI": {
        "Inverno": ['Broccoli', 'Cavolfiore', 'Finocchi', 'Spinaci', 'Bietole', 'Carciofi', 'Zucca'],
        "Primavera": ['Asparagi', 'Piselli', 'Fave', 'Carciofi', 'Zucchine', 'Insalata'],
        "Estate": ['Pomodori', 'Peperoni', 'Melanzane', 'Zucchine', 'Fagiolini', 'Cetrioli'],
        "Autunno": ['Zucca', 'Funghi', 'Broccoli', 'Spinaci', 'Finocchi', 'Carote']
    },
    "PORZIONI": {
        "Cereali (Pasta, Riso)": "80g", "Pane": "50g", "Carne/Pesce": "100g",
        "Legumi secchi": "50g", "Legumi scatola": "150g", "Verdura": "200g"
    }
}

# --- 2. FUNZIONI DI SUPPORTO ---
def get_stagione():
    mese = datetime.now().month
    if mese in [12, 1, 2]: return "Inverno"
    if mese in [3, 4, 5]: return "Primavera"
    if mese in [6, 7, 8]: return "Estate"
    return "Autunno"

# Impostiamo le verdure in base alla stagione attuale
STAGIONE_ATTUALE = get_stagione()
OPZIONI_VERD_ATTUALI = CONFIG["VERDURE_STAGIONALI"][STAGIONE_ATTUALE]
CONFIG["TUTTI_CARBO"] = sorted(list(set(CONFIG["CARBO_PRANZO"] + CONFIG["CARBO_CENA"])))

def get_index_safe(lista, valore):
    try: return lista.index(valore)
    except: return 0

def build_protein_pool():
    pool = []
    for prot, count in CONFIG["TARGET_PROTEINE"].items():
        pool.extend([prot] * count)
    while len(pool) < 14: pool.append("Legumi")
    random.shuffle(pool)
    return pool

def genera_pasti(pasti_esistenti=None):
    giorni = ['Lunedì', 'Martedì', 'Mercoledì', 'Giovedì', 'Venerdì', 'Sabato', 'Domenica']
    prot_pool = build_protein_pool()
    nuovi_pasti = []
    
    for i in range(14):
        tipo = "Pranzo" if i%2 == 0 else "Cena"
        if pasti_esistenti and i < len(pasti_esistenti) and pasti_esistenti[i].get('locked'):
            nuovi_pasti.append(pasti_esistenti[i])
            if pasti_esistenti[i]['prot'] in prot_pool: prot_pool.remove(pasti_esistenti[i]['prot'])
        else:
            nuovi_pasti.append({
                "id": i, "giorno": giorni[i//2], "tipo": tipo,
                "prot": prot_pool.pop() if prot_pool else "Legumi",
                "carbo": random.choice(CONFIG["CARBO_PRANZO"] if tipo == "Pranzo" else CONFIG["CARBO_CENA"]),
                "verd": random.choice(OPZIONI_VERD_ATTUALI), "locked": False
            })
    return nuovi_pasti

# --- 3. STORAGE ---
def load_data():
    if os.path.exists(CONFIG["FILE_SALVATAGGIO"]):
        try: return pd.read_csv(CONFIG["FILE_SALVATAGGIO"]).to_dict('records')
        except: return genera_pasti()
    return genera_pasti()

def save_data():
    pd.DataFrame(st.session_state.pasti).to_csv(CONFIG["FILE_SALVATAGGIO"], index=False)

# --- 4. UI ---
def render_header():
    st.title("🥗 Menù Salute Ministeriale")
    st.info(f"📅 Stagione rilevata: **{STAGIONE_ATTUALE}** (Verdure fresche di stagione selezionate)")
    
    with st.expander("ℹ️ Grammature Standard"):
        cols = st.columns(2)
        items = list(CONFIG["PORZIONI"].items())
        mid = len(items)//2
        for i, (k, v) in enumerate(items):
            with cols[0 if i < mid else 1]: st.write(f"**{k}**: {v}")

    if st.session_state.scambio_idx is not None:
        p1 = st.session_state.pasti[st.session_state.scambio_idx]
        st.warning(f"🔄 Spostamento: **{p1['giorno']} {p1['tipo']}**. Clicca SPOSTA su un altro pasto.")
        if st.button("Annulla spostamento"):
            st.session_state.scambio_idx = None
            st.rerun()
    
    # Pulsante rimosso dal rosso (type="primary" rimosso o cambiato)
    if st.button("🔄 GENERA NUOVO MENÙ BILANCIATO", use_container_width=True):
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
        
        new_c = st.selectbox("Cereale", CONFIG["TUTTI_CARBO"], 
                             index=get_index_safe(CONFIG["TUTTI_CARBO"], pasto['carbo']),
                             key=f"c_{idx}_{st.session_state.menu_key}")
        
        # Le verdure ora mostrano quelle della stagione corretta
        new_v = st.selectbox("Verdura", OPZIONI_VERD_ATTUALI, 
                             index=get_index_safe(OPZIONI_VERD_ATTUALI, pasto['verd']),
                             key=f"v_{idx}_{st.session_state.menu_key}")
        
        if new_p != pasto['prot'] or new_c != pasto['carbo'] or new_v != pasto['verd']:
            st.session_state.pasti[idx].update({"prot": new_p, "carbo": new_c, "verd": new_v})
            save_data()

        c1, c2 = st.columns(2)
        pasto['locked'] = c1.checkbox("Blocca", value=bool(pasto['locked']), key=f"l_{idx}_{st.session_state.menu_key}")
        
        if c2.button("↔️ SPOSTA", key=f"bt_{idx}_{st.session_state.menu_key}", use_container_width=True):
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
    st.set_page_config(page_title="Menù Salute", layout="wide")
    
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

    # Statistiche con Check Visivo
    st.divider()
    st.subheader("📊 Frequenze Settimanali")
    all_prots = [p['prot'] for p in st.session_state.pasti]
    cols = st.columns(len(CONFIG["TARGET_PROTEINE"]))
    
    for i, (nome, target) in enumerate(CONFIG["TARGET_PROTEINE"].items()):
        attuale = all_prots.count(nome)
        emoji = CONFIG["EMOJI_PROT"][nome]
        
        # Logica del Check Visivo
        stato = "✅" if attuale == target else "⚠️" if attuale > target else "📉"
        
        cols[i].metric(
            label=f"{emoji} {nome}", 
            value=f"{attuale}/{target}", 
            delta=stato,
            delta_color="normal" if attuale <= target else "inverse"
        )

if __name__ == "__main__":
    main()
