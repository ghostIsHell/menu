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
        # --- WINTER ---
        "Broccoli":      {"IT": "🥦 Broccoli",      "EN": "🥦 Broccoli",      "seasons": ["winter", "autumn"]},
        "Cauliflower":   {"IT": "🥦 Cavolfiore",     "EN": "🥦 Cauliflower",   "seasons": ["winter", "autumn"]},
        "Fennel":        {"IT": "🥗 Finocchi",        "EN": "🥗 Fennel",        "seasons": ["winter", "autumn"]},
        "Spinach":       {"IT": "🍃 Spinaci",         "EN": "🍃 Spinach",       "seasons": ["winter", "spring"]},
        "Chard":         {"IT": "🍃 Bietole",         "EN": "🍃 Chard",         "seasons": ["winter", "spring"]},
        "Artichokes":    {"IT": "🎍 Carciofi",        "EN": "🎍 Artichokes",    "seasons": ["winter", "spring"]},
        "Pumpkin":       {"IT": "🎃 Zucca",           "EN": "🎃 Pumpkin",       "seasons": ["winter", "autumn"]},
        "Cabbage":       {"IT": "🥬 Cavolo",          "EN": "🥬 Cabbage",       "seasons": ["winter"]},
        "Leeks":         {"IT": "🌿 Porri",           "EN": "🌿 Leeks",         "seasons": ["winter", "autumn"]},
        # --- SPRING ---
        "Asparagus":     {"IT": "🎋 Asparagi",        "EN": "🎋 Asparagus",     "seasons": ["spring"]},
        "Radishes":      {"IT": "🌸 Ravanelli",       "EN": "🌸 Radishes",      "seasons": ["spring"]},
        # --- SUMMER ---
        "Zucchini":      {"IT": "🥒 Zucchine",        "EN": "🥒 Zucchini",      "seasons": ["summer", "spring"]},
        "Tomatoes":      {"IT": "🍅 Pomodori",         "EN": "🍅 Tomatoes",      "seasons": ["summer"]},
        "Peppers":       {"IT": "🫑 Peperoni",         "EN": "🫑 Peppers",       "seasons": ["summer"]},
        "Eggplants":     {"IT": "🍆 Melanzane",        "EN": "🍆 Eggplants",     "seasons": ["summer"]},
        "Cucumbers":     {"IT": "🥒 Cetrioli",         "EN": "🥒 Cucumbers",     "seasons": ["summer"]},
        "Green Beans":   {"IT": "🥗 Fagiolini",        "EN": "🥗 Green Beans",   "seasons": ["summer", "spring"]},
        # --- ALL YEAR ---
        "Salad":         {"IT": "🥬 Insalata",         "EN": "🥬 Salad",         "seasons": ["winter", "spring", "summer", "autumn"]},
        "Mushrooms":     {"IT": "🍄 Funghi",           "EN": "🍄 Mushrooms",     "seasons": ["winter", "spring", "summer", "autumn"]},
        "Carrot":        {"IT": "🥕 Carote",           "EN": "🥕 Carrots",       "seasons": ["winter", "spring", "summer", "autumn"]},
    },
        "LEGUMES_SIDE": {
        "Peas":          {"IT": "🫛 Piselli",          "EN": "🫛 Peas",          "seasons": ["spring"]},
        "Broad Beans":   {"IT": "🫛 Fave",             "EN": "🫛 Broad Beans",   "seasons": ["spring"]},
        "Chickpeas":     {"IT": "🫘 Ceci",             "EN": "🫘 Chickpeas",     "seasons": ["winter", "spring", "summer", "autumn"]},
        "Lentils":       {"IT": "🫘 Lenticchie",       "EN": "🫘 Lentils",       "seasons": ["winter", "autumn"]},
        "Cannellini":    {"IT": "🫘 Cannellini",       "EN": "🫘 Cannellini",    "seasons": ["winter", "spring", "summer", "autumn"]},
    },
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
        "myths": "🍬 Miti", "curiosity": "🔬 Curiosità", "title_learn": "C'è sempre qualcosa di nuovo da imparare...", "know_it": "💡 Lo sapevi che?"
    
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
        "myths": "🍬 Miths", "curiosities": "🔬 Curiosità", "title_learn": "There's always something new to learn...", "know_it": "💡 Did you know?"
    }
}

# --- CREA 2018 BASED CONTENT ---

