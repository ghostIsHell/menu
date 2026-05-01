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
        "pizza_toggle": "Includi Pizza Settimanale", "gen": "🔄 GENERA", "save": "💾 SALVA MODIFICHE", "copy": "📋 COPIA MENÙ TESTUALE", "copy_here": "Copia da qui:", "copy_info": "Clicca sull'icona in alto a destra nel riquadro per copiare tutto!",
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
        "clear": "Pulisci Lista Spesa", "myths": "Sfatiamo alcuni miti", "general_source": "Fonte: Linee guida per una sana alimentazione (CREA)",
        "fish_tip_1": "⚠️ Se usi tonno/salmone sott'olio: 50g sgocciolato a testa (max 1 volta/sett).", "fish_tip_2": "🐟 Alterna pesci grassi (salmone) a pesci magri (orata).",
        "title_myths": "##### 🍬 Miti", "title_learn": "C'è sempre qualcosa di nuovo da imparare..."
    
    },
    "EN": {
        "auth_title": "🥗 Weekly Menu", "title": "🥗 Weekly Menu", "settings": "⚙️ Settings", "people": "People at the table",
        "pizza_toggle": "Include Weekly Pizza", "gen": "🔄 GENERATE", "save": "💾 SAVE CHANGES", "copy": "📋 COPY TEXT MENÙ", "copy_here": "Copy from here:", "copy_info": "💡 Click the icon in the top right of the box to copy everything!",
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
        "clear": "Clear Shopping List", "myths": "Let's dispel some myths", "general_source": "Source: Guidelines for a healthy diet (CREA)",
        "fish_tip_1": "⚠️ If using tuna/salmon in oil: 50g drained per person (max 1 time/week).", "fish_tip_2": "🐟 Alternate fatty fish (salmon) with lean fish (sea bream).",
        "title_myths": "##### 🍬 Miths", "title_learn": "There's always something new to learn..."
    }
}

TIPS = {
    "IT": [
        "Scegli porzioni adeguate di tutti i gruppi alimentari, alternandoli nei vari pasti.",
        "Evita digiuni prolungati: uno spuntino leggero (come un frutto) mantiene alta l'attenzione.",
        "Non mangiare davanti al computer! Fare una pausa vera aiuta a controllare il peso e avere più coscienza di ciò che mangi.",
        "Aumenta la varietà di alimenti vegetali: prova a consumare più tipi di verdura e frutta nello stesso pasto.",
        "Riduci il consumo di carne e privilegia altre fonti proteiche.",
        "Fai sempre un'adeguata prima colazione ogni giorno.",
        "Diversifica le scelte alimentari: variare i cibi riduce il rischio di assumere ripetutamente sostanze indesiderate.",
        "L'olio extravergine d'oliva è il miglior grasso, ma attenzione alle quantità!",
        "La cottura in forno non è sempre la più sana: occhio all'olio nella teglia e alle alte temperature.",
        "Uova e colesterolo: non vanno evitate, basta non eccedere e limitare salumi e formaggi.",
        "Il tonno sott'olio va limitato a circa 1 volta a settimana (porzione 50g sgocciolato)."
    ],
    "EN": [
        "Choose appropriate portions from all food groups, alternating them across meals.",
        "Avoid prolonged fasting: a light snack (such as a piece of fruit) helps maintain attention.",
        "Don’t eat in front of the computer! Taking a real break helps control weight and be more aware of what you eat.",
        "Increase the variety of plant-based foods: try to include more types of vegetables and fruits in the same meal.",
        "Reduce meat consumption and prioritize other protein sources.",
        "Always have an adequate breakfast every day.",
        "Diversify your food choices: varying foods reduces the risk of repeatedly consuming unwanted substances.",
        "Extra virgin olive oil is the best fat, but watch the quantities!",
        "Oven cooking is not always the healthiest: be mindful of the oil in the tray and high temperatures.",
        "Eggs and cholesterol: they don’t need to be avoided, just don’t overdo it and limit processed meats and cheeses.",
        "Tuna in oil should be limited to about once a week (portion: 50g drained)."
    ]
}

