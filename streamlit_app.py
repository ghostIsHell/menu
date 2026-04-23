import streamlit as st
import random
import pandas as pd
import uuid
import time
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
        "Whole Grain Pasta": {"IT": "🍝 Pasta Integrale", "EN": "🍝 Whole Grain Pasta", "gr": 80},
        "Brown Rice": {"IT": "🍚 Riso Integrale", "EN": "🍚 Brown Rice", "gr": 80},
        "Spelt": {"IT": "🌾 Farro", "EN": "🌾 Spelt", "gr": 80},
        "Barley": {"IT": "🌾 Orzo", "EN": "🌾 Barley", "gr": 80},
        "Gnocchi": {"IT": "🥟 Gnocchi", "EN": "🥟 Gnocchi", "gr": 200},
        "Whole Grain Bread": {"IT": "🍞 Pane Integrale", "EN": "🍞 Whole Grain Bread", "gr": 50},
        "Potatoes": {"IT": "🥔 Patate", "EN": "🥔 Potatoes", "gr": 200},
        "Whole Grain Couscous": {"IT": "🥣 Couscous Integrale", "EN": "🥣 Whole Grain Couscous", "gr": 80},
        "Included": {"IT": "🥡 Incluso", "EN": "🥡 Included", "gr": 0}
    },
    "VEG": {
        "Broccoli": {"IT": "🥦 Broccoli", "EN": "🥦 Broccoli"},
        "Cauliflower": {"IT": "🥦 Cavolfiore", "EN": "🥦 Cauliflower"},
        "Fennel": {"IT": "🥗 Finocchi", "EN": "🥗 Fennel"},
        "Spinach": {"IT": "🍃 Spinaci", "EN": "🍃 Spinach"},
        "Chard": {"IT": "🍃 Bietole", "EN": "🍃 Chard"},
        "Artichokes": {"IT": "🎍 Carciofi", "EN": "🎍 Artichokes"},
        "Pumpkin": {"IT": "🎃 Zucca", "EN": "🎃 Pumpkin"},
        "Asparagus": {"IT": "🎋 Asparagi", "EN": "🎋 Asparagus"},
        "Peas": {"IT": "🫛 Piselli", "EN": "🫛 Peas"},
        "Broad Beans": {"IT": "🫛 Fave", "EN": "🫛 Broad Beans"},
        "Zucchini": {"IT": "🥒 Zucchine", "EN": "🥒 Zucchini"},
        "Salad": {"IT": "🥬 Insalata", "EN": "🥬 Salad"},
        "Tomatoes": {"IT": "🍅 Pomodori", "EN": "🍅 Tomatoes"},
        "Peppers": {"IT": "🫑 Peperoni", "EN": "🫑 Peppers"},
        "Eggplants": {"IT": "🍆 Melanzane", "EN": "🍆 Eggplants"},
        "Green Beans": {"IT": "🥗 Fagiolini", "EN": "🥗 Green Beans"},
        "Cucumbers": {"IT": "🥒 Cetrioli", "EN": "🥒 Cucumbers"},
        "Mushrooms": {"IT": "🍄 Funghi", "EN": "🍄 Mushrooms"},
        "Carrot": {"IT": "🥕 Carote", "EN": "🥕 Carrots"}
    }
}