TIPS = {
    "IT": [
        # Direttiva 1 - Peso e attività fisica
        "Mantieni un peso corporeo nella norma: il sovrappeso aumenta il rischio di malattie cardiovascolari, diabete e alcuni tumori. (CREA 2018)",
        "Svolgi almeno 30 minuti di attività fisica moderata ogni giorno: anche una camminata veloce conta! (CREA 2018)",
        "Non saltare i pasti: aiuta a controllare la fame e riduce il rischio di abbuffate. (CREA 2018)",
        # Direttiva 2 - Frutta e verdura
        "Consuma almeno 5 porzioni al giorno tra frutta e verdura, variando i colori: ogni colore corrisponde a nutrienti diversi. (CREA 2018)",
        "Preferisci frutta e verdura di stagione: sono più nutrienti, più saporite e costano meno. (CREA 2018)",
        "Mangia la frutta intera piuttosto che come succo: mantieni le fibre e senti più sazietà. (CREA 2018)",
        # Direttiva 3 - Cereali integrali e legumi
        "Sostituisci i cereali raffinati con quelli integrali: pasta, riso e pane integrali apportano più fibre e saziano meglio. (CREA 2018)",
        "Consuma legumi almeno 3-4 volte a settimana: sono un'ottima fonte proteica, economica e sostenibile. (CREA 2018)",
        "I legumi possono sostituire la carne come fonte proteica in un pasto principale: prova pasta e fagioli o zuppa di lenticchie. (CREA 2018)",
        # Direttiva 4 - Acqua
        "Bevi almeno 1,5-2 litri di acqua al giorno, preferibilmente lontano dai pasti. Non aspettare di avere sete! (CREA 2018)",
        "L'acqua è la bevanda ideale: non apporta calorie e idrata in modo ottimale. Evita le bevande zuccherate. (CREA 2018)",
        # Direttiva 5 - Grassi
        "Usa l'olio extravergine d'oliva come condimento principale: è ricco di acidi grassi monoinsaturi protettivi, ma attento alle quantità (1-2 cucchiai a pasto). (CREA 2018)",
        "Limita i grassi saturi (burro, lardo, carni grasse): aumentano il colesterolo LDL e il rischio cardiovascolare. (CREA 2018)",
        "Il pesce azzurro (sgombro, sardine, alici) è ricco di omega-3: consumalo almeno 2-3 volte a settimana. (CREA 2018)",
        # Direttiva 6 - Zuccheri
        "Gli zuccheri aggiunti non dovrebbero superare il 10-15% delle calorie giornaliere totali. Leggi le etichette! (CREA 2018)",
        "Riduci le bevande zuccherate: una lattina di cola contiene circa 35g di zucchero, quasi tutta la quota giornaliera. (CREA 2018)",
        # Direttiva 7 - Sale
        "Riduci il sale a meno di 5g al giorno: usa erbe aromatiche, limone e spezie per insaporire. (CREA 2018)",
        "Fai attenzione al sale 'nascosto' negli alimenti processati: salumi, formaggi stagionati, pane, snack. (CREA 2018)",
        # Direttiva 8 - Alcol
        "Se consumi alcol, non superare 1 unità alcolica al giorno per le donne, 2 per gli uomini. L'ideale sarebbe zero. (CREA 2018)",
        "L'alcol è calorico e privo di nutrienti: 1g apporta 7 kcal, quasi quanto i grassi. (CREA 2018)",
        # Direttiva 9 - Varietà
        "Varia il più possibile la tua alimentazione: nessun alimento da solo contiene tutti i nutrienti necessari. (CREA 2018)",
        "Non esistono alimenti 'miracolosi' né 'superfood': la chiave è la varietà e l'equilibrio nel tempo. (CREA 2018)",
        # Direttiva 13 - Sostenibilità
        "Una dieta ricca di legumi, verdure e cereali integrali fa bene a te e all'ambiente: riduce le emissioni di CO2. (CREA 2018)",
        "Riduci gli sprechi alimentari: pianifica i pasti, fai una lista della spesa e conserva correttamente gli alimenti. (CREA 2018)",
    ],
    "EN": [
        "Maintain a normal body weight: overweight increases the risk of cardiovascular disease, diabetes and some cancers. (CREA 2018)",
        "Get at least 30 minutes of moderate physical activity every day: even a brisk walk counts! (CREA 2018)",
        "Don't skip meals: it helps control hunger and reduces the risk of overeating. (CREA 2018)",
        "Eat at least 5 portions of fruit and vegetables a day, varying the colours: each colour provides different nutrients. (CREA 2018)",
        "Prefer seasonal fruit and vegetables: they are more nutritious, tastier and cheaper. (CREA 2018)",
        "Eat whole fruit rather than juice: you keep the fibre and feel fuller for longer. (CREA 2018)",
        "Replace refined grains with whole grains: wholemeal pasta, rice and bread provide more fibre and are more satiating. (CREA 2018)",
        "Eat legumes at least 3-4 times a week: they are an excellent, affordable and sustainable protein source. (CREA 2018)",
        "Legumes can replace meat as a protein source in a main meal: try pasta e fagioli or lentil soup. (CREA 2018)",
        "Drink at least 1.5-2 litres of water a day, preferably between meals. Don't wait until you're thirsty! (CREA 2018)",
        "Water is the ideal drink: it has no calories and hydrates optimally. Avoid sugary drinks. (CREA 2018)",
        "Use extra virgin olive oil as your main condiment: it is rich in protective monounsaturated fatty acids, but watch the quantities (1-2 tablespoons per meal). (CREA 2018)",
        "Limit saturated fats (butter, lard, fatty meats): they raise LDL cholesterol and cardiovascular risk. (CREA 2018)",
        "Oily fish (mackerel, sardines, anchovies) is rich in omega-3: eat it at least 2-3 times a week. (CREA 2018)",
        "Added sugars should not exceed 10-15% of total daily calories. Read labels! (CREA 2018)",
        "Cut back on sugary drinks: a can of cola contains about 35g of sugar, almost the entire daily allowance. (CREA 2018)",
        "Reduce salt to less than 5g a day: use herbs, lemon and spices for flavour instead. (CREA 2018)",
        "Watch out for 'hidden' salt in processed foods: cured meats, aged cheeses, bread, snacks. (CREA 2018)",
        "If you drink alcohol, don't exceed 1 unit per day for women, 2 for men. Zero is ideal. (CREA 2018)",
        "Alcohol is calorie-dense and nutrient-free: 1g provides 7 kcal, almost as much as fat. (CREA 2018)",
        "Vary your diet as much as possible: no single food contains all the nutrients you need. (CREA 2018)",
        "There are no 'miracle' foods or 'superfoods': the key is variety and balance over time. (CREA 2018)",
        "A diet rich in legumes, vegetables and whole grains is good for you and the planet: it reduces CO2 emissions. (CREA 2018)",
        "Reduce food waste: plan your meals, make a shopping list and store food correctly. (CREA 2018)",
    ]
}

