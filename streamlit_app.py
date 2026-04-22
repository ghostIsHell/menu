import streamlit as st
import random
import pandas as pd
import uuid
from datetime import datetime
from st_supabase_connection import SupabaseConnection

# --- 1. CONFIGURATION & TRANSLATIONS ---
CONFIG = {
    "TABLE_NAME": "user_dinner",
    "EMOJI_PROT": {
        'Legumes': '🟢', 'Fish': '🔵', 'White Meat': '⚪', 
        'Eggs': '🟣', 'Cheese': '🟡', 'Red Meat': '🔴',
        'Pizza': '🍕', 'One-Pot Meal': '🍲'
    },
    "CARBO_LUNCH": ['Whole Grain Pasta', 'Brown Rice', 'Spelt', 'Barley', 'Gnocchi'],
    "CARBO_DINNER": ['Whole Grain Bread', 'Potatoes', 'Whole Grain Couscous'],
    "TARGET_PROT": {
        "Legumes": 3, "Fish": 3, "White Meat": 2, "Eggs": 3, 
        "Cheese": 1, "Red Meat": 1, "One-Pot Meal": 1
    },
    "VEG_SEASONAL": {
        "Winter": ['Broccoli', 'Cauliflower', 'Fennel', 'Spinach', 'Chard', 'Artichokes', 'Pumpkin'],
        "Spring": ['Asparagus', 'Peas', 'Broad Beans', 'Artichokes', 'Zucchini', 'Salad'],
        "Summer": ['Tomatoes', 'Peppers', 'Eggplants', 'Zucchini', 'Green Beans', 'Cucumbers'],
        "Autumn": ['Pumpkin', 'Mushrooms', 'Broccoli', 'Spinach', 'Fennel', 'Carrots']
    },
    "PORTIONS_GRAMS": {
        "Whole Grain Pasta": 80, "Brown Rice": 80, "Spelt": 80, "Barley": 80, "Gnocchi": 200,
        "Whole Grain Bread": 50, "Potatoes": 200, "Whole Grain Couscous": 80,
        "Legumes": 150, "Fish": 150, "White Meat": 120, "Red Meat": 100,
        "Cheese": 100, "Eggs": 2, "Vegetables": 200, "Pizza": 1
    }
}