UI_TEXT = {
"IT": {
        "auth_title": "🥗 Menù Settimanale", "title": "🥗 Menù Settimanale", "settings": "⚙️ Impostazioni", "people": "Persone a tavola",
        "pizza_toggle": "Includi Pizza Settimanale", "gen": "🔄 GENERA", "save": "💾 SALVA MODIFICHE",
        "sync": "Sincronizzato!", "pills": "📚 Pillole di Educazione Alimentare",
        "pills_txt": "- **Pizza:** 1 volta a settimana.\n- **Piatto Unico:** Pasta e fagioli, insalatone.\n- **Regola:** Sempre con verdura extra.",
        "guide": "⚖️ Grammature Consigliate",
        "guide_txt": "* **Cereali:** 80g\n* **Carne:** 120g\n* **Pesce:** 150g\n* **Verdura:** 200g",
        "freq": "📊 Frequenze Settimanali", "shop": "🛒 Lista della Spesa",
        "shop_calc": "Calcolata per", "days": ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"],
        "lunch": "Pranzo", "dinner": "Cena", "prot": "Proteina", "carb": "Carboidrato", "veg": "Verdura",
        "sugg": "ℹ️ Suggerimenti e Grammi", "total": "Totale per",
        "swap": "↔️ SCAMBIA", "confirm": "✅ CONFERMA", "lock": "Blocca", "pizza_tip": "🍕 Tip: Impasto integrale + contorno di finocchi/insalata.",
        "target_label": "Target", "menu_saved": "✅ Profilo e Menu salvati!", "cancel": "🚫 ANNULLA", "load_btn": "📥 CARICA PROFILO", "saved": "Tutto salvato!",
        "succes_reg": "Registrazione completata! Ora puoi accedere.", "welcomeback": "Bentornato. Accesso Eseguito!", "pwd_req": "Password (min. 6 caratteri)", "acc_create": "Crea Account", "logout":"Esci",
        "clear": "Pulisci Lista Spesa"
    },
    "EN": {
        "auth_title": "🥗 Weekly Menu", "title": "🥗 Weekly Menu", "settings": "⚙️ Settings", "people": "People at the table",
        "pizza_toggle": "Include Weekly Pizza", "gen": "🔄 GENERATE", "save": "💾 SAVE CHANGES",
        "sync": "Synced!", "pills": "📚 Nutritional Pills",
        "pills_txt": "- **Pizza:** Once a week.\n- **One-Pot Meal:** Pasta & beans, big salads.\n- **Rule:** Always add extra vegetables.",
        "guide": "⚖️ Portion Guidelines",
        "guide_txt": "* **Cereals:** 80g\n* **Meat:** 120g\n* **Fish:** 150g\n* **Vegetables:** 200g",
        "freq": "📊 Weekly Frequencies", "shop": "🛒 Shopping List",
        "shop_calc": "Calculated for", "days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
        "lunch": "Lunch", "dinner": "Dinner", "prot": "Protein", "carb": "Carbohydrate", "veg": "Vegetables",
        "sugg": "ℹ️ Suggestions & Grams", "total": "Total for",
        "swap": "↔️ SWAP", "confirm": "✅ CONFIRM", "lock": "Lock", "pizza_tip": "🍕 Tip: Whole dough + side of fennel/salad.",
        "target_label": "Target", "menu_saved": "✅ Profile & Menu saved!", "cancel": "🚫 CANCEL", "load_btn": "📥 LOAD PROFILE", "saved": "All saved!",
        "succes_reg": "Registration complete! You can now log in.", "welcomeback": "Welcome Back. You're logged in!", "pwd_req": "Password (min. 6 char)", "acc_create": "Create Account", "logout":"Logout",
        "clear": "Clear Shopping List"
    }
}

# --- 2. DATABASE ---
conn = st.connection(
    "supabase",
    type=SupabaseConnection,
    url=st.secrets["connections"]["supabase"]["url"],
    key=st.secrets["connections"]["supabase"]["key"]
)

def change_lang():
    # Il valore del widget con chiave "lang_selector" aggiorna direttamente lo stato
    st.session_state.lang = st.session_state.lang_selector

# --- AUTENTICAZIONE ---
def render_auth_screen():
    st.radio(
        "Language", 
        ["IT", "EN"], 
        horizontal=True, 
        key="lang_selector", # Chiave univoca per il widget
        on_change=change_lang, # Esegue la funzione al click
    )
    T = UI_TEXT[st.session_state.lang]
    st.title(T['auth_title'])
    
    tab1, tab2 = st.tabs(["Accedi", "Registrati"]) # TODO: T[]
    
    with tab1:
        with st.form("login"):
            email = st.text_input("Email")
            pwd = st.text_input("Password", type="password")
            if st.form_submit_button("Entra", use_container_width=True):
                user = login_user(email, pwd)
                if user:
                    st.success(T['welcomeback'])
                    time.sleep(1)
                    st.rerun()

    with tab2:
        with st.form("signup"):
            new_email = st.text_input("Email")
            new_pwd = st.text_input(T['pwd_req'], type="password")
            if st.form_submit_button(T['acc_create'], use_container_width=True):
                signup_user(new_email, new_pwd, T)

