import streamlit as st
import random
import pandas as pd
import uuid
from datetime import datetime
from st_supabase_connection import SupabaseConnection

# --- 1. DIZIONARIO DATI E TRADUZIONI (TUTTO BILINGUE) ---
DATA = {
    "PROT": {
        "Legumes": {"IT": "🟢 Legumi", "EN": "🟢 Legumes", "gr": 150, "unit": "g"},
        "Fish": {"IT": "🔵 Pesce", "EN": "🔵 Fish", "gr": 150, "unit": "g"},
        "White Meat": {"IT": "⚪ Carne Bianca", "EN": "⚪ White Meat", "gr": 120, "unit": "g"},
        "Eggs": {"IT": "🟣 Uova", "EN": "🟣 Eggs", "gr": 2, "unit": "pz"},
        "Cheese": {"IT": "🟡 Formaggio", "EN": "🟡 Cheese", "gr": 100, "unit": "g"},
        "Red Meat": {"IT": "🔴 Carne Rossa", "EN": "🔴 Red Meat", "gr": 100, "unit": "g"},
        "Pizza": {"IT": "🍕 Pizza", "EN": "🍕 Pizza", "gr": 1, "unit": "pz"},
        "One-Pot Meal": {"IT": "🍲 Piatto Unico", "EN": "🍲 One-Pot Meal", "gr": 150, "unit": "g"}
    },
    "CARBO": {
        "Whole Grain Pasta": {"IT": "Pasta Integrale", "EN": "Whole Grain Pasta", "gr": 80},
        "Brown Rice": {"IT": "Riso Integrale", "EN": "Brown Rice", "gr": 80},
        "Spelt": {"IT": "Farro", "EN": "Spelt", "gr": 80},
        "Barley": {"IT": "Orzo", "EN": "Barley", "gr": 80},
        "Gnocchi": {"IT": "Gnocchi", "EN": "Gnocchi", "gr": 200},
        "Whole Grain Bread": {"IT": "Pane Integrale", "EN": "Whole Grain Bread", "gr": 50},
        "Potatoes": {"IT": "Patate", "EN": "Potatoes", "gr": 200},
        "Whole Grain Couscous": {"IT": "Couscous Integrale", "EN": "Whole Grain Couscous", "gr": 80},
        "Included": {"IT": "Incluso nel piatto", "EN": "Included in meal", "gr": 0}
    },
    "VEG": {
        "Broccoli": {"IT": "Broccoli", "EN": "Broccoli"},
        "Cauliflower": {"IT": "Cavolfiore", "EN": "Cauliflower"},
        "Fennel": {"IT": "Finocchi", "EN": "Fennel"},
        "Spinach": {"IT": "Spinaci", "EN": "Spinach"},
        "Chard": {"IT": "Bietole", "EN": "Chard"},
        "Artichokes": {"IT": "Carciofi", "EN": "Artichokes"},
        "Pumpkin": {"IT": "Zucca", "EN": "Pumpkin"},
        "Asparagus": {"IT": "Asparagi", "EN": "Asparagus"},
        "Peas": {"IT": "Piselli", "EN": "Peas"},
        "Broad Beans": {"IT": "Fave", "EN": "Broad Beans"},
        "Zucchini": {"IT": "Zucchine", "EN": "Zucchini"},
        "Salad": {"IT": "Insalata", "EN": "Salad"},
        "Tomatoes": {"IT": "Pomodori", "EN": "Tomatoes"},
        "Peppers": {"IT": "Peperoni", "EN": "Peperoni"},
        "Eggplants": {"IT": "Melanzane", "EN": "Eggplants"},
        "Green Beans": {"IT": "Fagiolini", "EN": "Green Beans"},
        "Cucumbers": {"IT": "Cetrioli", "EN": "Cucumbers"},
        "Mushrooms": {"IT": "Funghi", "EN": "Mushrooms"},
        "Carrots": {"IT": "Carote", "EN": "Carrots"}
    }
}