TRANSLATIONS = {
    "IT": {
        "title": "Menù Settimanale",
        "settings": "⚙️ Impostazioni",
        "lang_label": "Lingua / Language",
        "persone": "Persone a tavola",
        "pizza_toggle": "Includi Pizza Settimanale",
        "gen_btn": "🔄 GENERA E SALVA",
        "save_btn": "💾 SALVA MODIFICHE",
        "sync_msg": "Sincronizzato!",
        "pills_title": "📚 Pillole di Educazione Alimentare",
        "pills_content": """- **La Pizza:** Equivale a una porzione abbondante di carboidrati + proteine + grassi. Consumala **1 volta a settimana**.
- **Piatti Unici:** Pasta e fagioli o insalatone sono sostituti validi. 
- **Regola d'oro:** Accompagna sempre con verdura extra per garantire fibre e sazietà.
- **Il Falso Amico:** Attenzione a birra o bibite con la pizza; sbilanciano il pasto.""",
        "guide_title": "⚖️ Grammature Consigliate",
        "guide_content": """**Porzioni standard (Adulto):**
* **Cereali:** 80g / **Pane:** 50g
* **Carne Bianca:** 120g / **Pesce:** 150g
* **Legumi:** 150g (cotti) / **Uova:** 2
* **Formaggio:** 50-100g / **Verdura:** 200g""",
        "stats_title": "📊 Frequenze Settimanali",
        "shop_title": "🛒 Lista della Spesa",
        "shop_calc": "Calcolata automaticamente per",
        "persona": "persona",
        "persone_plur": "persone",
        "days": ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"],
        "prot_label": "Proteina",
        "carb_label": "Carboidrato",
        "veg_label": "Verdura",
        "sugg_label": "ℹ️ Suggerimenti e Grammi",
        "single_label": "Singola Porzione",
        "total_label": "Totale per",
        "included": "Incluso",
        "pizza_tip": "🍕 Tip: Impasto integrale + contorno di finocchi/insalata.",
        "swap": "↔️ SCAMBIA",
        "confirm": "✅ CONFERMA",
        "cancel": "🚫 ANNULLA",
        "lock": "Blocca"
    },
    "EN": {
        "title": "Weekly Menu",
        "settings": "⚙️ Settings",
        "lang_label": "Language / Lingua",
        "persone": "People at the table",
        "pizza_toggle": "Include Weekly Pizza",
        "gen_btn": "🔄 GENERATE & SAVE",
        "save_btn": "💾 SAVE CHANGES",
        "sync_msg": "Synced!",
        "pills_title": "📚 Nutritional Pills",
        "pills_content": """- **Pizza:** Counts as a heavy portion of carbs + protein + fats. Eat it **once a week**.
- **One-Pot Meals:** Pasta & beans or big salads are great substitutes.
- **Golden Rule:** Always add extra vegetables for fiber and satiety.
- **The Fake Friend:** Watch out for beer or soda with pizza; they unbalance the meal.""",
        "guide_title": "⚖️ Recommended Portions",
        "guide_content": """**Standard Portions (Adult):**
* **Cereals:** 80g / **Bread:** 50g
* **White Meat:** 120g / **Fish:** 150g
* **Legumes:** 150g (cooked) / **Eggs:** 2
* **Cheese:** 50-100g / **Vegetables:** 200g""",
        "stats_title": "📊 Weekly Frequencies",
        "shop_title": "🛒 Shopping List",
        "shop_calc": "Automatically calculated for",
        "persona": "person",
        "persone_plur": "people",
        "days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
        "prot_label": "Protein Source",
        "carb_label": "Carbohydrate",
        "veg_label": "Vegetables",
        "sugg_label": "ℹ️ Suggestions & Grams",
        "single_label": "Single Portion",
        "total_label": "Total for",
        "included": "Included",
        "pizza_tip": "🍕 Tip: Whole dough + side of fennel/salad.",
        "swap": "↔️ SWAP",
        "confirm": "✅ CONFIRM",
        "cancel": "🚫 CANCEL",
        "lock": "Lock"
    }
}

ALL_VEG = sorted(list(set([v for sublist in CONFIG["VEG_SEASONAL"].values() for v in sublist])))
CONFIG["ALL_CARBO"] = sorted(list(set(CONFIG["CARBO_LUNCH"] + CONFIG["CARBO_DINNER"])))

# --- 2. DATABASE LOGIC ---
conn = st.connection(
    "supabase",
    type=SupabaseConnection,
    url=st.secrets["connections"]["supabase"]["url"],
    key=st.secrets["connections"]["supabase"]["key"]
)

def get_current_season():
    month = datetime.now().month
    if month in [12, 1, 2]: return "Winter"
    if month in [3, 4, 5]: return "Spring"
    if month in [6, 7, 8]: return "Summer"
    return "Autumn"

def load_menu_from_db(username):
    try:
        query = conn.query("*", table=CONFIG["TABLE_NAME"], ttl=0).eq("user_id", username).execute()
        if len(query.data) == 14:
            return sorted(query.data, key=lambda x: (x['day_idx'], x['type'] == 'Dinner'))
        return None
    except Exception: return None

def save_menu_to_db(username, meals):
    try:
        conn.table(CONFIG["TABLE_NAME"]).delete().eq("user_id", username).execute()
        insert_data = []
        for i, m in enumerate(meals):
            insert_data.append({
                "user_id": username, "day_idx": i // 2, "type": m["type"],
                "prot": m["prot"], "carbo": m["carbo"], "veg": m["veg"],
                "locked": m.get("locked", False)
            })
        conn.table(CONFIG["TABLE_NAME"]).insert(insert_data).execute()
    except Exception as e: st.error(f"Sync Error: {e}")

# --- 3. MEAL GENERATION ---
def build_protein_pool(use_pizza):
    pool = []
    targets = CONFIG["TARGET_PROT"].copy()
    if use_pizza: targets["Pizza"] = 1
    else: targets["Legumes"] += 1
    for prot, count in targets.items():
        pool.extend([prot] * count)
    random.shuffle(pool)
    return pool