# Funzione per il Login
def login_user(email, password):
    try:
        res = conn.auth.sign_in_with_password({"email": email, "password": password})
        return res
    except Exception as e:
        st.error(f"Login Error: {e}")
        return None

# Funzione per la Registrazione
def signup_user(email, password, T):
    try:
        res = conn.auth.sign_up({"email": email, "password": password})
        st.success(T['succes_reg'])
        return res
    except Exception as e:
        st.error(f"Registration Error: {e}")
        return None

# Funzione per il Logout
def logout_user():
    conn.auth.sign_out()
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

def load_user_data(user_id):
    try:
        # 1. Carica il profilo
        res_prof = conn.table("profiles").select("*").eq("id", user_id).execute()

        if not res_prof.data or len(res_prof.data) == 0:
            return None, None

        profile = res_prof.data[0]
        
        # 2. Carica i pasti legati a quel profilo ID
        res_meals = conn.table("user_dinner").select("*").eq("profile_id", user_id).execute()
            
        meals = None
        if res_meals.data and len(res_meals.data) == 14:
            meals = sorted(res_meals.data, key=lambda x: (x['day_idx'], x['type'] == 'Dinner'))
            
        return profile, meals

    except Exception as e:
        st.error(f"Load Data Errore: {e}")
        return None, None

def save_all_data(user_id, user_email, n_people, pizza_on, meals, T):
    try:
        # 1. Upsert del profilo (Inserisce o aggiorna se lo username esiste)
        prof_data = {
            "id": user_id,
            "username": user_email,
            "n_people": n_people,
            "pizza_enabled": pizza_on,
            "default_lang": st.session_state.lang
        }
        
        # Upsert basato sulla PRIMARY KEY (id)
        conn.table("profiles").upsert(prof_data).execute()

        # 2. Reset e inserimento pasti
        conn.table("user_dinner").delete().eq("profile_id", user_id).execute()
        
        to_insert = []
        for i, m in enumerate(meals):
            to_insert.append({
                "profile_id": user_id,
                "day_idx": i // 2,
                "type": m["type"],
                "prot": m["prot"],
                "carbo": m["carbo"],
                "veg": m["veg"],
                "locked": m.get("locked", False)
            })
        conn.table("user_dinner").insert(to_insert).execute()
        st.success(T['saved'])
    except Exception as e:
        st.error(f"Save Error: {e}")

# --- 3. LOGICA GENERAZIONE ---
def generate_menu(pizza_on, current_meals=None):
    pool = []
    targets = {k: v["target"] for k, v in DATA["PROT"].items()}
    if not pizza_on:
        targets["Pizza"] = 0
        targets["Legumes"] += 1
        
    if current_meals: # cambiata
        for m in current_meals:
            if m.get("locked") and m["prot"] in targets and targets[m["prot"]] > 0:
                targets[m["prot"]] -= 1
    
    for k, v in targets.items(): pool.extend([k] * v)
    random.shuffle(pool)
    
    meals = []
    veg_keys = list(DATA["VEG"].keys())
    for i in range(14):
        if current_meals and current_meals[i].get("locked"):
            meals.append(current_meals[i])
        else:
            p = pool.pop() if pool else random.choice(list(DATA["PROT"].keys()))
            is_lunch = i % 2 == 0
            if p in ["Pizza", "One-Pot Meal"]: c = "Included"
            else: c = random.choice(["Whole Grain Pasta", "Brown Rice", "Spelt", "Barley", "Gnocchi"] if is_lunch else ["Whole Grain Bread", "Potatoes", "Whole Grain Couscous"])
            meals.append({"type": "Lunch" if is_lunch else "Dinner", "prot": p, "carbo": c, "veg": random.choice(veg_keys), "locked": False})
    return meals

