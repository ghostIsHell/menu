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
    "PORTIONS_INFO": {
        "Whole Grain Pasta": "80g", "Brown Rice": "80g", "Spelt/Barley": "80g", "Gnocchi": "200g",
        "Whole Grain Bread": "50-60g", "Potatoes": "200g", "Legumes (Dry)": "50g", "Legumes (Cooked)": "150g",
        "Fish": "150g", "White Meat": "120g", "Red Meat": "100g", "Cheese": "100g", "Eggs": "2 units"
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
# Using the manual secret mapping for maximum reliability
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
    except Exception:
        return None

def save_menu_to_db(username, meals):
    try:
        # 1. Clean old entries for this specific user
        conn.table(CONFIG["TABLE_NAME"]).delete().eq("user_id", username).execute()
        
        # 2. Prepare new data
        insert_data = []
        for i, m in enumerate(meals):
            insert_data.append({
                "user_id": username,
                "day_idx": i // 2,
                "type": m["type"],
                "prot": m["prot"],
                "carbo": m["carbo"],
                "veg": m["veg"],
                "locked": m.get("locked", False)
            })
        
        # 3. Bulk insert
        conn.table(CONFIG["TABLE_NAME"]).insert(insert_data).execute()
        st.sidebar.success("Database synced successfully!")
    except Exception as e:
        st.error(f"Sync Error: {e}")

# --- 3. MEAL GENERATION ENGINE ---
def build_protein_pool(use_pizza):
    pool = []
    targets = CONFIG["TARGET_PROT"].copy()
    if use_pizza:
        targets["Pizza"] = 1
    else:
        targets["Legumes"] += 1
    
    for prot, count in targets.items():
        pool.extend([prot] * count)
    random.shuffle(pool)
    return pool

def generate_new_menu(use_pizza=True):
    prot_pool = build_protein_pool(use_pizza)
    current_season_veg = CONFIG["VEG_SEASONAL"][get_current_season()]
    meals = []
    
    for i in range(14):
        m_type = "Lunch" if i % 2 == 0 else "Dinner"
        prot = prot_pool.pop()
        
        if prot in ['Pizza', 'One-Pot Meal']:
            carbo = "Included"
        else:
            carbo = random.choice(CONFIG["CARBO_LUNCH"] if m_type == "Lunch" else CONFIG["CARBO_DINNER"])
            
        meals.append({
            "type": m_type,
            "prot": prot,
            "carbo": carbo,
            "veg": random.choice(current_season_veg),
            "locked": False
        })
    return meals

# --- 4. UI COMPONENTS ---
def render_meal_card(idx):
    meal = st.session_state.meals[idx]
    is_swapping = (st.session_state.swap_idx == idx)
    
    with st.container(border=True):
        st.markdown(f"**{'☀️' if meal['type'] == 'Lunch' else '🌙'} {meal['type']}**")
        
        # Protein Selection
        prot_options = list(CONFIG["EMOJI_PROT"].keys())
        new_p = st.selectbox("Protein Source", prot_options, 
                             index=prot_options.index(meal['prot']), 
                             key=f"p_{idx}_{st.session_state.sync_key}")
        
        # Carbs logic & specific warnings
        if new_p in ['Pizza', 'One-Pot Meal']:
            new_c = "Included"
            if new_p == 'Pizza':
                st.warning("🍕 Tip: Whole dough + side of fennel/salad.")
            else:
                st.info(f"🍲 Example: {CONFIG['ONE_POT_EXAMPLES'][idx % len(CONFIG['ONE_POT_EXAMPLES'])]}")
        else:
            carbo_options = CONFIG["ALL_CARBO"]
            current_c = meal['carbo'] if meal['carbo'] in carbo_options else carbo_options[0]
            new_c = st.selectbox("Cereal/Carb", carbo_options, 
                                 index=carbo_options.index(current_c), 
                                 key=f"c_{idx}_{st.session_state.sync_key}")
        
        # Vegetable selection
        new_v = st.selectbox("Vegetables", ALL_VEG, 
                             index=ALL_VEG.index(meal['veg']), 
                             key=f"v_{idx}_{st.session_state.sync_key}")

        # Info Expander (Portions)
        with st.expander("ℹ️ Info & Grams"):
            st.write("**Target Portions:**")
            for item, grams in CONFIG["PORTIONS_INFO"].items():
                st.caption(f"- {item}: {grams}")

        # State Update
        if new_p != meal['prot'] or new_c != meal['carbo'] or new_v != meal['veg']:
            st.session_state.meals[idx].update({"prot": new_p, "carbo": new_c, "veg": new_v})

        # Actions (Lock & Swap)
        c1, c2 = st.columns(2)
        meal['locked'] = c1.checkbox("Lock", value=meal['locked'], key=f"l_{idx}_{st.session_state.sync_key}")
        
        btn_label = "✅ CONFIRM" if (st.session_state.swap_idx is not None and not is_swapping) else "↔️ SWAP"
        if is_swapping: btn_label = "🚫 CANCEL"
        
        if c2.button(btn_label, key=f"btn_{idx}_{st.session_state.sync_key}", use_container_width=True):
            if st.session_state.swap_idx is None:
                st.session_state.swap_idx = idx
                st.rerun()
            elif is_swapping:
                st.session_state.swap_idx = None
                st.rerun()
            else:
                idx1, idx2 = st.session_state.swap_idx, idx
                st.session_state.meals[idx1], st.session_state.meals[idx2] = st.session_state.meals[idx2], st.session_state.meals[idx1]
                st.session_state.swap_idx = None
                st.session_state.sync_key = str(uuid.uuid4())
                st.rerun()

# --- 5. MAIN APP ---
def main():
    st.set_page_config(page_title="Safe Healthy Menu DB", layout="wide", page_icon="🥗")
    
    # State initialization
    if 'sync_key' not in st.session_state: st.session_state.sync_key = str(uuid.uuid4())
    if 'swap_idx' not in st.session_state: st.session_state.swap_idx = None

    # Sidebar Controls
    with st.sidebar:
        st.header("👤 Profile & Settings")
        username = st.text_input("Username / Email", value="guest_user")
        use_pizza = st.toggle("Include Weekly Pizza", value=True)
        
        st.divider()
        if st.button("🔄 GENERATE NEW MENU", use_container_width=True):
            st.session_state.meals = generate_new_menu(use_pizza)
            save_menu_to_db(username, st.session_state.meals)
            st.rerun()
        
        if st.button("💾 SAVE CHANGES", type="primary", use_container_width=True):
            save_menu_to_db(username, st.session_state.meals)
            st.success("All changes saved to database!")

    # Load data from DB if session is empty
    if 'meals' not in st.session_state:
        db_data = load_menu_from_db(username)
        if db_data:
            st.session_state.meals = db_data
        else:
            st.session_state.meals = generate_new_menu(use_pizza)

    st.title(f"🥗 Weekly Menu for {username}")

    # --- 📊 PROTEIN STATISTICS LOGIC ---
    st.subheader("📊 Protein Balance Status")
    cols = st.columns(len(CONFIG["EMOJI_PROT"]))
    all_prots = [m['prot'] for m in st.session_state.meals]
    
    adj_targets = CONFIG["TARGET_PROT"].copy()
    if use_pizza: adj_targets["Pizza"] = 1
    else: adj_targets["Legumes"] += 1

    for i, (name, target) in enumerate(adj_targets.items()):
        current = all_prots.count(name)
        emoji = CONFIG["EMOJI_PROT"][name]
        
        if current == target:
            color = "normal"
            arrow = "off"
            label = f"↕ Target: {target}"
        elif current > target: 
            color = "inverse"
            arrow = "up"
            label = f"Target: {target}"
        else: 
            color = "off"
            arrow = "down"
            label = f"Target: {target}"
        
        cols[i].metric(
            label=f"{emoji} {name}", 
            value=f"{current}", 
            delta=label, 
            delta_color=color, 
            delta_arrow=arrow
        )

    # --- 📅 MENU GRID ---
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    for i, day_name in enumerate(days):
        with st.expander(f"📅 {day_name.upper()}"):
            col_l, col_r = st.columns(2)
            with col_l: render_meal_card(i*2)
            with col_r: render_meal_card(i*2 + 1)

if __name__ == "__main__":
    main()