MYTHS_AND_CUR = {
    "IT": [
        # Grassi
        {"titolo": "🧈 Il burro fa meno male dell'olio", "testo": "Falso. Il burro è ricco di grassi saturi che aumentano il colesterolo LDL. L'olio EVO, ricco di grassi monoinsaturi, è molto più protettivo per il cuore. (CREA 2018 - Direttiva 5)"},
        {"titolo": "🥑 I grassi fanno ingrassare", "testo": "Non tutti i grassi sono uguali. I grassi insaturi (olio d'oliva, frutta secca, pesce) sono essenziali e protettivi. Fa ingrassare l'eccesso calorico totale, non un singolo nutriente. (CREA 2018 - Direttiva 5)"},
        {"titolo": "🐟 Il pesce sott'olio non vale come il fresco", "testo": "Il tonno e il salmone in scatola mantengono buone proprietà nutrizionali. Preferisci quelli al naturale e limita a 1 volta/settimana quelli sott'olio (50g sgocciolati). (CREA 2018 - Direttiva 5)"},
        # Zuccheri
        {"titolo": "🍯 Il miele è più sano dello zucchero", "testo": "Pur avendo qualche micronutriente in più, il miele è comunque uno zucchero aggiunto da consumare con moderazione. La differenza calorica è minima. (CREA 2018 - Direttiva 6)"},
        {"titolo": "🧃 I succhi di frutta sono sani come la frutta", "testo": "Falso. I succhi perdono le fibre, saziano meno e contengono comunque zuccheri liberi (8-10%). Un bicchiere = circa 70 kcal di zuccheri. Meglio mangiare la frutta intera. (CREA 2018 - Direttiva 6)"},
        {"titolo": "🍬 Lo zucchero di canna fa meno male", "testo": "La differenza nutrizionale è trascurabile. Il colore scuro dipende solo dalla melassa residua. Entrambi sono zuccheri aggiunti da limitare. (CREA 2018 - Direttiva 6)"},
        {"titolo": "🍭 Lo zucchero rende iperattivi i bambini", "testo": "Studi scientifici approfonditi hanno smentito questa credenza. Non esiste una relazione causale tra saccarosio e iperattività nei bambini. (CREA 2018 - Direttiva 6)"},
        # Sale
        {"titolo": "🧂 Il sale rosa dell'Himalaya è più sano", "testo": "Contiene le stesse quantità di sodio del comune sale da cucina. Le tracce di minerali aggiuntivi sono irrilevanti ai fini nutrizionali. Va limitato esattamente come il sale normale. (CREA 2018 - Direttiva 7)"},
        {"titolo": "🧂 Cucinare senza sale rende il cibo insapore", "testo": "Il palato si adatta in poche settimane. Erbe aromatiche, spezie, aglio, limone e aceto permettono di ottenere piatti saporiti e salutari. (CREA 2018 - Direttiva 7)"},
        # Proteine
        {"titolo": "🥩 Bisogna mangiare carne tutti i giorni per avere proteine", "testo": "Falso. Legumi, uova, pesce, latticini e anche cereali integrali contribuiscono al fabbisogno proteico. La dieta mediterranea prevede carne poche volte a settimana. (CREA 2018 - Direttiva 3)"},
        {"titolo": "🫘 I legumi fanno gonfiare e sono difficili da digerire", "testo": "Ammollo prolungato, cottura adeguata e l'aggiunta di erbe (alloro, rosmarino) riducono significativamente il gonfiore. Chi li consuma regolarmente li tollera meglio. (CREA 2018 - Direttiva 3)"},
        {"titolo": "🥚 Le uova fanno aumentare il colesterolo", "testo": "Le evidenze scientifiche attuali mostrano che un consumo moderato di uova (fino a 4 a settimana) non è problematico per la maggior parte delle persone sane. (CREA 2018 - Direttiva 9)"},
        # Cereali
        {"titolo": "🍞 Il pane fa ingrassare", "testo": "Il pane, specie se integrale, è una fonte importante di carboidrati complessi, fibre e vitamine del gruppo B. Fa ingrassare l'eccesso calorico totale, non il pane in sé. (CREA 2018 - Direttiva 3)"},
        {"titolo": "🌾 Il glutine fa male a tutti", "testo": "Il glutine è problematico solo per celiaci (circa 1% della popolazione) e per chi ha sensibilità accertata. Per tutti gli altri, i cereali integrali contenenti glutine sono alimenti sani e consigliati. (CREA 2018 - Direttiva 3)"},
        # Diete e integratori
        {"titolo": "💊 Gli integratori sostituiscono una dieta sana", "testo": "Gli integratori possono essere utili in caso di carenze accertate, ma non sostituiscono mai una dieta varia ed equilibrata. La matrice alimentare è irriducibile a una pillola. (CREA 2018 - Direttiva 11)"},
        {"titolo": "🥗 Le diete drastiche funzionano meglio", "testo": "Le diete drastiche causano perdita di massa muscolare, effetto yo-yo e carenze nutrizionali. Un calo di 0,5-1 kg a settimana è fisiologico e mantenibile. (CREA 2018 - Direttiva 11)"},
        {"titolo": "🌟 Esistono i 'superfood'", "testo": "Nessun alimento singolo può supplire a una dieta sbilanciata. Il concetto di 'superfood' è prevalentemente di marketing. La varietà è l'unico vero 'super' approccio. (CREA 2018 - Direttiva 11)"},
        # Sostenibilità
        {"titolo": "🌍 Mangiare sano costa troppo", "testo": "Una dieta mediterranea basata su legumi, cereali integrali, frutta e verdura di stagione è tra le diete più economiche. La carne è spesso la voce di spesa più alta. (CREA 2018 - Direttiva 13)"},
    ],
    "EN": [
        {"titolo": "🧈 Butter is healthier than oil", "testo": "False. Butter is rich in saturated fats that raise LDL cholesterol. Extra virgin olive oil, rich in monounsaturated fats, is much more protective for the heart. (CREA 2018 - Directive 5)"},
        {"titolo": "🥑 Fat makes you fat", "testo": "Not all fats are equal. Unsaturated fats (olive oil, nuts, fish) are essential and protective. What causes weight gain is a total calorie surplus, not a single nutrient. (CREA 2018 - Directive 5)"},
        {"titolo": "🐟 Canned fish is not as good as fresh", "testo": "Canned tuna and salmon retain good nutritional properties. Prefer those in water, and limit oil-packed versions to once a week (50g drained). (CREA 2018 - Directive 5)"},
        {"titolo": "🍯 Honey is healthier than sugar", "testo": "Although it has slightly more micronutrients, honey is still an added sugar to be consumed in moderation. The calorie difference is minimal. (CREA 2018 - Directive 6)"},
        {"titolo": "🧃 Fruit juices are as healthy as fruit", "testo": "False. Juices lose fibre, are less filling and still contain free sugars (8-10%). One glass ≈ 70 kcal of sugar. Better to eat whole fruit. (CREA 2018 - Directive 6)"},
        {"titolo": "🍬 Brown sugar is less harmful", "testo": "The nutritional difference is negligible. The dark colour comes only from residual molasses. Both are added sugars to be limited. (CREA 2018 - Directive 6)"},
        {"titolo": "🍭 Sugar makes children hyperactive", "testo": "In-depth scientific studies have debunked this belief. There is no causal link between sucrose and hyperactivity in children. (CREA 2018 - Directive 6)"},
        {"titolo": "🧂 Himalayan pink salt is healthier", "testo": "It contains the same amount of sodium as regular table salt. The additional mineral traces are nutritionally irrelevant. It should be limited just like normal salt. (CREA 2018 - Directive 7)"},
        {"titolo": "🧂 Cooking without salt makes food tasteless", "testo": "The palate adapts within a few weeks. Herbs, spices, garlic, lemon and vinegar can make food tasty and healthy. (CREA 2018 - Directive 7)"},
        {"titolo": "🥩 You need to eat meat every day for protein", "testo": "False. Legumes, eggs, fish, dairy and even wholegrains contribute to protein needs. The Mediterranean diet includes meat only a few times a week. (CREA 2018 - Directive 3)"},
        {"titolo": "🫘 Legumes cause bloating and are hard to digest", "testo": "Prolonged soaking, proper cooking and adding herbs (bay leaf, rosemary) significantly reduce bloating. Those who eat them regularly tolerate them better. (CREA 2018 - Directive 3)"},
        {"titolo": "🥚 Eggs raise cholesterol", "testo": "Current scientific evidence shows that moderate egg consumption (up to 4 per week) is not problematic for most healthy people. (CREA 2018 - Directive 9)"},
        {"titolo": "🍞 Bread makes you fat", "testo": "Bread, especially wholemeal, is an important source of complex carbohydrates, fibre and B vitamins. It is total calorie excess that causes weight gain, not bread itself. (CREA 2018 - Directive 3)"},
        {"titolo": "🌾 Gluten is harmful for everyone", "testo": "Gluten is only problematic for coeliacs (about 1% of the population) and those with confirmed sensitivity. For everyone else, gluten-containing wholegrains are healthy and recommended. (CREA 2018 - Directive 3)"},
        {"titolo": "💊 Supplements replace a healthy diet", "testo": "Supplements can be useful for confirmed deficiencies, but never replace a varied, balanced diet. The food matrix cannot be reduced to a pill. (CREA 2018 - Directive 11)"},
        {"titolo": "🥗 Drastic diets work better", "testo": "Drastic diets cause muscle loss, yo-yo effect and nutritional deficiencies. A loss of 0.5-1 kg per week is physiological and sustainable. (CREA 2018 - Directive 11)"},
        {"titolo": "🌟 Superfoods exist", "testo": "No single food can compensate for an unbalanced diet. The 'superfood' concept is largely marketing. Variety is the only truly 'super' approach. (CREA 2018 - Directive 11)"},
        {"titolo": "🌍 Eating healthy is too expensive", "testo": "A Mediterranean diet based on legumes, whole grains, seasonal fruit and vegetables is among the most affordable diets. Meat is often the biggest food expense. (CREA 2018 - Directive 13)"},
    ]
}