def update_meal(idx):
    # Recupera i valori dai widget usando le chiavi temporanee
    v_key = st.session_state.menu_version
    new_p = st.session_state[f"p{idx}_{v_key}"]
    new_v = st.session_state[f"v{idx}_{v_key}"]
    # Se non è pizza/piatto unico, prendi il carbo, altrimenti "Included"
    if new_p in ["Pizza", "One-Pot Meal"]:
        new_c = "Included"
    else:
        # Recupera il carboidrato attuale dallo stato
        current_c = st.session_state.get(f"c{idx}_{v_key}", st.session_state.meals[idx]["carbo"])
        # Se è "Included" ma ora serve un carboidrato vero, metti un default
        if current_c == "Included":
            new_c = "Whole Grain Pasta" if idx % 2 == 0 else "Whole Grain Bread"
        else:
            new_c = current_c
    
    # Aggiorna lo stato ufficiale
    st.session_state.meals[idx].update({
        "prot": new_p, 
        "carbo": new_c, 
        "veg": new_v
    })

def get_grouped_shopping_list(meals, n_people, lang):
    basket = {
        "🥩 Proteine": {},
        "🍞 Carboidrati": {},
        "🥦 Verdure": {}
    }
    
    for m in meals:
        # Calcolo Proteine
        p_info = DATA["PROT"][m["prot"]]
        name_p = p_info[lang]
        if name_p not in basket["🥩 Proteine"]:
            basket["🥩 Proteine"][name_p] = {"q": 0, "u": p_info["unit"]}
        basket["🥩 Proteine"][name_p]["q"] += p_info["gr"] * n_people

        # Calcolo Carboidrati
        if m["carbo"] != "Included":
            c_info = DATA["CARBO"][m["carbo"]]
            name_c = c_info[lang]
            if name_c not in basket["🍞 Carboidrati"]:
                basket["🍞 Carboidrati"][name_c] = {"q": 0, "u": "g"}
            basket["🍞 Carboidrati"][name_c]["q"] += c_info["gr"] * n_people

        # Calcolo Verdure
        v_name = DATA["VEG"][m["veg"]][lang]
        if v_name not in basket["🥦 Verdure"]:
            basket["🥦 Verdure"][v_name] = {"q": 0, "u": "g"}
        basket["🥦 Verdure"][v_name]["q"] += 200 * n_people
        
    return basket

def render_menu_grid(T):
    st.subheader(T.get("menu_title")) # O usa una chiave di UI_TEXT
    
    for i, day_name in enumerate(T["days"]):
        with st.expander(f"📅 {day_name.upper()}"):
            cols = st.columns(2)
            for j in range(2):
                idx = i * 2 + j
                render_meal_card(idx, j, T)