UI_TEXT = {
    "IT": {
        "title": "Menù Settimanale", "settings": "⚙️ Impostazioni", "user": "Nome Utente",
        "people": "Persone a tavola", "pizza_toggle": "Includi Pizza Settimanale",
        "gen_btn": "🔄 GENERA E SALVA", "save_btn": "💾 SALVA MODIFICHE", "sync": "Sincronizzato!",
        "pills_title": "📚 Pillole di Educazione Alimentare",
        "pills_txt": "- **Pizza:** 1 volta a settimana.\n- **Piatto Unico:** Pasta e fagioli, insalatone.\n- **Regola:** Sempre con verdura extra.\n- **Falso Amico:** Attenzione a bibite e dolci.",
        "guide_title": "⚖️ Grammature Consigliate",
        "guide_txt": "* **Cereali:** 80g\n* **Pane:** 50g\n* **Carne Bianca:** 120g\n* **Pesce:** 150g\n* **Verdura:** 200g",
        "freq_title": "📊 Frequenze Settimanali", "shop_title": "🛒 Lista della Spesa",
        "shop_calc": "Calcolata per", "days": ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"],
        "lunch": "Pranzo", "dinner": "Cena", "prot": "Proteina", "carb": "Carboidrato", "veg": "Verdura",
        "sugg": "ℹ️ Suggerimenti e Grammi", "single": "Singola Porzione", "total": "Totale per",
        "swap": "↔️ SCAMBIA", "confirm": "✅ CONFERMA", "lock": "Blocca", "kg_label": "Kg", "unit_pz": "pz", "unit_g": "g"
    },
    "EN": {
        "title": "Weekly Menu", "settings": "⚙️ Settings", "user": "Username",
        "people": "People at table", "pizza_toggle": "Include Weekly Pizza",
        "gen_btn": "🔄 GENERATE & SAVE", "save_btn": "💾 SAVE CHANGES", "sync": "Synced!",
        "pills_title": "📚 Nutritional Pills",
        "pills_txt": "- **Pizza:** Once a week.\n- **One-Pot Meal:** Pasta & beans, big salads.\n- **Rule:** Always add extra vegetables.\n- **Fake Friend:** Watch out for sodas and sweets.",
        "guide_title": "⚖️ Portion Guidelines",
        "guide_txt": "* **Cereals:** 80g\n* **Bread:** 50g\n* **White Meat:** 120g\n* **Fish:** 150g\n* **Vegetables:** 200g",
        "freq_title": "📊 Weekly Frequencies", "shop_title": "🛒 Shopping List",
        "shop_calc": "Calculated for", "days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
        "lunch": "Lunch", "dinner": "Dinner", "prot": "Protein", "carb": "Carbohydrate", "veg": "Vegetables",
        "sugg": "ℹ️ Suggestions & Grams", "single": "Single Portion", "total": "Total for",
        "swap": "↔️ SWAP", "confirm": "✅ CONFIRM", "lock": "Lock", "kg_label": "Kg", "unit_pz": "pcs", "unit_g": "g"
    }
}

# --- 2. DATABASE HELPERS ---
conn = st.connection("supabase", type=SupabaseConnection, 
                    url=st.secrets["connections"]["supabase"]["url"], 
                    key=st.secrets["connections"]["supabase"]["key"])

def load_db(user):
    res = conn.query("*", table="user_dinner", ttl=0).eq("user_id", user).execute()
    return sorted(res.data, key=lambda x: (x['day_idx'], x['type'] == 'Dinner')) if len(res.data) == 14 else None

def save_db(user, meals):
    conn.table("user_dinner").delete().eq("user_id", user).execute()
    data_to_save = []
    for i, m in enumerate(meals):
        data_to_save.append({
            "user_id": user, "day_idx": i // 2, "type": m["type"],
            "prot": m["prot"], "carbo": m["carbo"], "veg": m["veg"], "locked": m["locked"]
        })
    conn.table("user_dinner").insert(data_to_save).execute()