CURIOSITIES = {
    "IT": [
        {"titolo": "🫒 Olio EVO e cottura", "testo": "L'olio extravergine d'oliva è più stabile al calore di quanto si creda: il suo punto di fumo (≈180°C) lo rende adatto anche alla cottura. Evita però di surriscaldarlo. (CREA 2018)"},
        {"titolo": "🫘 Legumi = carne vegetale", "testo": "100g di lenticchie secche contengono circa 25g di proteine, paragonabili a molte fonti animali, con il vantaggio di apportare fibre e zero colesterolo. (CREA 2018)"},
        {"titolo": "🥦 Cottura e nutrienti", "testo": "Alcune verdure (carote, pomodori) rilasciano più antiossidanti se cotte. Altre (broccoli, peperoni) perdono vitamina C con il calore. Varia metodo e verdure! (CREA 2018)"},
        {"titolo": "🍅 Il licopene del pomodoro", "testo": "Il licopene, potente antiossidante del pomodoro, è meglio assorbito dal corpo quando il pomodoro è cotto e condito con olio. La salsa di pomodoro è più 'funzionale' del pomodoro crudo! (CREA 2018)"},
        {"titolo": "🌾 Fibra e microbiota", "testo": "Le fibre dei cereali integrali e dei legumi nutrono il microbiota intestinale (i batteri 'buoni'), che a sua volta protegge dalla infiammazione cronica e rafforza il sistema immunitario. (CREA 2018)"},
        {"titolo": "🐟 Omega-3 e cervello", "testo": "Gli acidi grassi omega-3 del pesce azzurro sono fondamentali per il funzionamento cerebrale e la prevenzione della depressione. Il DHA è il principale grasso del cervello umano. (CREA 2018)"},
        {"titolo": "🍊 Vitamina C e ferro", "testo": "Consumare alimenti ricchi di vitamina C (agrumi, peperoni) insieme a fonti di ferro vegetale (legumi, spinaci) ne migliora notevolmente l'assorbimento. (CREA 2018)"},
        {"titolo": "💧 Acqua e metabolismo", "testo": "Una corretta idratazione migliora il metabolismo, la concentrazione e la performance fisica. Anche una leggera disidratazione (1-2%) riduce le capacità cognitive. (CREA 2018)"},
        {"titolo": "🧄 Aglio e salute cardiovascolare", "testo": "L'aglio contiene allicina, un composto con proprietà antibatteriche e cardioprotettive. È una delle spezie più studiate per i benefici sulla pressione sanguigna. (CREA 2018)"},
        {"titolo": "🫐 I polifenoli della frutta", "testo": "I polifenoli di frutti come mirtilli, melograno e uva nera hanno potenti proprietà antiossidanti e antinfiammatorie. La diversità di colori nella frutta è la chiave! (CREA 2018)"},
    ],
    "EN": [
        {"titolo": "🫒 Olive oil and cooking", "testo": "Extra virgin olive oil is more heat-stable than commonly believed: its smoke point (≈180°C) makes it suitable for cooking too. Just avoid overheating it. (CREA 2018)"},
        {"titolo": "🫘 Legumes = plant-based meat", "testo": "100g of dried lentils contain about 25g of protein, comparable to many animal sources, with the added benefit of fibre and zero cholesterol. (CREA 2018)"},
        {"titolo": "🥦 Cooking and nutrients", "testo": "Some vegetables (carrots, tomatoes) release more antioxidants when cooked. Others (broccoli, peppers) lose vitamin C with heat. Vary both method and vegetables! (CREA 2018)"},
        {"titolo": "🍅 Lycopene in tomatoes", "testo": "Lycopene, the powerful antioxidant in tomatoes, is better absorbed by the body when tomatoes are cooked and dressed with oil. Tomato sauce is more 'functional' than raw tomato! (CREA 2018)"},
        {"titolo": "🌾 Fibre and the microbiome", "testo": "Fibres from wholegrains and legumes feed the gut microbiome (the 'good' bacteria), which in turn protects against chronic inflammation and strengthens the immune system. (CREA 2018)"},
        {"titolo": "🐟 Omega-3 and the brain", "testo": "The omega-3 fatty acids in oily fish are essential for brain function and depression prevention. DHA is the main fat in the human brain. (CREA 2018)"},
        {"titolo": "🍊 Vitamin C and iron", "testo": "Eating vitamin C-rich foods (citrus fruits, peppers) alongside plant-based iron sources (legumes, spinach) significantly improves iron absorption. (CREA 2018)"},
        {"titolo": "💧 Water and metabolism", "testo": "Proper hydration improves metabolism, concentration and physical performance. Even mild dehydration (1-2%) reduces cognitive abilities. (CREA 2018)"},
        {"titolo": "🧄 Garlic and cardiovascular health", "testo": "Garlic contains allicin, a compound with antibacterial and cardioprotective properties. It is one of the most studied spices for its blood pressure benefits. (CREA 2018)"},
        {"titolo": "🫐 Polyphenols in fruit", "testo": "Polyphenols in fruits like blueberries, pomegranate and black grapes have powerful antioxidant and anti-inflammatory properties. Colour diversity in fruit is the key! (CREA 2018)"},
    ]
}

