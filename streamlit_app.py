import streamlit as st
import random
import pandas as pd
import uuid
from datetime import datetime
from st_supabase_connection import SupabaseConnection

# --- 1. CONFIGURAZIONE E TRADUZIONI ---
DATA = {
    "PROT": {
        "Legumes": {"IT": "🟢 Legumi", "EN": "🟢 Legumes", "gr": 150, "unit": "g", "target": 3},
        "Fish": {"IT": "🔵 Pesce", "EN": "🔵 Fish", "gr": 150, "unit": "g", "target": 3},
        "White Meat": {"IT": "⚪ Carne Bianca", "EN": "⚪ White Meat", "gr": 120, "unit": "g", "target": 2},
        "Eggs": {"IT": "🟣 Uova", "EN": "🟣 Eggs", "gr": 2, "unit": "pz", "target": 3},
        "Cheese": {"IT": "🟡 Formaggio", "EN": "🟡 Cheese", "gr": 100, "unit": "g", "target": 1},
        "Red Meat": {"IT": "🔴 Carne Rossa", "EN": "🔴 Red Meat", "gr": 100, "unit": "g", "target": 1},
        "Pizza": {"IT": "🍕 Pizza", "EN": "🍕 Pizza", "gr": 1, "unit": "pz", "target": 1},
        "One-Pot Meal": {"IT": "🍲 Piatto Unico", "EN": "🍲 One-Pot Meal", "gr": 150, "unit": "g", "target": 1}
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
        "Included": {"IT": "Incluso / Included", "EN": "Included", "gr": 0}
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
        "Peppers": {"IT": "Peperoni", "EN": "Peppers"},
        "Eggplants": {"IT": "Melanzane", "EN": "Eggplants"},
        "Green Beans": {"IT": "Fagiolini", "EN": "Green Beans"},
        "Cucumbers": {"IT": "Cetrioli", "EN": "Cucumbers"},
        "Mushrooms": {"IT": "Funghi", "EN": "Mushrooms"},
        "Carrots": {"IT": "Carote", "EN": "Carrots"}
    }
}

UI_TEXT = {
    "IT": {
        "title": "Menù Settimanale", "settings": "⚙️ Impostazioni", "people": "Persone a tavola",
        "pizza_toggle": "Includi Pizza Settimanale", "gen": "🔄 GENERA E SALVA", "save": "💾 SALVA MODIFICHE",
        "sync": "Sincronizzato!", "pills": "📚 Pillole di Educazione Alimentare",
        "pills_txt": "- **Pizza:** 1 volta a settimana.\n- **Piatto Unico:** Pasta e fagioli, insalatone.\n- **Regola:** Sempre con verdura extra.",
        "guide": "⚖️ Grammature Consigliate",
        "guide_txt": "* **Cereali:** 80g\n* **Carne:** 120g\n* **Pesce:** 150g\n* **Verdura:** 200g",
        "freq": "📊 Frequenze Settimanali", "shop": "🛒 Lista della Spesa",
        "shop_calc": "Calcolata per", "days": ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"],
        "lunch": "Pranzo", "dinner": "Cena", "prot": "Proteina", "carb": "Carboidrato", "veg": "Verdura",
        "sugg": "ℹ️ Suggerimenti e Grammi", "single": "Porzione Singola", "total": "Totale per",
        "swap": "↔️ SCAMBIA", "confirm": "✅ CONFERMA", "lock": "Blocca", "pizza_tip": "🍕 Tip: Impasto integrale + contorno di finocchi/insalata.",
        "target_label": "Target"
    },
    "EN": {
        "title": "Weekly Menu", "settings": "⚙️ Settings", "people": "People at the table",
        "pizza_toggle": "Include Weekly Pizza", "gen": "🔄 GENERATE & SAVE", "save": "💾 SAVE CHANGES",
        "sync": "Synced!", "pills": "📚 Nutritional Pills",
        "pills_txt": "- **Pizza:** Once a week.\n- **One-Pot Meal:** Pasta & beans, big salads.\n- **Rule:** Always add extra vegetables.",
        "guide": "⚖️ Portion Guidelines",
        "guide_txt": "* **Cereals:** 80g\n* **Meat:** 120g\n* **Fish:** 150g\n* **Vegetables:** 200g",
        "freq": "📊 Weekly Frequencies", "shop": "🛒 Shopping List",
        "shop_calc": "Calculated for", "days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
        "lunch": "Lunch", "dinner": "Dinner", "prot": "Protein", "carb": "Carbohydrate", "veg": "Vegetables",
        "sugg": "ℹ️ Suggestions & Grams", "single": "Single Portion", "total": "Total for",
        "swap": "↔️ SWAP", "confirm": "✅ CONFIRM", "lock": "Lock", "pizza_tip": "🍕 Tip: Whole dough + side of fennel/salad.",
        "target_label": "Target"
    }
}