# --- 3. GENERATION LOGIC ---
def generate_new_menu(pizza_on):
    pool = []
    targets = {"Legumes": 3 if pizza_on else 4, "Fish": 3, "White Meat": 2, "Eggs": 3, "Cheese": 1, "Red Meat": 1, "One-Pot Meal": 1, "Pizza": 1 if pizza_on else 0}
    for k, v in targets.items(): pool.extend([k] * v)
    random.shuffle(pool)
    
    meals = []
    all_veg = list(DATA["VEG"].keys())
    for i in range(14):
        p = pool.pop()
        is_lunch = (i % 2 == 0)
        if p in ["Pizza", "One-Pot Meal"]:
            c = "Included"
        else:
            c = random.choice(["Whole Grain Pasta", "Brown Rice", "Spelt", "Barley", "Gnocchi"] if is_lunch else ["Whole Grain Bread", "Potatoes", "Whole Grain Couscous"])
        meals.append({"type": "Lunch" if is_lunch else "Dinner", "prot": p, "carbo": c, "veg": random.choice(all_veg), "locked": False})
    return meals

# --- 4. MAIN APP ---
def main():
    st.set_page_config(page_title="HealthMenu AI", layout="wide")

    # --- SIDEBAR & LANGUAGE ---
    with st.sidebar:
        lang = st.radio("Language / Lingua", ["IT", "EN"], horizontal=True)
        T = UI_TEXT[lang]
        st.header(T["settings"])
        user = st.text_input(T["user"], value="guest")
        num_persone = st.number_input(T["people"], 1, 10, 1)
        pizza_on = st.toggle(T["pizza_toggle"], value=True)
        
        st.divider()
        if st.button(T["gen_btn"], use_container_width=True):
            st.session_state.meals = generate_new_menu(pizza_on)
            save_db(user, st.session_state.meals)
            st.rerun()
        if st.button(T["save_btn"], use_container_width=True):
            save_db(user, st.session_state.meals)
            st.success(T["sync"])

    # Load initial state
    if "meals" not in st.session_state:
        db_data = load_db(user)
        st.session_state.meals = db_data if db_data else generate_new_menu(pizza_on)
        st.session_state.swap_idx = None
    
    st.title(f"{T['title']} - {user}")

    # --- INFO SECTIONS ---
    col1, col2 = st.columns(2)
    with col1:
        with st.expander(T["pills_title"]): st.markdown(T["pills_txt"])
    with col2:
        with st.expander(T["guide_title"]): st.markdown(T["guide_txt"])

    # --- FREQUENCIES ---
    st.subheader(T["freq_title"])
    all_p_ids = [m["prot"] for m in st.session_state.meals]
    cols = st.columns(len(DATA["PROT"]))
    for i, (p_id, p_info) in enumerate(DATA["PROT"].items()):
        cols[i].metric(label=p_info[lang], value=all_p_ids.count(p_id))

    # --- GRID ---
    for i, day_label in enumerate(T["days"]):
        with st.expander(f"📅 {day_label.upper()}"):
            m_cols = st.columns(2)
            for j in range(2):
                idx = i*2 + j
                m = st.session_state.meals[idx]
                is_swapping = (st.session_state.swap_idx == idx)
                
                with m_cols[j].container(border=True):
                    st.markdown(f"**{T['lunch' if j==0 else 'dinner']}**")
                    
                    # Selezione Proteina
                    p_opts = list(DATA["PROT"].keys())
                    new_p = st.selectbox(T["prot"], p_opts, index=p_opts.index(m["prot"]), format_func=lambda x: DATA["PROT"][x][lang], key=f"p{idx}")
                    
                    # Selezione Carbo
                    if new_p in ["Pizza", "One-Pot Meal"]:
                        new_c = "Included"
                        st.caption(f"✨ {DATA['CARBO']['Included'][lang]}")
                    else:
                        c_opts = [k for k in DATA["CARBO"].keys() if k != "Included"]
                        current_c_idx = c_opts.index(m["carbo"]) if m["carbo"] in c_opts else 0
                        new_c = st.selectbox(T["carb"], c_opts, index=current_c_idx, format_func=lambda x: DATA["CARBO"][x][lang], key=f"c{idx}")
                    
                    # Selezione Verdura
                    v_opts = list(DATA["VEG"].keys())
                    new_v = st.selectbox(T["veg"], v_opts, index=v_opts.index(m["veg"]), format_func=lambda x: DATA["VEG"][x][lang], key=f"v{idx}")
                    
                    st.session_state.meals[idx].update({"prot": new_p, "carbo": new_c, "veg": new_v})

                    # Suggerimenti Grammature
                    with st.expander(T["sugg"]):
                        g_p = DATA["PROT"][new_p]["gr"]
                        u_p = T["unit_pz"] if DATA["PROT"][new_p]["unit"] == "pz" else T["unit_g"]
                        g_c = DATA["CARBO"][new_c]["gr"]
                        
                        st.write(f"**{T['total']} {num_persone}:**")
                        st.write(f"- {DATA['PROT'][new_p][lang]}: {g_p * num_persone} {u_p}")
                        if g_c > 0: st.write(f"- {DATA['CARBO'][new_c][lang]}: {g_c * num_persone} {T['unit_g']}")
                        st.write(f"- {DATA['VEG'][new_v][lang]}: {200 * num_persone} {T['unit_g']}")

                    # Bottoni
                    b_cols = st.columns(2)
                    m["locked"] = b_cols[0].checkbox(T["lock"], value=m["locked"], key=f"lk{idx}")
                    btn_txt = T["confirm"] if (st.session_state.swap_idx is not None and not is_swapping) else T["swap"]
                    if b_cols[1].button(btn_txt, key=f"sw{idx}", use_container_width=True):
                        if st.session_state.swap_idx is None:
                            st.session_state.swap_idx = idx
                            st.rerun()
                        else:
                            st.session_state.meals[idx], st.session_state.meals[st.session_state.swap_idx] = st.session_state.meals[st.session_state.swap_idx], st.session_state.meals[idx]
                            st.session_state.swap_idx = None
                            st.rerun()

    # --- SHOPPING LIST ---
    st.divider()
    st.markdown(f"""
        <div style="background-color: #f0f2f6; padding: 20px; border-radius: 10px; border-left: 5px solid #ff4b4b;">
            <h2 style="margin: 0;">{T['shop_title']}</h2>
            <p style="margin: 0; font-weight: bold;">{T['shop_calc']} <span style="color: #ff4b4b;">{num_persone}</span> {lang}</p>
        </div>
    """, unsafe_allow_html=True)
    
    basket = {}
    for m in st.session_state.meals:
        # Prot
        p_id = m["prot"]
        p_name = DATA["PROT"][p_id][lang]
        p_qty = DATA["PROT"][p_id]["gr"] * num_persone
        p_unit = DATA["PROT"][p_id]["unit"]
        basket[p_name] = basket.get(p_name, {"qty": 0, "unit": p_unit})
        basket[p_name]["qty"] += p_qty
        
        # Carbo
        c_id = m["carbo"]
        if c_id != "Included":
            c_name = DATA["CARBO"][c_id][lang]
            c_qty = DATA["CARBO"][c_id]["gr"] * num_persone
            basket[c_name] = basket.get(c_name, {"qty": 0, "unit": "g"})
            basket[c_name]["qty"] += c_qty
        
        # Veg
        v_name = DATA["VEG"][m["veg"]][lang]
        v_qty = 200 * num_persone
        basket[v_name] = basket.get(v_name, {"qty": 0, "unit": "g"})
        basket[v_name]["qty"] += v_qty

    s_cols = st.columns(2)
    items = list(basket.items())
    for i, (name, info) in enumerate(items):
        target_col = s_cols[0] if i < len(items)/2 else s_cols[1]
        qty = info["qty"]
        unit = T["unit_pz"] if info["unit"] == "pz" else T["unit_g"]
        
        if info["unit"] == "g" and qty >= 1000:
            val_str = f"{qty/1000:.2f} {T['kg_label']}"
        else:
            val_str = f"{qty} {unit}"
        
        target_col.write(f"- **{name}**: {val_str}")

if __name__ == "__main__":
    main()