SEASON_LABELS = {
    "IT": {"winter": "❄️ Inverno", "spring": "🌸 Primavera", "summer": "☀️ Estate", "autumn": "🍂 Autunno"},
    "EN": {"winter": "❄️ Winter",  "spring": "🌸 Spring",    "summer": "☀️ Summer",  "autumn": "🍂 Autumn"},
}

def get_supabase_client():
    if "supabase_client" not in st.session_state:
        from supabase import create_client
        url = st.secrets["connections"]["supabase"]["url"]
        key = st.secrets["connections"]["supabase"]["key"]
        st.session_state.supabase_client = create_client(url, key)
    return st.session_state.supabase_client

def get_current_season():
    month = datetime.now().month
    if month in [12, 1, 2]:   return "winter"
    elif month in [3, 4, 5]:  return "spring"
    elif month in [6, 7, 8]:  return "summer"
    else:                     return "autumn"

def render_season_selector():
    lang = st.session_state.lang
    season_options = ["winter", "spring", "summer", "autumn"]

    translated_options = [SEASON_LABELS[lang][s] for s in season_options]

    current_idx = season_options.index(st.session_state.season)
        
    selected_label  = st.selectbox(
        "🌍 " + ("Stagione" if lang == "IT" else "Season"),
        options=translated_options,
        index=current_idx,
        key=f"season_selector_{lang}"
    )
    
    selected_idx = translated_options.index(selected_label)
    st.session_state.season = season_options[selected_idx]
    
    auto = get_current_season()
    if st.session_state.season != auto:
        st.caption(f"⚠️ Auto: {SEASON_LABELS[lang][auto]}")
    
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
    conn = get_supabase_client()
    try:
        res = conn.auth.sign_in_with_password({"email": email, "password": password})
        if res.session:
            # Persist the token so we can restore it after a full page refresh
            st.session_state.user = res.user
            st.session_state.access_token = res.session.access_token
            st.session_state.refresh_token = res.session.refresh_token
        return res
    except Exception as e:
        st.error(f"Login Error: {e}")
        return None

