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
        "title": "Menù Settimanale", "settings": "⚙️ Impostazioni", "people": "Persone a tavola",
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
        "target_label": "Target", "menu_saved": "✅ Profilo e Menu salvati!", "cancel": "🚫 ANNULLA", "load_btn": "📥 CARICA PROFILO",
        "welcomeback": "Bentornato"
    },
    "EN": {
        "title": "Weekly Menu", "settings": "⚙️ Settings", "people": "People at the table",
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
        "target_label": "Target", "menu_saved": "✅ Profile & Menu saved!", "cancel": "🚫 CANCEL", "load_btn": "📥 LOAD PROFILE",
        "welcomeback": "Welcome Back"
    }
}

# --- 2. DATABASE ---
conn = st.connection(
    "supabase",
    type=SupabaseConnection,
    url=st.secrets["connections"]["supabase"]["url"],
    key=st.secrets["connections"]["supabase"]["key"]
)

def load_user_data(username):
    try:
        # 1. Carica il profilo
        res_prof = conn.table("profiles").select("*").eq("username", username).execute()

        if not res_prof.data or len(res_prof.data) == 0:
            return None, None

        profile = res_prof.data[0]
        
        # 2. Carica i pasti legati a quel profilo ID
        res_meals = conn.table("user_dinner").select("*").eq("profile_id", profile['id']).execute()
            
        meals = None
        if res_meals.data and len(res_meals.data) == 14:
            meals = sorted(res_meals.data, key=lambda x: (x['day_idx'], x['type'] == 'Dinner'))
            
        return profile, meals

    except Exception as e:
        st.error(f"Errore caricamento dati: {e}")
        return None, None

def save_all_data(username, n_people, pizza_on, meals): # al posto di save_db
    try:
        # 1. Upsert del profilo (Inserisce o aggiorna se lo username esiste)
        prof_data = {
            "username": username,
            "n_people": n_people,
            "pizza_enabled": pizza_on,
            "default_lang": st.session_state.lang
        }
        res_prof = conn.table("profiles").upsert(prof_data, on_conflict="username").execute()
        profile_id = res_prof.data[0]['id']

        # 2. Cancella e reinserisce i pasti
        conn.table("user_dinner").delete().eq("profile_id", profile_id).execute()
        
        to_insert = []
        for i, m in enumerate(meals):
            to_insert.append({
                "profile_id": profile_id,
                "day_idx": i // 2,
                "type": m["type"],
                "prot": m["prot"],
                "carbo": m["carbo"],
                "veg": m["veg"],
                "locked": m.get("locked", False)
            })
        conn.table("user_dinner").insert(to_insert).execute()
        st.success("Tutto salvato!")
    except Exception as e:
        st.error(f"Errore salvataggio: {e}")

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