# --- 2. DATABASE ---
conn = st.connection("supabase", type=SupabaseConnection, 
                    url=st.secrets["connections"]["supabase"]["url"], 
                    key=st.secrets["connections"]["supabase"]["key"])

def load_db(user):
    res = conn.query("*", table="user_dinner", ttl=0).eq("user_id", user).execute()
    return sorted(res.data, key=lambda x: (x['day_idx'], x['type'] == 'Dinner')) if len(res.data) == 14 else None

def save_db(user, meals):
    conn.table("user_dinner").delete().eq("user_id", user).execute()
    conn.table("user_dinner").insert([{"user_id": user, "day_idx": i//2, "type": m["type"], "prot": m["prot"], "carbo": m["carbo"], "veg": m["veg"], "locked": m["locked"]} for i, m in enumerate(meals)]).execute()

# --- 3. LOGICA GENERAZIONE ---
def generate_menu(pizza_on, current_meals=None):
    pool = []
    targets = {k: v["target"] for k, v in DATA["PROT"].items()}
    if not pizza_on:
        targets["Pizza"] = 0
        targets["Legumes"] += 1
        
    if current_meals:
        for m in current_meals:
            if m.get("locked"):
                p_type = m["prot"]
                if p_type in targets and targets[p_type] > 0:
                    targets[p_type] -= 1
    
    for k, v in targets.items(): pool.extend([k] * v)    
    random.shuffle(pool)
    
    meals = []
    veg_keys = list(DATA["VEG"].keys())
    for i in range(14):
        if current_meals and current_meals[i].get("locked"):
            meals.append(current_meals[i])
        else:
            p = pool.pop()
            is_lunch = i % 2 == 0
            if p in ["Pizza", "One-Pot Meal"]: c = "Included"
            else: c = random.choice(["Whole Grain Pasta", "Brown Rice", "Spelt", "Barley", "Gnocchi"] if is_lunch else ["Whole Grain Bread", "Potatoes", "Whole Grain Couscous"])
            meals.append({"type": "Lunch" if is_lunch else "Dinner", "prot": p, "carbo": c, "veg": random.choice(veg_keys), "locked": False})
    return meals

# --- 4. APP ---
def main():
    st.set_page_config(page_title="HealthMenu DB", layout="wide")
    
    with st.sidebar:
        lang = st.radio("Language / Lingua", ["IT", "EN"], horizontal=True)
        T = UI_TEXT[lang]
        st.header(T["settings"])
        user = st.text_input("User", "guest")
        n_p = st.number_input(T["people"], 1, 10, 1)
        piz = st.toggle(T["pizza_toggle"], True)
        if st.button(T["gen"], use_container_width=True):
            current = st.session_state.get("meals")
            st.session_state.meals = generate_menu(piz, current)
            save_db(user, st.session_state.meals)
            st.session_state.swap_idx = None
            st.rerun()
        if st.button(T["save"], use_container_width=True):
            save_db(user, st.session_state.meals)
            st.success(T["sync"])

    if "meals" not in st.session_state:
        db = load_db(user)
        st.session_state.meals = db if db else generate_menu(piz)
        st.session_state.swap_idx = None

    st.title(f"{T['title']} - {user}")

    # Pills & Guidelines
    c1, c2 = st.columns(2)
    c1.expander(T["pills"]).markdown(T["pills_txt"])
    c2.expander(T["guide"]).markdown(T["guide_txt"])

    # --- FREQUENZE (TARGETS) ---
    st.subheader(T["freq"])
    all_p = [m["prot"] for m in st.session_state.meals]
    cols = st.columns(len(DATA["PROT"]))
    for i, (k, v) in enumerate(DATA["PROT"].items()):
        current = all_p.count(k)
        target = v["target"] if (k != "Pizza" or piz) else 0
        if not piz and k == "Legumes": target = 4
        
        # Logica Colore Target
        color = "normal" if current == target else "inverse" if current > target else "off"
        arrow = "off" if current == target else "up" if current > target else "down"
        
        cols[i].metric(label=v[lang], value=current, delta=f"{T['target_label']}: {target}", delta_color=color, delta_arrow=arrow)

    # --- GRID ---
    for i, day_name in enumerate(T["days"]):
        with st.expander(f"📅 {day_name.upper()}"):
            cols = st.columns(2)
            for j in range(2):
                idx = i*2 + j
                m = st.session_state.meals[idx]
                with cols[j].container(border=True):
                    st.write(f"**{T['lunch' if j==0 else 'dinner']}**")
                    new_p = st.selectbox(T["prot"], list(DATA["PROT"].keys()), index=list(DATA["PROT"].keys()).index(m["prot"]), format_func=lambda x: DATA["PROT"][x][lang], key=f"p{idx}")
                    
                    if new_p in ["Pizza", "One-Pot Meal"]:
                        new_c = "Included"
                        if new_p == "Pizza": st.warning(T["pizza_tip"])
                    else:
                        c_opts = [ck for ck in DATA["CARBO"].keys() if ck != "Included"]
                        new_c = st.selectbox(T["carb"], c_opts, index=c_opts.index(m["carbo"]) if m["carbo"] in c_opts else 0, format_func=lambda x: DATA["CARBO"][x][lang], key=f"c{idx}")
                    
                    new_v = st.selectbox(T["veg"], list(DATA["VEG"].keys()), index=list(DATA["VEG"].keys()).index(m["veg"]), format_func=lambda x: DATA["VEG"][x][lang], key=f"v{idx}")
                    st.session_state.meals[idx].update({"prot": new_p, "carbo": new_c, "veg": new_v})

                    # Grammi dinamici
                    with st.expander(T["sugg"]):
                        g_p, g_c = DATA["PROT"][new_p]["gr"], DATA["CARBO"][new_c]["gr"]
                        u_p = "pz" if DATA["PROT"][new_p]["unit"] == "pz" else "g"
                        st.write(f"**{T['total']} {n_p}:**")
                        st.write(f"- {DATA['PROT'][new_p][lang]}: {g_p * n_p} {u_p}")
                        if g_c > 0: st.write(f"- {DATA['CARBO'][new_c][lang]}: {g_c * n_p} g")
                        st.write(f"- {T['veg']}: {200 * n_p} g")

                    # Swap & Lock
                    sl1, sl2 = st.columns(2)
                    m["locked"] = sl1.checkbox(T["lock"], m["locked"], key=f"lk{idx}")
                    if sl2.button(T["swap"], key=f"sw{idx}", use_container_width=True):
                        if st.session_state.swap_idx is None: st.session_state.swap_idx = idx
                        else:
                            st.session_state.meals[idx], st.session_state.meals[st.session_state.swap_idx] = st.session_state.meals[st.session_state.swap_idx], st.session_state.meals[idx]
                            st.session_state.swap_idx = None
                            st.rerun()

    # --- SHOPPING LIST STILIZZATA ---
    st.divider()
    st.markdown(f"""<div style="background:#f0f2f6;padding:20px;border-radius:10px;border-left:5px solid #ff4b4b">
        <h3>{T['shop']}</h3><p>{T['shop_calc']} <b>{n_p}</b> {'persona/person' if n_p==1 else 'persone/people'}</p></div>""", unsafe_allow_html=True)
    
    basket = {}
    for m in st.session_state.meals:
        # Prot
        p_info = DATA["PROT"][m["prot"]]
        basket[p_info[lang]] = basket.get(p_info[lang], {"q": 0, "u": p_info["unit"]})
        basket[p_info[lang]]["q"] += p_info["gr"] * n_p
        # Carbo
        if m["carbo"] != "Included":
            c_info = DATA["CARBO"][m["carbo"]]
            basket[c_info[lang]] = basket.get(c_info[lang], {"q": 0, "u": "g"})
            basket[c_info[lang]]["q"] += c_info["gr"] * n_p
        # Veg
        v_name = DATA["VEG"][m["veg"]][lang]
        basket[v_name] = basket.get(v_name, {"q": 0, "u": "g"})
        basket[v_name]["q"] += 200 * n_p

    c1, c2 = st.columns(2)
    items = list(basket.items())
    for i, (name, info) in enumerate(items):
        col = c1 if i < len(items)/2 else c2
        q, u = info["q"], info["u"]
        val = f"{q/1000:.2f} Kg" if (u=="g" and q>=1000) else f"{q} {u}"
        col.write(f"- **{name}**: {val}")

if __name__ == "__main__": main()