# Funzione per la Registrazione
def signup_user(email, password, T):
    conn = get_supabase_client()
    try:
        res = conn.auth.sign_up({"email": email, "password": password})
        st.success(T['succes_reg'])
        return res
    except Exception as e:
        st.error(f"Registration Error: {e}")
        return None

# Funzione per il Logout
def logout_user():
    conn = get_supabase_client()
    try:
        conn.auth.sign_out()
    except:
        pass
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()  # ← only once, nothing after this runs anyway
    
def load_user_data(user_id):
    conn = get_supabase_client()
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
    conn = get_supabase_client()
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
                "legume_side": m.get("legume_side"),
                "locked": m.get("locked", False)
            })
        conn.table("user_dinner").insert(to_insert).execute()
        st.success(T['saved'])
    except Exception as e:
        st.error(f"Save Error: {e}")

# --- 3. LOGICA GENERAZIONE ---
def generate_menu(pizza_on, current_meals=None):
    season = st.session_state.get("season", get_current_season())

    # Seasonal vegetable pool
    seasonal_veg = [k for k, v in DATA["VEG"].items() if season in v["seasons"]]
    if not seasonal_veg:
        seasonal_veg = list(DATA["VEG"].keys())

    # Seasonal legume side pool
    seasonal_leg_side = [k for k, v in DATA["LEGUMES_SIDE"].items() if season in v["seasons"]]
    if not seasonal_leg_side:
        seasonal_leg_side = list(DATA["LEGUMES_SIDE"].keys())
    
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
    
    for k, v in targets.items():
        pool.extend([k] * v)
    random.shuffle(pool)

    # Legume side: assign to ~3 meals where protein is NOT already legumes
    # We'll decide per-meal after protein assignment
    leg_side_budget = 3  # times per week as side dish
    
    meals = []
    leg_side_used = 0
    
    for i in range(14):
        if current_meals and current_meals[i].get("locked"):
            meals.append(current_meals[i])
            if current_meals[i].get("legume_side"):
                leg_side_used += 1
            continue
        is_lunch = i % 2 == 0
        # --- PROTEIN ---
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

        # --- CARBO ---

        if p in ["Pizza", "One-Pot Meal"]: 
            c = "Included"
        else: 
            c = random.choice(
                ["Whole Grain Pasta", "Brown Rice", "Spelt", "Barley", "Gnocchi"] 
                if is_lunch else 
                ["Whole Grain Bread", "Potatoes", "Whole Grain Couscous"]
            )
            
        # --- VEGETABLE (seasonal) ---
        # --- VERDURA CON VINCOLI DECRESCENTI ---
        v = None
        for window_size in [3, 2, 1]:
            recent_vegs = [m["veg"] for m in meals[-window_size:]] if i > 0 else []
            available_veg = [veg for veg in seasonal_veg if veg not in recent_vegs]
            if available_veg:
                v = random.choice(available_veg)
                break
        if not v: 
            v = random.choice(seasonal_veg)

        # --- LEGUME SIDE (optional, not if protein is already legumes) ---
        legume_side = None
        if leg_side_used < leg_side_budget and p != "Legumes" and random.random() < 0.4:
            legume_side = random.choice(seasonal_leg_side)
            leg_side_used += 1
        
        meals.append({
            "type": "Lunch" if is_lunch else "Dinner",
            "prot": p, "carbo": c, "veg": v,
            "legume_side": legume_side,
            "locked": False
        })
    return meals