def generate_new_menu(use_pizza=True):
    prot_pool = build_protein_pool(use_pizza)
    current_veg = CONFIG["VEG_SEASONAL"][get_current_season()]
    meals = []
    for i in range(14):
        m_type = "Lunch" if i % 2 == 0 else "Dinner"
        prot = prot_pool.pop()
        carbo = "Included" if prot in ['Pizza', 'One-Pot Meal'] else \
                random.choice(CONFIG["CARBO_LUNCH"] if m_type == "Lunch" else CONFIG["CARBO_DINNER"])
        meals.append({
            "type": m_type, "prot": prot, "carbo": carbo,
            "veg": random.choice(current_veg), "locked": False
        })
    return meals

# --- 4. UI COMPONENTS ---
def render_meal_card(idx, num_people, L):
    meal = st.session_state.meals[idx]
    is_swapping = (st.session_state.swap_idx == idx)
    
    with st.container(border=True):
        st.markdown(f"**{'☀️' if meal['type'] == 'Lunch' else '🌙'} {meal['type']}**")
        
        prot_options = list(CONFIG["EMOJI_PROT"].keys())
        new_p = st.selectbox(L["prot_label"], prot_options, index=prot_options.index(meal['prot']), key=f"p_{idx}_{st.session_state.sync_key}")
        
        if new_p in ['Pizza', 'One-Pot Meal']:
            new_c = "Included"
            if new_p == 'Pizza': st.warning(L["pizza_tip"])
        else:
            c_opts = CONFIG["ALL_CARBO"]
            curr_c = meal['carbo'] if meal['carbo'] in c_opts else c_opts[0]
            new_c = st.selectbox(L["carb_label"], c_opts, index=c_opts.index(curr_c), key=f"c_{idx}_{st.session_state.sync_key}")
        
        new_v = st.selectbox(L["veg_label"], ALL_VEG, index=ALL_VEG.index(meal['veg']), key=f"v_{idx}_{st.session_state.sync_key}")

        with st.expander(L["sugg_label"]):
            ref_p = CONFIG["PORTIONS_GRAMS"].get(new_p, 0)
            ref_c = CONFIG["PORTIONS_GRAMS"].get(new_c, 0) if new_c != "Included" else 0
            ref_v = CONFIG["PORTIONS_GRAMS"].get("Vegetables", 200)
            
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown(f"**{L['single_label']}:**")
                st.caption(f"- {new_p}: {ref_p}g/pz")
                if new_c != "Included": st.caption(f"- {new_c}: {ref_c}g")
                st.caption(f"- {L['veg_label']}: {ref_v}g")
            with col_b:
                st.markdown(f"**{L['total_label']} {num_people}:**")
                st.write(f"- {ref_p * num_people}g/pz")
                if new_c != "Included": st.write(f"- {ref_c * num_people}g")
                st.write(f"- {ref_v * num_people}g")

        if new_p != meal['prot'] or new_c != meal['carbo'] or new_v != meal['veg']:
            st.session_state.meals[idx].update({"prot": new_p, "carbo": new_c, "veg": new_v})

        c1, c2 = st.columns(2)
        meal['locked'] = c1.checkbox(L["lock"], value=meal['locked'], key=f"l_{idx}_{st.session_state.sync_key}")
        btn_label = L["confirm"] if (st.session_state.swap_idx is not None and not is_swapping) else L["swap"]
        
        if c2.button(btn_label, key=f"btn_{idx}_{st.session_state.sync_key}", use_container_width=True):
            if st.session_state.swap_idx is None: st.session_state.swap_idx = idx
            elif is_swapping: st.session_state.swap_idx = None
            else:
                i1, i2 = st.session_state.swap_idx, idx
                st.session_state.meals[i1], st.session_state.meals[i2] = st.session_state.meals[i2], st.session_state.meals[i1]
                st.session_state.swap_idx = None
                st.session_state.sync_key = str(uuid.uuid4())
            st.rerun()