def render_meal_card(idx, col_idx, T):
    """
    idx: indice assoluto nel session_state.meals (0-13)
    col_idx: 0 per pranzo, 1 per cena
    """
    m = st.session_state.meals[idx]
    v_key = st.session_state.menu_version
    is_swapping = (st.session_state.swap_idx == idx)
    active_swap = (st.session_state.swap_idx is not None)

    with st.container(border=True):
        # Titolo della card
        label = T['lunch' if col_idx == 0 else 'dinner']
        st.write(f"**{label}**" if not is_swapping else f"### {T['swap']}")

        # --- SELETTORI ---
        new_p = st.selectbox(
            T["prot"], 
            list(DATA["PROT"].keys()), 
            index=list(DATA["PROT"].keys()).index(m["prot"]), 
            format_func=lambda x: DATA["PROT"][x][st.session_state.lang], 
            key=f"p{idx}_{v_key}",
            on_change=update_meal,
            args=(idx,)
        )

        if new_p in ["Pizza", "One-Pot Meal"]:
            new_c = "Included"
            if new_p == "Pizza": st.warning(T["pizza_tip"])
        else:
            c_opts = [ck for ck in DATA["CARBO"].keys() if ck != "Included"]
            c_idx = c_opts.index(m["carbo"]) if m["carbo"] in c_opts else 0
            new_c = st.selectbox(
                T["carb"], 
                c_opts, 
                index=c_idx, 
                format_func=lambda x: DATA["CARBO"][x][st.session_state.lang], 
                key=f"c{idx}_{v_key}",
                on_change=update_meal,
                args=(idx,)
            )

        new_v = st.selectbox(
            T["veg"], 
            list(DATA["VEG"].keys()), 
            index=list(DATA["VEG"].keys()).index(m["veg"]), 
            format_func=lambda x: DATA["VEG"][x][st.session_state.lang], 
            key=f"v{idx}_{v_key}",
            on_change=update_meal,
            args=(idx,)
        )

        # --- GRAMMI DINAMICI ---
        with st.expander(T["sugg"]):
            g_p = DATA["PROT"][new_p]["gr"]
            g_c = DATA["CARBO"][new_c]["gr"]
            u_p = "pz" if DATA["PROT"][new_p]["unit"] == "pz" else "g"
            st.write(f"**{T['total']} {st.session_state.n_people}:**")
            st.write(f"- {DATA['PROT'][new_p][st.session_state.lang]}: {g_p * st.session_state.n_people} {u_p}")
            if g_c > 0: 
                st.write(f"- {DATA['CARBO'][new_c][st.session_state.lang]}: {g_c * st.session_state.n_people} g")
            st.write(f"- {T['veg']}: {200 * st.session_state.n_people} g")

        # --- SWAP & LOCK ---
        sl1, sl2 = st.columns(2)
        m["locked"] = sl1.checkbox(T["lock"], m["locked"], key=f"lk{idx}_{v_key}")

        # Logica del Bottone Swap
        if is_swapping:
            btn_label, btn_type = T["cancel"], "secondary"
        elif active_swap:
            btn_label, btn_type = T["confirm"], "primary"
        else:
            btn_label, btn_type = T["swap"], "secondary"

        if sl2.button(btn_label, key=f"sw{idx}_{v_key}", use_container_width=True, type=btn_type):
            handle_swap_logic(idx, is_swapping)

def handle_swap_logic(idx, is_swapping):
    """Gestisce la logica di scambio separata per pulizia"""
    if st.session_state.swap_idx is None:
        st.session_state.swap_idx = idx
        st.rerun()
    elif is_swapping:
        st.session_state.swap_idx = None
        st.rerun()
    else:
        idx1, idx2 = st.session_state.swap_idx, idx
        st.session_state.meals[idx1], st.session_state.meals[idx2] = \
            st.session_state.meals[idx2], st.session_state.meals[idx1]
        st.session_state.swap_idx = None
        st.session_state.menu_version += 1 
        st.rerun()

def render_shopping_section(T):
    st.divider()
    st.subheader(T['shop'])

    # Verifica se ci sono pasti, altrimenti esce
    if not st.session_state.meals:
        st.info("Nessun pasto selezionato.")
        return

    # Bottone di reset
    if st.button(T['clear'], use_container_width=True):
        for key in list(st.session_state.keys()):
            if key.startswith("shop_"):
                st.session_state[key] = False
        st.rerun()

    # Otteniamo i dati calcolati
    shopping_data = get_grouped_shopping_list(
        st.session_state.meals, 
        st.session_state.n_people, 
        st.session_state.lang
    )

    # Visualizzazione a 3 colonne
    cols = st.columns(3)
    for idx, (cat, items) in enumerate(shopping_data.items()):
        with cols[idx]:
            st.markdown(f"#### {cat}")
            for name, info in items.items():
                q, u = info["q"], info["u"]
                # Formattazione Peso
                val = f"{q/1000:.2f} Kg" if (u=="g" and q>=1000) else f"{int(q)} {u}"
                
                # Checkbox
                st.checkbox(f"**{name}** ({val})", key=f"shop_{cat}_{name}")