# --- 4. APP ---
def main():
    st.set_page_config(page_title="Menu", layout="wide")

    # --- INIZIALIZZAZIONE STATO ---
    if "lang" not in st.session_state: st.session_state.lang = "IT"
    if "menu_version" not in st.session_state: st.session_state.menu_version = 0
    if "swap_idx" not in st.session_state: st.session_state.swap_idx = None
    if "n_people" not in st.session_state: st.session_state.n_people = 2
    if "piz" not in st.session_state: st.session_state.piz = True
    
    # Autenticazione
    user_input = st.sidebar.text_input("Inserisci il tuo Nome Utente", "guest")
         
    with st.sidebar:
        st.session_state.lang = st.radio("Language", ["IT", "EN"], horizontal=True)
        T = UI_TEXT[st.session_state.lang]
        st.header(T["settings"])

        if st.button(T["load_btn"], use_container_width=True):
            #st.write(f"--- Tentativo caricamento per: {user_input} ---")
            profile, db_meals = load_user_data(user_input)
            # st.write(f"DEBUG: Risultato query profilo: {profile}")
            if profile:
                # st.write("Esito: Profilo TROVATO")
                st.session_state.n_people = profile['n_people']
                st.session_state.piz = profile['pizza_enabled']
                st.session_state.lang = profile['default_lang']
                if db_meals:
                    st.session_state.meals = []
                    for m in db_meals:
                        st.session_state.meals.append({
                            "type": m["type"],
                            "prot": m["prot"],
                            "carbo": m["carbo"],
                            "veg": m["veg"],
                            "locked": m["locked"]
                        })
                    st.session_state.menu_version += 1
                    time.sleep(1)
                    st.toast(f"{T['welcomeback']} {user_input}!", icon="✅")
                    st.rerun()
                else:
                    st.sidebar.info("Profilo trovato, ma nessun pasto salvato.")
            else:
                # st.write("Esito: Profilo NON trovato")
                st.sidebar.warning(f"Errore: utente {user_input} non trovato")
                #st.toast(st.session_state.load_error, icon="❌")

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
            save_all_data(user_input, st.session_state.n_people, piz, st.session_state.meals)
            
    # Caricamento iniziale pasti
    if "meals" not in st.session_state:
        st.session_state.meals = generate_menu(st.session_state.piz)
        
    st.title(f"{T['title']} - {user_input}")

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
    for i, day_name in enumerate(T["days"]):
        with st.expander(f"📅 {day_name.upper()}"):
            cols = st.columns(2)
            for j in range(2):
                idx = i*2 + j
                m = st.session_state.meals[idx]
                v_key = st.session_state.menu_version

                is_swapping = (st.session_state.swap_idx == idx)
                active_swap = (st.session_state.swap_idx is not None)
                
                with cols[j].container(border=True):
                    st.write(f"**{T['lunch' if j==0 else 'dinner']}**" if st.session_state.swap_idx != idx else f"### {T['swap']}")
                    
                    # Selettori
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
                        new_c = st.selectbox(T["carb"], 
                                             c_opts, 
                                             index=c_idx if m["carbo"] in c_opts else 0, 
                                             format_func=lambda x: DATA["CARBO"][x][st.session_state.lang], 
                                             key=f"c{idx}_{v_key}",
                                             on_change=update_meal,
                                             args=(idx,)
                                            )
                    
                    new_v = st.selectbox(T["veg"], 
                                         list(DATA["VEG"].keys()), 
                                         index=list(DATA["VEG"].keys()).index(m["veg"]), 
                                         format_func=lambda x: DATA["VEG"][x][st.session_state.lang], 
                                         key=f"v{idx}_{v_key}",
                                         on_change=update_meal,
                                         args=(idx,)
                                        )

                    # Grammi dinamici
                    with st.expander(T["sugg"]):
                        g_p, g_c = DATA["PROT"][new_p]["gr"], DATA["CARBO"][new_c]["gr"]
                        u_p = "pz" if DATA["PROT"][new_p]["unit"] == "pz" else "g"
                        st.write(f"**{T['total']} {st.session_state.n_people}:**")
                        st.write(f"- {DATA['PROT'][new_p][st.session_state.lang]}: {g_p * st.session_state.n_people} {u_p}")
                        if g_c > 0: st.write(f"- {DATA['CARBO'][new_c][st.session_state.lang]}: {g_c * st.session_state.n_people} g")
                        st.write(f"- {T['veg']}: {200 * st.session_state.n_people} g")

                    # Swap & Lock
                    sl1, sl2 = st.columns(2)
                    m["locked"] = sl1.checkbox(T["lock"], m["locked"], key=f"lk{idx}_{v_key}")

                    if is_swapping:
                        btn_label = T["cancel"]
                        btn_type = "secondary"
                    elif active_swap:
                        btn_label = T["confirm"]
                        btn_type = "primary"
                    else:
                        btn_label = T["swap"]
                        btn_type = "secondary"

                    if sl2.button(btn_label, key=f"sw{idx}_{v_key}", use_container_width=True, type=btn_type):
                        if st.session_state.swap_idx is None:
                            # 1. Inizia lo scambio
                            st.session_state.swap_idx = idx
                            st.rerun()
                        elif is_swapping:
                            # 2. Annulla lo scambio
                            st.session_state.swap_idx = None
                            st.rerun()
                        else:
                            # 3. Esegui lo scambio tra idx e swap_idx
                            idx1, idx2 = st.session_state.swap_idx, idx
                            # Scambiamo i dati nel dizionario
                            st.session_state.meals[idx1], st.session_state.meals[idx2] = \
                            st.session_state.meals[idx2], st.session_state.meals[idx1]
                            # Reset stato scambio e incremento versione per refresh widget
                            st.session_state.swap_idx = None
                            st.session_state.menu_version += 1 
                            st.rerun()

    # --- SHOPPING LIST STILIZZATA ---
    st.divider()

    st.subheader(T['shop'])

    st.markdown(f"""
        <div style="
            background-color: #f0f2f6; 
            padding: 15px; 
            border-radius: 10px; 
            border-left: 5px solid #ff4b4b; 
            margin-bottom: 20px;
        ">
            <p style="
                margin: 0; 
                color: #31333f; 
                font-size: 16px;
            ">
                {T['shop_calc']} <b>{st.session_state.n_people}</b> {('persona' if st.session_state.n_people==1 else 'persone')}
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    basket = {}
    for m in st.session_state.meals:
        # Prot
        p_info = DATA["PROT"][m["prot"]]
        basket[p_info[st.session_state.lang]] = basket.get(p_info[st.session_state.lang], {"q": 0, "u": p_info["unit"]})
        basket[p_info[st.session_state.lang]]["q"] += p_info["gr"] * st.session_state.n_people
        # Carbo
        if m["carbo"] != "Included":
            c_info = DATA["CARBO"][m["carbo"]]
            basket[c_info[st.session_state.lang]] = basket.get(c_info[st.session_state.lang], {"q": 0, "u": "g"})
            basket[c_info[st.session_state.lang]]["q"] += c_info["gr"] * st.session_state.n_people
        # Veg
        v_name = DATA["VEG"][m["veg"]][st.session_state.lang]
        basket[v_name] = basket.get(v_name, {"q": 0, "u": "g"})
        basket[v_name]["q"] += 200 * st.session_state.n_people

    c1, c2 = st.columns(2)
    items = list(basket.items())
    for i, (name, info) in enumerate(items):
        col = c1 if i < len(items)/2 else c2
        q, u = info["q"], info["u"]
        val = f"{q/1000:.2f} Kg" if (u=="g" and q>=1000) else f"{q} {u}"
        col.write(f"- **{name}**: {val}")

if __name__ == "__main__": main()