# --- 5. MAIN APP ---
def main():
    st.set_page_config(page_title="Healthy Menu DB", layout="wide", page_icon="🥗")
    
    if 'sync_key' not in st.session_state: st.session_state.sync_key = str(uuid.uuid4())
    if 'swap_idx' not in st.session_state: st.session_state.swap_idx = None

    # --- SIDEBAR & LANGUAGE CHOICE ---
    with st.sidebar:
        lang_choice = st.radio("Language / Lingua", ["IT", "EN"], horizontal=True)
        L = TRANSLATIONS[lang_choice] # Get the current translation dictionary
        
        st.header(L["settings"])
        username = st.text_input("Username", value="guest_user")
        num_persone = st.number_input(L["persone"], 1, 10, 1)
        use_pizza = st.toggle(L["pizza_toggle"], value=True)
        
        st.divider()
        if st.button(L["gen_btn"], use_container_width=True):
            st.session_state.meals = generate_new_menu(use_pizza)
            save_menu_to_db(username, st.session_state.meals)
            st.rerun()
        
        if st.button(L["save_btn"], use_container_width=True):
            save_menu_to_db(username, st.session_state.meals)
            st.success(L["sync_msg"])

    if 'meals' not in st.session_state:
        db_data = load_menu_from_db(username)
        st.session_state.meals = db_data if db_data else generate_new_menu(use_pizza)

    st.title(f"🥗 {L['title']}: {username}")

    # --- SECTION: PILLS & GUIDELINES ---
    col_pill1, col_pill2 = st.columns(2)
    with col_pill1:
        with st.expander(L["pills_title"]):
            st.markdown(L["pills_content"])
    with col_pill2:
        with st.expander(L["guide_title"]):
            st.markdown(L["guide_content"])

    # --- 📊 STATISTICS ---
    st.subheader(L["stats_title"])
    all_prots = [m['prot'] for m in st.session_state.meals]
    cols = st.columns(len(CONFIG["EMOJI_PROT"]))
    adj_targets = CONFIG["TARGET_PROT"].copy()
    if use_pizza: adj_targets["Pizza"] = 1
    else: adj_targets["Legumes"] += 1

    for i, (name, target) in enumerate(adj_targets.items()):
        current = all_prots.count(name)
        emoji = CONFIG["EMOJI_PROT"][name]
        color, arrow, label = ("normal", "off", f"↕ Target: {target}") if current == target else \
                            ("inverse", "up", f"Target: {target}") if current > target else \
                            ("off", "down", f"Target: {target}")
        cols[i].metric(label=f"{emoji} {name}", value=f"{current}", delta=label, delta_color=color, delta_arrow=arrow)

    # --- 📅 GRID ---
    for i, day_name in enumerate(L["days"]):
        with st.expander(f"📅 {day_name.upper()}"):
            l, r = st.columns(2)
            with l: render_meal_card(i*2, num_persone, L)
            with r: render_meal_card(i*2 + 1, num_persone, L)

    # --- 🛒 SHOPPING LIST ---
    st.divider()
    pers_label = L["persona"] if num_persone == 1 else L["persone_plur"]
    st.markdown(f"""
        <div style="background-color: #f0f2f6; padding: 20px; border-radius: 10px; border-left: 5px solid #ff4b4b; margin-bottom: 20px;">
            <h2 style="margin: 0; color: #31333f;">{L['shop_title']}</h2>
            <p style="margin: 0; color: #555; font-weight: bold;">
                {L['shop_calc']} <span style="color: #ff4b4b;">{num_persone} {pers_label}</span>
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    shop_list = {}
    for m in st.session_state.meals:
        for item in [m['prot'], m['carbo'], m['veg']]:
            if item == "Included": continue
            key = "Vegetables" if item in ALL_VEG else item
            qty = CONFIG["PORTIONS_GRAMS"].get(key, 0) * num_persone
            shop_list[key] = shop_list.get(key, 0) + qty

    s_col1, s_col2 = st.columns(2)
    items = list(shop_list.items())
    half = (len(items) + 1) // 2
    for i, (name, total) in enumerate(items):
        target_col = s_col1 if i < half else s_col2
        unit = "pz" if name in ["Eggs", "Pizza"] else "g"
        display_total = f"{total/1000:.2f} Kg" if (unit == "g" and total >= 1000) else f"{total} {unit}"
        target_col.write(f"- **{name}**: {display_total}")

if __name__ == "__main__":
    main()