def render_app_content(user_id, user_email, T):
    # --- INIZIALIZZAZIONE STATO ---
    if "menu_version" not in st.session_state: st.session_state.menu_version = 0
    if "swap_idx" not in st.session_state: st.session_state.swap_idx = None
    if "n_people" not in st.session_state: st.session_state.n_people = 2
    if "piz" not in st.session_state: st.session_state.piz = True

    # --- CARICAMENTO AUTOMATICO DATI (Solo la prima volta) ---
    if "loaded_for_user" not in st.session_state or st.session_state.loaded_for_user != user_id:
        profile, db_meals = load_user_data(user_id)
        if profile:
            st.session_state.n_people = profile['n_people']
            st.session_state.piz = profile['pizza_enabled']
            st.session_state.lang = profile['default_lang']
            if db_meals:
                st.session_state.meals = [{
                    "type": m["type"], 
                    "prot": m["prot"], 
                    "carbo": m["carbo"], 
                    "veg": m["veg"], 
                    "locked": m["locked"]
                } for m in db_meals]
        st.session_state.loaded_for_user = user_id
    # --- SIDEBAR SETTINGS ---
    with st.sidebar:
        st.radio(
            "Language", 
            ["IT", "EN"], 
            horizontal=True, 
            key="lang_selector", # Chiave univoca per il widget
            on_change=change_lang, # Esegue la funzione al click
        )
        T = UI_TEXT[st.session_state.lang]
        st.header(T["settings"])

        n_people = st.number_input(T["people"], 1, 10, value=st.session_state.n_people)
        st.session_state.n_people = n_people # Sync
        
        piz = st.toggle(T["pizza_toggle"], value=st.session_state.piz)
        st.session_state.piz = piz # Sync
        
        if st.button(T["gen"], use_container_width=True):
            current = st.session_state.get("meals")
            st.session_state.meals = generate_menu(piz, current)
            st.session_state.swap_idx = None
            st.session_state.menu_version += 1
            st.rerun()
            
        if st.button(T["save"], use_container_width=True):
            save_all_data(user_id, user_email, st.session_state.n_people, piz, st.session_state.meals, T)
            
    # Caricamento iniziale pasti
    if "meals" not in st.session_state:
        st.session_state.meals = generate_menu(st.session_state.piz)

    st.title(f"{T['title']}")

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
        target = v["target"] if (k != "Pizza" or st.session_state.piz) else 0
        if not st.session_state.piz and k == "Legumes": target = 4
        
        # Logica Colore Target
        color = "normal" if current == target else "inverse" if current > target else "off"
        arrow = "off" if current == target else "up" if current > target else "down"
        
        cols[i].metric(label=v[st.session_state.lang], value=current, delta=f"{T['target_label']}: {target}", delta_color=color, delta_arrow=arrow)

    # --- GRID ---
    render_menu_grid(T)

    # --- SHOPPING LIST STILIZZATA ---
    render_shopping_section(T)

# --- 4. APP ---
def main():
    if "lang" not in st.session_state: st.session_state.lang = "IT"
    T = UI_TEXT[st.session_state.lang]

    st.set_page_config(page_title="Menu", layout="wide")
    
    # Autenticazione
    # Controllo Sessione Supabase
    try:
        session = conn.auth.get_session()
    except:
        session = None

    if not session:
        # Se non c'è sessione, mostra solo il login
        render_auth_screen()
    else:
        # Se l'utente è autenticato, mostra l'app
        user_id = session.user.id
        user_email = session.user.email
        
        # Sidebar con Logout e Info Utente
        with st.sidebar:
            st.markdown(f"#### {T['title']")
            st.write(f"👤 **{user_email}**")
            if st.button(T["logout"], type="primary"):
                logout_user()
            st.divider()
            
        render_app_content(user_id, user_email, T)

if __name__ == "__main__": main()
