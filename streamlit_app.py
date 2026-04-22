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

# --- 2. DATABASE CONNECTION ---
conn = st.connection(
    "supabase",
    type=SupabaseConnection,
    url=st.secrets["connections"]["supabase"]["url"],
    key=st.secrets["connections"]["supabase"]["key"]
)

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

# --- 3. UI COMPONENTS ---
def render_meal_card(idx):
    meal = st.session_state.meals[idx]
    is_swapping = (st.session_state.swap_idx == idx)
    
    with st.container(border=True):
        st.markdown(f"**{'☀️' if meal['type'] == 'Lunch' else '🌙'} {meal['type']}**")
        
        # Selectors
        prot_options = list(CONFIG["EMOJI_PROT"].keys())
        new_p = st.selectbox("Protein", prot_options, index=prot_options.index(meal['prot']), key=f"p_{idx}_{st.session_state.sync_key}")
        
        if new_p in ['Pizza', 'One-Pot Meal']:
            new_c = "Included"
            if new_p == 'Pizza': st.warning("🍕 Tip: Whole dough + side of fennel/salad.")
            else: st.info(f"🍲 Example: {CONFIG['ONE_POT_EXAMPLES'][idx % len(CONFIG['ONE_POT_EXAMPLES'])]}")
        else:
            c_opts = CONFIG["ALL_CARBO"]
            curr_c = meal['carbo'] if meal['carbo'] in c_opts else c_opts[0]
            new_c = st.selectbox("Carb", c_opts, index=c_opts.index(curr_c), key=f"c_{idx}_{st.session_state.sync_key}")
        
        new_v = st.selectbox("Vegetables", ALL_VEG, index=ALL_VEG.index(meal['veg']), key=f"v_{idx}_{st.session_state.sync_key}")

        # --- NEW: TIPS & PORTIONS EXPANDER ---
        with st.expander("ℹ️ Tips & Portions"):
            st.markdown("**Recommended Portions (per person):**")
            for item, weight in CONFIG["PORTIONS_INFO"].items():
                st.write(f"- {item}: {weight}")
            st.markdown("---")
            st.markdown("**Cooking Tip:** Always prefer steaming or grilling to keep nutrients intact.")

        # Sync changes to session state
        if new_p != meal['prot'] or new_c != meal['carbo'] or new_v != meal['veg']:
            st.session_state.meals[idx].update({"prot": new_p, "carbo": new_c, "veg": new_v})

        # Swap & Lock Actions
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
                i1, i2 = st.session_state.swap_idx, idx
                st.session_state.meals[i1], st.session_state.meals[i2] = st.session_state.meals[i2], st.session_state.meals[i1]
                st.session_state.swap_idx = None
                st.session_state.sync_key = str(uuid.uuid4())
                st.rerun()

# --- 4. MAIN APP ---
def main():
    st.set_page_config(page_title="DB Healthy Menu", layout="wide")
    
    if 'sync_key' not in st.session_state: st.session_state.sync_key = str(uuid.uuid4())
    if 'swap_idx' not in st.session_state: st.session_state.swap_idx = None

    with st.sidebar:
        st.header("Settings")
        username = st.text_input("Username", value="default_user")
        use_pizza = st.toggle("Include Pizza", value=True)
        
        if st.button("🔄 GENERATE & SAVE"):
            # logic for generate_new_menu remains as before
            from streamlit_app import generate_new_menu # Assuming it's in the same file or imported
            st.session_state.meals = generate_new_menu(use_pizza)
            save_menu_to_db(username, st.session_state.meals)
            st.rerun()
        
        if st.button("💾 SAVE CHANGES"):
            save_menu_to_db(username, st.session_state.meals)
            st.success("Synced!")

    if 'meals' not in st.session_state:
        db_data = load_menu_from_db(username)
        if db_data: st.session_state.meals = db_data
        else: st.warning("Please generate a menu.")

    st.title(f"🥗 Weekly Menu for {username}")

    # --- 📊 ENHANCED STATISTICS SECTION ---
    st.subheader("📊 Protein Balance")
    cols = st.columns(len(CONFIG["EMOJI_PROT"]))
    all_prots = [m['prot'] for m in st.session_state.meals] if 'meals' in st.session_state else []
    
    # Dynamic target adjustment
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

    # --- 📅 GRID RENDERING ---
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    if 'meals' in st.session_state:
        for i, day in enumerate(days):
            with st.expander(f"📅 {day.upper()}"):
                l, r = st.columns(2)
                with l: render_meal_card(i*2)
                with r: render_meal_card(i*2 + 1)

if __name__ == "__main__":
    main()
