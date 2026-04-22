import streamlit as st
import random
import pandas as pd
import uuid
from datetime import datetime
from st_supabase_connection import SupabaseConnection

# --- 1. CONFIGURATION ---
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
    },
    "ONE_POT_EXAMPLES": [
        "Pasta and Beans", "Rice and Peas", "Tuna Salad (Tuna+Bread+Veg)", 
        "Chicken Couscous", "Whole Grain Chicken Sandwich", 
        "Baked Omelet with Potatoes", "Ricotta & Spinach Savory Pie"
    ]
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
def render_meal_card(idx, num_people):
    meal = st.session_state.meals[idx]
    is_swapping = (st.session_state.swap_idx == idx)
    
    with st.container(border=True):
        st.markdown(f"**{'☀️' if meal['type'] == 'Lunch' else '🌙'} {meal['type']}**")
        
        # Selectors
        prot_options = list(CONFIG["EMOJI_PROT"].keys())
        new_p = st.selectbox("Protein Source", prot_options, index=prot_options.index(meal['prot']), key=f"p_{idx}_{st.session_state.sync_key}")
        
        if new_p in ['Pizza', 'One-Pot Meal']:
            new_c = "Included"
            if new_p == 'Pizza': st.warning("🍕 Tip: Whole dough + side of fennel/salad.")
            else: st.info(f"🍲 Example: {CONFIG['ONE_POT_EXAMPLES'][idx % len(CONFIG['ONE_POT_EXAMPLES'])]}")
        else:
            c_opts = CONFIG["ALL_CARBO"]
            curr_c = meal['carbo'] if meal['carbo'] in c_opts else c_opts[0]
            new_c = st.selectbox("Carb", c_opts, index=c_opts.index(curr_c), key=f"c_{idx}_{st.session_state.sync_key}")
        
        new_v = st.selectbox("Vegetables", ALL_VEG, index=ALL_VEG.index(meal['veg']), key=f"v_{idx}_{st.session_state.sync_key}")

        # SUGGESTIONS BOX
        with st.expander("ℹ️ Suggestions & Recommended Grams"):
            ref_p = CONFIG["PORTIONS_GRAMS"].get(new_p, 0)
            ref_c = CONFIG["PORTIONS_GRAMS"].get(new_c, 0) if new_c != "Included" else 0
            ref_v = CONFIG["PORTIONS_GRAMS"].get("Vegetables", 200)
            
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown("**Singola Porzione:**")
                st.caption(f"- Proteina: {ref_p}g/pz")
                if new_c != "Included": st.caption(f"- Carboidrato: {ref_c}g")
                st.caption(f"- Verdura: {ref_v}g")
            with col_b:
                st.markdown(f"**Per {num_people} {'Persona' if num_people == 1 else 'Persone'}:**")
                st.write(f"- {ref_p * num_people}g/pz")
                if new_c != "Included": st.write(f"- {ref_c * num_people}g")
                st.write(f"- {ref_v * num_people}g")

        if new_p != meal['prot'] or new_c != meal['carbo'] or new_v != meal['veg']:
            st.session_state.meals[idx].update({"prot": new_p, "carbo": new_c, "veg": new_v})

        # Actions
        c1, c2 = st.columns(2)
        meal['locked'] = c1.checkbox("Lock", value=meal['locked'], key=f"l_{idx}_{st.session_state.sync_key}")
        btn_label = "✅ CONFIRM" if (st.session_state.swap_idx is not None and not is_swapping) else "↔️ SWAP"
        
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

    with st.sidebar:
        st.header("⚙️ Impostazioni")
        username = st.text_input("Username", value="guest_user")
        num_persone_sidebar = st.number_input("Persone a tavola", 1, 10, 1)
        use_pizza = st.toggle("Includi Pizza Settimanale", value=True)
        
        st.divider()
        if st.button("🔄 GENERA E SALVA", use_container_width=True):
            st.session_state.meals = generate_new_menu(use_pizza)
            save_menu_to_db(username, st.session_state.meals)
            st.rerun()
        
        if st.button("💾 SALVA MODIFICHE", use_container_width=True):
            save_menu_to_db(username, st.session_state.meals)
            st.success("Sincronizzato!")

    # Load data
    if 'meals' not in st.session_state:
        db_data = load_menu_from_db(username)
        st.session_state.meals = db_data if db_data else generate_new_menu(use_pizza)

    st.title(f"🥗 Menù Settimanale: {username}")

    # --- SECTION: PILLS & GUIDELINES ---
    col_pill1, col_pill2 = st.columns(2)
    
    with col_pill1:
        with st.expander("📚 Pillole di Educazione Alimentare"):
            st.markdown("""
            - **La Pizza:** Equivale a una porzione abbondante di carboidrati + proteine + grassi. Consumala **1 volta a settimana**.
            - **Piatti Unici:** Pasta e fagioli o insalatone sono sostituti validi. 
            - **Regola d'oro:** Accompagna sempre con verdura extra per garantire fibre e sazietà.
            - **Il Falso Amico:** Attenzione a birra o bibite con la pizza; sbilanciano il pasto.
            """)
            
    with col_pill2:
        with st.expander("⚖️ Grammature Consigliate (Linee Guida)"):
            st.markdown("""
            **Porzioni standard per un adulto sano:**
            * **Pasta/Riso/Cereali:** 80g
            * **Pane:** 50g
            * **Carne Bianca:** 100-120g
            * **Pesce:** 150g
            * **Legumi secchi:** 50g (o 150g cotti)
            * **Uova:** 2 unità
            * **Formaggio:** 50-100g (a seconda della stagionatura)
            * **Verdura:** almeno 200g
            """)

    # --- 📊 FREQUENZE SETTIMANALI ---
    st.subheader("📊 Frequenze Settimanali")
    all_prots = [m['prot'] for m in st.session_state.meals]
    cols = st.columns(len(CONFIG["EMOJI_PROT"]))
    
    adj_targets = CONFIG["TARGET_PROT"].copy()
    if use_pizza: adj_targets["Pizza"] = 1
    else: adj_targets["Legumes"] += 1

    for i, (name, target) in enumerate(adj_targets.items()):
        current = all_prots.count(name)
        emoji = CONFIG["EMOJI_PROT"][name]
        
        if current == target:
            color, arrow, label = "normal", "off", f"↕ Target: {target}"
        elif current > target: 
            color, arrow, label = "inverse", "up", f"Target: {target}"
        else: 
            color, arrow, label = "off", "down", f"Target: {target}"
        
        cols[i].metric(label=f"{emoji} {name}", value=f"{current}", delta=label, delta_color=color, delta_arrow=arrow)

    # --- 📅 GRID RENDERING ---
    days = ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"]
    for i, day in enumerate(days):
        with st.expander(f"📅 {day.upper()}"):
            l, r = st.columns(2)
            with l: render_meal_card(i*2, num_persone_sidebar)
            with r: render_meal_card(i*2 + 1, num_persone_sidebar)

    # --- 🛒 SHOPPING LIST ---
    st.divider()
    
    # Intestazione Stilizzata
    st.markdown(f"""
        <div style="background-color: #f0f2f6; padding: 20px; border-radius: 10px; border-left: 5px solid #ff4b4b; margin-bottom: 20px;">
            <h2 style="margin: 0; color: #31333f;">🛒 Lista della Spesa</h2>
            <p style="margin: 0; color: #555; font-weight: bold;">
                Calcolata automaticamente per <span style="color: #ff4b4b;">{num_persone_sidebar} {'persona' if num_persone_sidebar == 1 else 'persone'}</span>
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    shop_list = {}
    for m in st.session_state.meals:
        for item in [m['prot'], m['carbo'], m['veg']]:
            if item == "Included": continue
            key = "Vegetables" if item in ALL_VEG else item
            qty = CONFIG["PORTIONS_GRAMS"].get(key, 0) * num_persone_sidebar
            shop_list[key] = shop_list.get(key, 0) + qty

    s_col1, s_col2 = st.columns(2)
    items = list(shop_list.items())
    half = (len(items) + 1) // 2
    
    for i, (name, total) in enumerate(items):
        target_col = s_col1 if i < half else s_col2
        unit = "pz" if name in ["Eggs", "Pizza"] else "g"
        # Mostriamo il totale in Kg se supera i 1000g per pulizia visiva
        if unit == "g" and total >= 1000:
            display_total = f"{total/1000:.2f} Kg"
        else:
            display_total = f"{total} {unit}"
            
        target_col.write(f"- **{name}**: {display_total}")

if __name__ == "__main__":
    main()