MYTHS_AND_CUR = {
    "IT": [
        {"titolo": "Zucchero di canna vs Bianco", "testo": "Non è vero che lo zucchero grezzo sia più nutriente. La differenza di colore dipende solo da residui vegetali (melassa) senza vantaggi nutrizionali: sono la stessa cosa."},
        {"titolo": "Zucchero e Iperattività", "testo": "Studi approfonditi hanno smentito che il saccarosio provochi alterazioni del comportamento o iperattività nei bambini."},
        {"titolo": "Succhi 'Senza Zuccheri Aggiunti'", "testo": "Contengono comunque gli zuccheri naturali della frutta (8-10%). Un bicchiere fornisce circa 70kcal: sono zuccheri liberi da controllare."},
        {"titolo": "Il Miele è dietetico?", "testo": "No. Pur avendo meno calorie per 100g rispetto allo zucchero (304 vs 392) a causa dell'acqua, rimane una fonte di zuccheri aggiunti da consumare con moderazione."},
        {"titolo": "Miele e Neonati ⚠️", "testo": "Sotto i 12 mesi il miele è sconsigliato: può contenere spore di botulino che il sistema dei neonati non riesce a contrastare. Pericoloso anche se pastorizzato."},
        {"titolo": "Prodotti Light", "testo": "Non sono una scusa per mangiarne di più. Spesso inducono un falso senso di sicurezza, ma possono avere molte calorie. Leggi sempre l'etichetta."},
        {"titolo": "Lo Zucchero è un veleno?", "testo": "Non esistono alimenti buoni o cattivi in assoluto. È la quantità totale nella dieta a fare la differenza. I residui di lavorazione (calce, anidride solforosa) sono presenti in tracce innocue."},
        {"titolo": "Dipendenza da Zucchero", "testo": "Non esiste una vera dipendenza fisica. È un comportamento compulsivo che può essere corretto con una buona educazione alimentare."}
    ],
    "EN": [
        {"titolo": "Brown Sugar vs White Sugar", "testo": "It is not true that raw sugar is more nutritious. The difference in color is only due to plant residues (molasses) with no nutritional advantages: they are essentially the same."},
        {"titolo": "Sugar and Hyperactivity", "testo": "Extensive studies have debunked the idea that sucrose causes behavioral changes or hyperactivity in children."},
        {"titolo": "'No Added Sugar' Juices", "testo": "They still contain the natural sugars of fruit (8–10%). A glass provides about 70 kcal: these are free sugars that should be monitored."},
        {"titolo": "Is Honey Diet-Friendly?", "testo": "No. Although it has fewer calories per 100g than sugar (304 vs 392) due to its water content, it remains a source of added sugars to be consumed in moderation."},
        {"titolo": "Honey and Infants ⚠️", "testo": "Under 12 months, honey is not recommended: it may contain botulinum spores that infants’ systems cannot fight. Dangerous even if pasteurized."},
        {"titolo": "Light Products", "testo": "They are not an excuse to eat more. They often create a false sense of security but can still be high in calories. Always read the label."},
        {"titolo": "Is Sugar a Poison?", "testo": "There are no foods that are absolutely good or bad. It is the total amount in the diet that makes the difference. Processing residues (lime, sulfur dioxide) are present only in harmless traces."},
        {"titolo": "Sugar Addiction", "testo": "There is no true physical addiction. It is a compulsive behavior that can be corrected with proper nutritional education."}
    ]
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
    st.session_state.menu_version += 1
    st.session_state.swap_idx = None

def get_menu_text_format(meals, T):
    """Trasforma la lista dei pasti in una stringa leggibile per il copia-incolla"""
    output = f"📅 {T['title'].upper()} 🥗\n\n"
    
    for i, day_name in enumerate(T["days"]):
        output += f"--- {day_name.upper()} ---\n"
        
        # Pranzo
        m_l = meals[i*2]
        output += f"☀️ {T['lunch']}: {DATA['PROT'][m_l['prot']][st.session_state.lang]} + "
        output += f"{DATA['CARBO'][m_l['carbo']][st.session_state.lang] if m_l['carbo'] != 'Included' else ''} + "
        output += f"{DATA['VEG'][m_l['veg']][st.session_state.lang]}\n"
        
        # Cena
        m_d = meals[i*2 + 1]
        output += f"🌙 {T['dinner']}: {DATA['PROT'][m_d['prot']][st.session_state.lang]} + "
        output += f"{DATA['CARBO'][m_d['carbo']][st.session_state.lang] if m_d['carbo'] != 'Included' else ''} + "
        output += f"{DATA['VEG'][m_d['veg']][st.session_state.lang]}\n\n"
    
    return output

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
            is_lunch = (i % 2 == 0)
            to_insert.append({
                "profile_id": user_id,
                "day_idx": i // 2,
                "type": "Lunch" if is_lunch else "Dinner",
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

    # Sottraiamo le proteine dei pasti "bloccati" dal pool
    if current_meals:
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
            is_lunch = i % 2 == 0

            # Cerchiamo una proteina nel pool diversa dall'ultima usata
            p = None
            # Proviamo con memoria 3, poi 2, poi 1
            for window_size in [3, 2, 1]:
                recent_prots = [m["prot"] for m in meals[-window_size:]] if i > 0 else []
                for idx, candidate in enumerate(pool):
                    if candidate not in recent_prots:
                        p = pool.pop(idx)
                        break
                if p: break # Trovata!
                    
            # Fallback estremo: se proprio non c'è scelta, prendi il primo del pool
            if not p and pool:
                p = pool.pop(0)
            elif not p:
                p = random.choice(list(DATA["PROT"].keys()))

            if p in ["Pizza", "One-Pot Meal"]: c = "Included"
            else: c = random.choice(["Whole Grain Pasta", "Brown Rice", "Spelt", "Barley", "Gnocchi"] if is_lunch else ["Whole Grain Bread", "Potatoes", "Whole Grain Couscous"])
            
            # --- VERDURA CON VINCOLI DECRESCENTI ---
            v = None
            for window_size in [3, 2, 1]:
                recent_vegs = [m["veg"] for m in meals[-window_size:]] if i > 0 else []
                available_veg = [veg for veg in veg_keys if veg not in recent_vegs]
                if available_veg:
                    v = random.choice(available_veg)
                    break
            if not v: v = random.choice(veg_keys)
            
            meals.append({"type": "Lunch" if is_lunch else "Dinner", "prot": p, "carbo": c, "veg": v, "locked": False})
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
    basket = { # TODO: lan
        "🥩 Proteine": {},
        "🍞 Carboidrati": {},
        "🥦 Verdure": {}
    }
    
    for m in meals:
        prot_key = m["prot"]
        carbo_key = m["carbo"]
        veg_key = m["veg"]
        # Se la chiave non esiste (es. è in italiano), cerchiamo di recuperarla o saltiamo
        if prot_key not in DATA["PROT"] or (carbo_key not in DATA["CARBO"] and carbo_key != "Included") or veg_key not in DATA["VEG"]:
            continue
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
        
        prot_options = list(DATA["PROT"].keys())
        # Protezione: se il valore nel DB non è una chiave valida, usa la prima
        current_prot = m["prot"] if m["prot"] in prot_options else prot_options[0]
        # --- SELETTORI ---
        new_p = st.selectbox(
            T["prot"], 
            options=prot_options, 
            index=list(DATA["PROT"].keys()).index(current_prot), 
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

        veg_options = list(DATA["VEG"].keys())
        current_veg = m["veg"] if m["veg"] in veg_options else veg_options[0]
        new_v = st.selectbox(
            T["veg"], 
            options=veg_options, 
            index=list(DATA["VEG"].keys()).index(current_veg), 
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

            if new_p == "Fish":
                st.caption(T["fish_tip_1"])
                st.caption(T["fish_tip_2"])
                
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

def render_myths_section(T):
    st.divider()

    st.write("---")
    st.markdown(T["title_myths"])
    st.caption(T["title_learn"])
    # Usiamo un popover per la sezione "nascosta"
    with st.popover("💡 Lo sapevi che?"):
        st.subheader(T["myths"])
        lang = st.session_state.lang
        
        # Selezioniamo 2 miti casuali dal database ogni volta che l'app gira
        # Usiamo min() per sicurezza, nel caso la lista fosse più corta di 2
        pool_miti = MYTHS_AND_CUR.get(lang, MYTHS_AND_CUR["IT"])
        random_myths = random.sample(pool_miti, min(2, len(pool_miti)))
        
        for myth in random_myths:
            with st.expander(f"🔍 {myth['titolo']}"):
                st.write(myth["testo"])
        
        st.caption(T["general_source"])

def render_app_content(user_id, user_email, T):
    # --- CARICAMENTO AUTOMATICO DATI (Solo la prima volta) ---
    if "loaded_for_user" not in st.session_state or st.session_state.loaded_for_user != user_id:
        profile, db_meals = load_user_data(user_id)
        if profile:
            st.session_state.n_people = profile.get('n_people', 2)
            st.session_state.piz = profile.get('pizza_enabled', True)
            # Se la lingua caricata è diversa da quella attuale, aggiornala
            if profile.get('default_lang') != st.session_state.lang:
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
        st.divider()
        if st.button(T["copy"], use_container_width=True):
            menu_string = get_menu_text_format(st.session_state.meals, T)
            # Mostriamo un'area di testo che l'utente può copiare facilmente
            st.code(menu_string, language="text")
            st.info(T["copy_info"])
            
        st.divider()
        st.subheader("💡 Tip of the day")
        # Scegliamo un consiglio random basato sulla lingua
        random_tip = random.choice(TIPS[st.session_state.lang])
        st.info(random_tip)
        
            
    # Caricamento iniziale pasti
    if not st.session_state.get("meals"):
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

    # --- MYTHS and CURIOSITY
    render_myths_section(T)

def init_session_state():
    """Inizializza tutte le variabili di stato necessarie all'avvio"""
    defaults = {
        "lang": "IT",
        "menu_version": 0,
        "swap_idx": None,
        "n_people": 2,
        "piz": True,
        "loaded_for_user": None, # Per gestire il caricamento dati da DB
        "meals": []              # Lista pasti vuota inizialmente
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# --- 4. APP ---
def main():
    st.set_page_config(page_title="Menu", layout="wide", page_icon="🥗")
    init_session_state()
    T = UI_TEXT[st.session_state.lang]
    
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
            st.markdown(f"#### {T['title']}")
            st.write(f"👤 **{user_email}**")
            if st.button(T["logout"], type="primary"):
                logout_user()
            st.divider()
            
        render_app_content(user_id, user_email, T)

if __name__ == "__main__": main()