# --- UPDATED: format_func for vegetable selectboxes (with ⚠️ for out-of-season) ---
def veg_label(key, lang):
    season = st.session_state.get("season", get_current_season())
    info = DATA["VEG"][key]
    label = info[lang]
    if season not in info["seasons"]:
        label = f"⚠️ {label}"
    return label
    
def legume_side_label(key, lang):
    season = st.session_state.get("season", get_current_season())
    info = DATA["LEGUMES_SIDE"][key]
    label = info[lang]
    #if season not in info["seasons"]:
    #    label = f"⚠️ {label}"
    return label

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

        # ✅ Only show legume side if protein is NOT already Legumes
        if new_p == "Legumes":
            # Legume side dish (optional)
            leg_side_options = ["None"] + list(DATA["LEGUMES_SIDE"].keys())
            current_leg = m.get("legume_side") or "None"
            if current_leg not in leg_side_options:
                current_leg = "None"

            new_leg = st.selectbox(
                "🫘 " + ("Legume (contorno)" if st.session_state.lang == "IT" else "Legume (side)"),
                options=leg_side_options,
                index=leg_side_options.index(current_leg),
                format_func=lambda x: "—" if x == "None" else legume_side_label(x, st.session_state.lang),
                key=f"leg{idx}_{v_key}",
                on_change=update_meal,
                args=(idx,)
            )
            # Store it back (update_meal handles prot/carbo/veg, add legume_side here)
            st.session_state.meals[idx]["legume_side"] = None if new_leg == "None" else new_leg
        else:
            # Clear any previously set legume side if protein switched to Legumes
            st.session_state.meals[idx]["legume_side"] = None

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
    lang = st.session_state.lang

    st.write("---")
    st.markdown(T["title_myths"])
    st.caption(T["title_learn"])
    # Usiamo un popover per la sezione "nascosta"
    with st.popover(T["know_it"]):
        tab_myths, tab_cur = st.tabs([
            T["myths"],
            T["curiosities"]
        ])

        with tab_myths:
            st.caption(T["general_source"])
            pool = MYTHS_AND_CUR.get(lang, MYTHS_AND_CUR["IT"])
            for myth in random.sample(pool, min(3, len(pool))):
                with st.expander(myth["titolo"]):
                    st.write(myth["testo"])

        with tab_cur:
            st.caption(T["general_source"])
            pool = CURIOSITIES.get(lang, CURIOSITIES["IT"])
            for cur in random.sample(pool, min(3, len(pool))):
                with st.expander(cur["titolo"]):
                    st.write(cur["testo"])

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
                    "legume_side": m.get("legume_side"),
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

        render_season_selector()

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
    defaults = {
        "lang": "IT",
        "menu_version": 0,
        "swap_idx": None,
        "n_people": 2,
        "piz": True,
        "loaded_for_user": None,
        "meals": [],
        "season": get_current_season()
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# --- 4. APP ---
def main(): 
    st.set_page_config(page_title="Menu", layout="wide", page_icon="🥗")
    init_session_state()
    T = UI_TEXT[st.session_state.lang]

    if "user" not in st.session_state or st.session_state.user is None:
        if "access_token" in st.session_state:
            try:
                conn = get_supabase_client()
                # Restore the session from stored tokens
                res = conn.auth.set_session(
                    st.session_state.access_token,
                    st.session_state.refresh_token
                )
                if res.user:
                    st.session_state.user = res.user
                else:
                    st.session_state.user = None
            except:
                st.session_state.user = None
        else:
            st.session_state.user = None
    
    if st.session_state.user is None:
        render_auth_screen()
    else:
        user_id = st.session_state.user.id
        user_email = st.session_state.user.email
                
        # Sidebar con Logout e Info Utente
        with st.sidebar:
            st.markdown(f"#### {T['title']}")
            st.write(f"👤 **{user_email}**")
            if st.button(T["logout"], type="primary"):
                logout_user()
            st.divider()
            
        render_app_content(user_id, user_email, T)

if __name__ == "__main__": main()
