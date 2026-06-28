import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests
from datetime import datetime, timedelta

# --- 🎨 TUNING IFORTUNA.CZ + FONT ROBOTO ---
st.set_page_config(page_title="MS 2026 - Tipovačka", page_icon="⚽", layout="centered")

st.markdown("""
    <style>
    /* IMPORT EXKLUZIVNÍCH FONTŮ Z GOOGLE FONTS (STAATLICHES + ROBOTO) */
    @import url('https://fonts.googleapis.com/css2?family=Staatliches&family=Roboto:wght=400;500;700&display=swap');

    /* 1. GLOBÁLNÍ VYNUCENÍ TMÁVÉHO FORTUNA DESIGNU */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stAppViewBlockContainer"] {
        background-color: #121212 !important; /* Hluboká černá Fortuny */
        color: #FFFFFF !important;
        font-family: 'Roboto', sans-serif !important;
    }
    
    /* Vynucení čistého písma Roboto pro běžné textové elementy */
    p, label, .stWidget label p, div[data-testid="stMarkdownContainer"] p {
        font-family: 'Roboto', sans-serif !important;
        color: #FFFFFF !important;
    }
    
    /* 🔥 NASAZENÍ SPORTVNÍHO FONTU 'STAATLICHES' NA VŠECHNY HLAVNÍ NADPISY */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Staatliches', sans-serif !important;
        color: #FFF200 !important; /* Fortuna zářivě žlutá */
        letter-spacing: 1.5px !important;
        text-transform: uppercase !important;
    }

    /* Hlavička expanderu (text zápasu) dostane Staatliches */
    .streamlit-expanderHeader p {
        font-family: 'Staatliches', sans-serif !important;
        color: #FFFFFF !important;
        letter-spacing: 1px !important;
        text-transform: uppercase !important;
    }
    
    [data-testid="stAppViewBlockContainer"] {
        padding-top: 1.5rem !important;
        padding-bottom: 3rem !important;
        max-width: 760px !important;
    }
    
    /* 2. BOČNÍ PANEL (SIDEBAR) - Čistá temná barva se žlutou linkou */
    [data-testid="stSidebar"] {
        background-color: #1A1A1A !important; 
        border-right: 2px solid #FFF200 !important;
    }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] label {
        color: #FFFFFF !important;
    }
    [data-testid="stSidebar"] h3 {
        font-family: 'Staatliches', sans-serif !important;
        color: #FFF200 !important;
    }
    
    /* Tlačítko odhlášení v sidebaru */
    [data-testid="stSidebar"] .stButton button {
        background-color: #262626 !important;
        border: 1px solid #333333 !important;
        color: #FF4B4B !important;
        border-radius: 4px !important;
        width: 100% !important;
    }
    [data-testid="stSidebar"] .stButton button:hover,
    [data-testid="stSidebar"] .stButton button:hover *,
    [data-testid="stSidebar"] .stButton button:hover p,
    [data-testid="stSidebar"] .stButton button:hover span {
        background-color: #FFF200 !important;
        color: #000000 !important;
    }

    /* 3. VSTUPNÍ POLE A FORMULÁŘE */
    div[data-testid="stTextInput"] input, div[data-testid="stNumberInput"] input {
        background-color: #1A1A1A !important;
        color: #FFFFFF !important;
        border: 1px solid #333333 !important;
        border-radius: 4px !important;
    }
    div[data-testid="stRadio"] label span {
        color: #FFFFFF !important;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] {
        background-color: #1A1A1A !important;
        padding: 12px !important;
        border-radius: 6px !important;
        border: 1px solid #2D2D2D !important;
    }

    /* 4. TLAČÍTKA */
    div.stButton > button {
        border-radius: 4px !important;
        font-weight: 800 !important;
        letter-spacing: 0.5px !important;
        text-transform: uppercase !important;
        transition: all 0.15s ease-in-out !important;
    }
    
    div.stButton > button[kind="primary"] {
        background-color: #FFF200 !important;
        border: none !important;
        box-shadow: 0 4px 10px rgba(255, 242, 0, 0.15) !important;
        width: 100% !important;
    }
    div.stButton > button[kind="primary"] *, 
    div.stButton > button[kind="primary"] p, 
    div.stButton > button[kind="primary"] div,
    div.stButton > button[kind="primary"] span {
        color: #000000 !important; 
        font-family: 'Roboto', sans-serif !important;
    }
    div.stButton > button[kind="primary"]:hover,
    div.stButton > button[kind="primary"]:hover *,
    div.stButton > button[kind="primary"]:hover p,
    div.stButton > button[kind="primary"]:hover span {
        background-color: #FFE600 !important;
        color: #000000 !important;
        box-shadow: 0 4px 14px rgba(255, 242, 0, 0.3) !important;
    }
    
    div.stButton > button[kind="secondary"] {
        background-color: #1A1A1A !important;
        border: 1px solid #FFF200 !important;
        color: #FFF200 !important;
    }
    div.stButton > button[kind="secondary"] *,
    div.stButton > button[kind="secondary"] p,
    div.stButton > button[kind="secondary"] span {
        color: #FFF200 !important;
    }
    div.stButton > button[kind="secondary"]:hover,
    div.stButton > button[kind="secondary"]:hover *,
    div.stButton > button[kind="secondary"]:hover p,
    div.stButton > button[kind="secondary"]:hover span {
        background-color: #FFF200 !important;
        color: #000000 !important;
        border-color: #FFF200 !important;
    }

    /* 5. KARTY ZÁPASŮ (EXPANDERY) */
    .streamlit-expander {
        border: 1px solid #2D2D2D !important;
        border-radius: 6px !important;
        background-color: #1A1A1A !important;
        margin-bottom: 14px !important;
    }
    .streamlit-expanderHeader {
        background-color: #1A1A1A !important;
        border-bottom: 1px solid #252525 !important;
        padding: 12px 16px !important;
    }
    .streamlit-expanderHeader:hover {
        background-color: #222222 !important;
    }
    
    /* 6. HORNÍ NAVIGAČNÍ MENU (TABS) */
    div[data-testid="stTabBar"] {
        background-color: #1A1A1A !important;
        padding: 4px !important;
        border-radius: 6px !important;
        border: 1px solid #2D2D2D !important;
        margin-bottom: 25px !important;
    }
    div[data-testid="stTabBar"] button {
        background: transparent !important;
    }
    div[data-testid="stTabBar"] button p {
        color: #888888 !important;
        font-weight: 700 !important;
    }
    div[data-testid="stTabBar"] button[aria-selected="true"] {
        background-color: #222222 !important;
        border-bottom: 2px solid #FFF200 !important;
    }
    div[data-testid="stTabBar"] button[aria-selected="true"] p {
        color: #FFF200 !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- NAPOJENÍ NA GOOGLE TABULKY ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

if "gspread_creds" in st.secrets:
    import json
    creds_dict = dict(st.secrets["gspread_creds"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
else:
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)

client = gspread.authorize(creds)

# --- 🧠 PAMĚŤOVÉ FUNKCE (OCHRANA PŘED ERROR 429) ---
@st.cache_data(ttl=30)
def nacti_uzivatele():
    try: return client.open("Mistrovstvi_Tipovacka").worksheet("Uzivatele").get_all_records()
    except: return []

@st.cache_data(ttl=30)
def nacti_zapasy():
    try: return client.open("Mistrovstvi_Tipovacka").worksheet("Zápasy").get_all_records()
    except: return []

@st.cache_data(ttl=30)
def nacti_sazky():
    try: return client.open("Mistrovstvi_Tipovacka").worksheet("Sázky").get_all_records()
    except: return []

# --- INICIALIZACE STAVU PŘIHLÁŠENÍ ---
if "prihlasen" not in st.session_state:
    st.session_state["prihlasen"] = False
    st.session_state["uzivatel"] = ""

# --- HLAVNÍ TITULEK ---
st.title("⚽ MS 26 TIPOVAČKA")

# ==========================================
# OBRAZOVKA A: PŘIHLÁŠENÍ
# ==========================================
if not st.session_state["prihlasen"]:
    st.subheader("Přihlášení do systému")
    jmeno = st.text_input("Jméno")
    heslo = st.text_input("Heslo", type="password")
    
    if st.button("Přihlásit se", type="secondary"):
        data_uzivatele_local = nacti_uzivatele()
        uzivatele_overeni = {}
        for radek in data_uzivatele_local:
            uzivatele_overeni[str(radek.get("Jméno", ""))] = str(radek.get("Heslo", ""))
            
        if jmeno in uzivatele_overeni and uzivatele_overeni[jmeno] == heslo:
            st.session_state["prihlasen"] = True
            st.session_state["uzivatel"] = jmeno
            st.success(f"Vítej, {jmeno}!")
            st.rerun()
        else:
            st.error("Nesprávné jméno nebo heslo!")

# ==========================================
# OBRAZOVKA B: CELÝ VNITŘEK TIPOVAČKY (JEN PRO PŘIHLÁŠENÉ)
# ==========================================
else:
    data_uzivatele = nacti_uzivatele()
    data_zapasy = nacti_zapasy()
    vsechny_sazky = nacti_sazky()
    
# --- BEZPEČNÉ DYNAMICKÉ NAČTENÍ REŽIMU PLAYOFF Z TABULKY ZÁPASY (BUŇKA V1) ---
    try:
        sheet_zapasy_raw = client.open("Mistrovstvi_Tipovacka").worksheet("Zápasy")
        stav_playoff_v_tabulce = sheet_zapasy_raw.acell('V1').value
        je_playoff = str(stav_playoff_v_tabulce).strip().lower() == "ano"
    except:
        je_playoff = False  # Výchozí stav, pokud by selhalo spojení

    UZIVATELE = {}
    for radek in data_uzivatele:
        jm_klic = str(radek.get("Jméno", ""))
        if jm_klic:
            UZIVATELE[jm_klic] = {
                "heslo": str(radek.get("Heslo", "")),
                "body": radek.get("Body", 0),
                "status": str(radek.get("Status", "")).strip()
            }

    PREKLAD_TYMU = {
        "Canada": {"jmeno": "Kanada", "kod": "ca"}, "Mexico": {"jmeno": "Mexiko", "kod": "mx"}, "USA": {"jmeno": "USA", "kod": "us"},
        "England": {"jmeno": "Anglie", "kod": "gb-eng"}, "Austria": {"jmeno": "Rakousko", "kod": "at"}, "Belgium": {"jmeno": "Belgie", "kod": "be"},
        "Bosnia & Herzegovina": {"jmeno": "Bosna a Herc.", "kod": "ba"}, "Croatia": {"jmeno": "Chorvatsko", "kod": "hr"}, "Czech Republic": {"jmeno": "Česko", "kod": "cz"},
        "France": {"jmeno": "Francie", "kod": "fr"}, "Germany": {"jmeno": "Německo", "kod": "de"}, "Netherlands": {"jmeno": "Nizozemsko", "kod": "nl"},
        "Norway": {"jmeno": "Norsko", "kod": "no"}, "Portugal": {"jmeno": "Portugalsko", "kod": "pt"}, "Scotland": {"jmeno": "Skotsko", "kod": "gb-sct"},
        "Spain": {"jmeno": "Španělsko", "kod": "es"}, "Sweden": {"jmeno": "Švédsko", "kod": "se"}, "Switzerland": {"jmeno": "Švýcarsko", "kod": "ch"}, "Turkey": {"jmeno": "Turecko", "kod": "tr"},
        "Argentina": {"jmeno": "Argentina", "kod": "ar"}, "Brazil": {"jmeno": "Brazílie", "kod": "br"}, "Ecuador": {"jmeno": "Ekvádor", "kod": "ec"},
        "Colombia": {"jmeno": "Kolumbie", "kod": "co"}, "Paraguay": {"jmeno": "Paraguay", "kod": "py"}, "Uruguay": {"jmeno": "Uruguay", "kod": "uy"},
        "Algeria": {"jmeno": "Alžírsko", "kod": "dz"}, "Egypt": {"jmeno": "Egypt", "kod": "eg"}, "Ghana": {"jmeno": "Ghana", "kod": "gh"},
        "DR Congo": {"jmeno": "DR Kongo", "kod": "cd"}, "Cape Verde": {"jmeno": "Kapverdy", "kod": "cv"}, "Morocco": {"jmeno": "Maroko", "kod": "ma"},
        "Ivory Coast": {"jmeno": "Pobřeží slonoviny", "kod": "ci"}, "Senegal": {"jmeno": "Senegal", "kod": "sn"}, "Tunisia": {"jmeno": "Tunisko", "kod": "tn"}, "South Africa": {"jmeno": "Jihoafrická rep.", "kod": "za"},
        "Australia": {"jmeno": "Austrálie", "kod": "au"}, "Iran": {"jmeno": "Írán", "kod": "ir"}, "Iraq": {"jmeno": "Irák", "kod": "iq"},
        "Japan": {"jmeno": "Japonsko", "kod": "jp"}, "Jordan": {"jmeno": "Jordánsko", "kod": "jo"}, "Qatar": {"jmeno": "Katar", "kod": "qa"},
        "Saudi Arabia": {"jmeno": "Saúdská Arábie", "kod": "sa"}, "South Korea": {"jmeno": "Jižní Korea", "kod": "kr"}, "Uzbekistan": {"jmeno": "Uzbekistán", "kod": "uz"},
        "Curaçao": {"jmeno": "Curaçao", "kod": "cw"}, "Haiti": {"jmeno": "Haiti", "kod": "ht"}, "Panama": {"jmeno": "Panama", "kod": "pa"}, "New Zealand": {"jmeno": "Nový Zéland", "kod": "nz"}
    }
    
    def dej_data_tymu(tym_z_api):
        return PREKLAD_TYMU.get(tym_z_api, {"jmeno": tym_z_api, "kod": "un"})
        
    aktualni_uzivatel = st.session_state["uzivatel"]
    aktualni_body = UZIVATELE[aktualni_uzivatel]["body"] if aktualni_uzivatel in UZIVATELE else 0.0
    
    # --- SIDEBAR VÝPISY ---
    st.sidebar.write(f"👤 Hráč: **{aktualni_uzivatel}**")
    st.sidebar.write(f"✨ Body: **{aktualni_body} b.**")
    
    moje_sazky = [s for s in vsechny_sazky if str(s.get("Uzivatel", "")) == aktualni_uzivatel]
    
    pouziti_zolici = sum(1 for s in moje_sazky if str(s.get("Zolik", "Ne")).lower() == "ano")
    max_zoliku = 3  
    zbyva_zoliku = max(0, max_zoliku - pouziti_zolici)
    
    ikony_zoliku = " ".join(["🃏"] * zbyva_zoliku + ["❌"] * pouziti_zolici)
    st.sidebar.write(f"🃏 Žolíci: **{ikony_zoliku}** ({zbyva_zoliku} ze 3)")
    
    if st.sidebar.button("Odhlásit se"):
        st.session_state["prihlasen"] = False
        st.session_state["uzivatel"] = ""
        st.rerun()
        
    st.sidebar.write("")
    stuj_status = UZIVATELE[aktualni_uzivatel].get("status", "") if aktualni_uzivatel in UZIVATELE else ""
    novy_status = st.sidebar.text_input("💬 Rýpni si do ostatních:", value=stuj_status, max_chars=60, key="banter_input")
    
    if novy_status != stuj_status:
        if st.sidebar.button("💾 Uložit status", type="secondary", key="btn_uložit_status"):
            with st.spinner("Ukládám status..."):
                sheet_u = client.open("Mistrovstvi_Tipovacka").worksheet("Uzivatele")
                u_list = sheet_u.get_all_records()
                for i, r in enumerate(u_list):
                    if str(r["Jméno"]) == aktualni_uzivatel:
                        sheet_u.update_cell(i + 2, 4, novy_status)
                        break
            st.cache_data.clear()
            st.rerun()    
        
    st.sidebar.markdown("---")
    st.sidebar.subheader("🏆 Průběžné pořadí")
    
    serazeni_hraci = sorted(UZIVATELE.items(), key=lambda x: x[1]['body'], reverse=True)
    medaile = ["🥇", "🥈", "🥉"]
    
    for i, (jm, dt) in enumerate(serazeni_hraci):
        znak = medaile[i] if i < len(medaile) else "🏅"
        styl_jmena = "font-weight: bold; color: #FFF200; font-size: 16px;" if jm == aktualni_uzivatel else "color: #FFFFFF; font-size: 16px;"
        text_statusu = f"<div style='color: #aaaaaa; font-style: italic; font-size: 13px; margin-top: 2px; padding-left: 22px;'>„{dt['status']}“</div>" if dt['status'] else ""
        st.sidebar.markdown(f"<div style='margin-bottom: 14px; line-height: 1.2;'><span style='{styl_jmena}'>{i+1}. {znak} {jm} — {dt['body']} b.</span>{text_statusu}</div>", unsafe_allow_html=True)

    # ==========================================
    # 🛠 POMOCNÁ FUNKCE PRO DETAIL ZÁPASU (S NOVÝM INTEGRALNÍM SÁZENÍM)
    # ==========================================
    def vykresli_detail_zapasu(z, zapas_uzamcen, moje_sazky):
        stavajici_tip = next((s for s in moje_sazky if str(s.get("ID_zapasu")) == str(z["ID"])), None)
        t_domaci = dej_data_tymu(z['Domaci'])
        t_hoste = dej_data_tymu(z['Hoste'])
        
        je_zapas_ukoncen = str(z.get("Stav", "")).lower() == "ukonceno"
        skore_text = f" ({z.get('Vysledek', '')})" if z.get('Vysledek') else ""
        
        odpocet_titulek = ""
        vnitrni_odpocet_html = ""
        
        if not je_zapas_ukoncen and not zapas_uzamcen:
            try:
                match_dt = datetime.strptime(f"{z.get('Datum', '')}.2026", "%d.%m. %H:%M.%Y")
                lock_dt = match_dt - timedelta(minutes=1)
                aktualni_cas = datetime.utcnow() + timedelta(hours=2)
                diff = lock_dt - aktualni_cas
                
                if diff.total_seconds() > 0:
                    dny = diff.days
                    hodiny, sekundy = divmod(diff.seconds, 3600)
                    minuty, _ = divmod(sekundy, 60)
                    
                    if dny > 0: cas_text = f"{dny} d. {hodiny} hod."; barva = "#888888"
                    elif hodiny > 0: cas_text = f"{hodiny} hod. {minuty} min."; barva = "#FFF200"; odpocet_titulek = f" ⏱️ ({hodiny}h {minuty}m)"
                    else: cas_text = f"{minuty} minut!!"; barva = "#FF4B4B"; odpocet_titulek = f" 🚨 ({minuty}m!)"
                    
                    vnitrni_odpocet_html = f"<div style='text-align: center; margin-top: -10px; margin-bottom: 15px; font-size: 13px; color: {barva}; font-weight: 500;'>⏳ Do uzamčení tipů zbývá: <span style='font-weight: bold; text-transform: uppercase;'>{cas_text}</span></div>"
            except: pass
        
        if je_zapas_ukoncen: titulek_radku = f"✅ {z.get('Datum', '')} | {t_domaci['jmeno']} vs {t_hoste['jmeno']}{skore_text} (ODEHRÁNO)"
        elif zapas_uzamcen: titulek_radku = f"🔒 {z.get('Datum', '')} | {t_domaci['jmeno']} vs {t_hoste['jmeno']} (TIPY UZAVŘENY)"
        else: titulek_radku = f"📅 {z.get('Datum', '')} | {t_domaci['jmeno']} vs {t_hoste['jmeno']}{odpocet_titulek}"
        
        with st.expander(titulek_radku):
            st.write("")
            if je_playoff:
                st.warning("🚨 **PLAY-OFF ZÁPAS:** Tipuje se pouze postupující (1 nebo 2). V případě penalt se vítězi přičte fiktivní 1 gól navíc k remíze!")
            
            img_domaci = f"<img src='https://flagcdn.com/w160/{t_domaci['kod']}.png' width='70' style='border-radius: 4px;'><br>" if t_domaci['kod'] != "un" else ""
            img_hoste = f"<img src='https://flagcdn.com/w160/{t_hoste['kod']}.png' width='70' style='border-radius: 4px;'><br>" if t_hoste['kod'] != "un" else ""
            stred_text = str(z.get('Vysledek')) if je_zapas_ukoncen and z.get('Vysledek') else "VS"
            stred_color = "#FFF200" if je_zapas_ukoncen and z.get('Vysledek') else "#888888"
            
            # --- 🟢 GEOMETRICKY VYCENTROVANÉ A FONTOVĚ SJEDNOCENÉ KURZY ---
            k1_html = f"({z.get('Kurz_1', '')})" if str(z.get('Kurz_1', '')).strip() else ""
            k2_html = f"({z.get('Kurz_2', '')})" if str(z.get('Kurz_2', '')).strip() else ""
            kx_html = f"({z.get('Kurz_X', '')})" if (str(z.get('Kurz_X', '')).strip() and not je_zapas_ukoncen) else ""

            st.markdown(f"""
            <div style='display: flex; justify-content: space-between; align-items: center; width: 100%;'>
                <div style='flex: 1; text-align: center;'>
                    {img_domaci}
                    <div style='font-size: 20px; font-weight: bold; margin-top: 5px;'>{t_domaci['jmeno']}</div>
                </div>
                <div style='flex: 1; text-align: center;'>
                    <h2 style='color: {stred_color}; margin: 0; padding: 0; font-family: "Staatliches", sans-serif; font-size: 36px; font-weight: bold; letter-spacing: 1px; text-align: center;'>{stred_text}</h2>
                </div>
                <div style='flex: 1; text-align: center;'>
                    {img_hoste}
                    <div style='font-size: 20px; font-weight: bold; margin-top: 5px;'>{t_hoste['jmeno']}</div>
                </div>
            </div>
            
            <div style='display: flex; justify-content: space-between; align-items: center; width: 100%; margin-top: 10px; font-size: 13px; color: #888888; font-weight: 400;'>
                <div style='flex: 1; text-align: center;'>{k1_html}</div>
                <div style='flex: 1; text-align: center;'>{kx_html}</div>
                <div style='flex: 1; text-align: center;'>{k2_html}</div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("---")
            
            if vnitrni_odpocet_html: st.markdown(vnitrni_odpocet_html, unsafe_allow_html=True)
            
            if zapas_uzamcen:
                if stavajici_tip:
                    st.success("🔒 Tipy jsou uzavřeny. Tvůj podaný tiket:")
                    c1, c2 = st.columns(2)
                    with c1: st.info(f"**Hlavní sázka:** {stavajici_tip.get('Tip_Hlavni')}")
                    with c2: st.info(f"**Tip na přesné skóre:** {stavajici_tip.get('Tip_Skore')}")
                else: st.warning("🔒 Zápas již odstartoval bez tvého tipu.")
            else:
                if stavajici_tip: st.warning("⚠️ Na tento zápas už máš vsazeno. Níže můžeš svůj tip kdykoliv upravit.")
                
                moznat_hlavni = ["1", "2"] if je_playoff else ["1", "10", "X", "02", "2"]
                format_hlavni_dict = {
                    "1": f"1 (Výhra {t_domaci['jmeno']})",
                    "X": "X (Čistá remíza)",
                    "2": f"2 (Výhra {t_hoste['jmeno']})",
                    "10": f"10 (Neprohra {t_domaci['jmeno']})",
                    "02": f"02 (Neprohra {t_hoste['jmeno']})"
                }
                
                idx_hlavni = moznat_hlavni.index(str(stavajici_tip["Tip_Hlavni"])) if stavajici_tip and str(stavajici_tip["Tip_Hlavni"]) in moznat_hlavni else 0
                
                stare_home, stare_away = 0, 0
                if stavajici_tip and ":" in str(stavajici_tip.get("Tip_Skore", "")):
                    try: stare_home, stare_away = map(int, str(stavajici_tip["Tip_Skore"]).split(":"))
                    except: pass
                
                col_s1, col_s2 = st.columns(2)
                with col_s1:
                    st.write("**1. Hlavní sázka (Základ)**")
                    volba_hlavni = st.radio("Zvol typ výsledku:", moznat_hlavni, index=idx_hlavni, format_func=lambda x: format_hlavni_dict.get(x, x), key=f"main_{z['ID']}")
                with col_s2:
                    st.write("**2. Přesné skóre zápasu**")
                    c_g1, c_g2 = st.columns(2)
                    with c_g1: tip_goly_home = st.number_input(f"{t_domaci['jmeno']}", min_value=0, max_value=20, value=stare_home, step=1, key=f"gh_{z['ID']}")
                    with c_g2: tip_goly_away = st.number_input(f"{t_hoste['jmeno']}", min_value=0, max_value=20, value=stare_away, step=1, key=f"ga_{z['ID']}")
                    st.caption("💡 Skóre je nezávislý tip, může posloužit třeba jako taktická pojistka.")
                
                uz_ma_zolika = stavajici_tip and str(stavajici_tip.get("Zolik", "Ne")).lower() == "ano"
                chce_zolika = False
                if zbyva_zoliku > 0 or uz_ma_zolika:
                    chce_zolika = st.checkbox("🃏 Aktivovat ŽOLÍKA (Dvojnásobné body za celý zápas!)", value=uz_ma_zolika, key=f"zol_{z['ID']}")
                else: st.caption("❌ Už jsi vyčerpal všech 3 žolíky pro tuto fázi.")
                
# --- OCHRANA PROTI REMÍZOVÉMU SKÓRE V PLAY-OFF ---
                ZABLOKOVAT_ZAPIS = False
                if je_playoff and tip_goly_home == tip_goly_away:
                    st.error("🚨 **V play-off zápase nesmíš tipovat nerozhodný výsledek!**")
                    ZABLOKOVAT_ZAPIS = True
                
                text_tlacitka = "🔄 AKTUALIZOVAT TIKET" if stavajici_tip else "💾 VSADIT TIKET"
                if st.button(text_tlacitka, key=f"btn_{z['ID']}", type="primary"):
                    sheet_sazky = client.open("Mistrovstvi_Tipovacka").worksheet("Sázky")
                    string_skore = f"{tip_goly_home}:{tip_goly_away}"
                    
                    vsechny_sazky_aktualni = sheet_sazky.get_all_records()
                    radek_pro_zapis = None
                    for idx, s in enumerate(vsechny_sazky_aktualni):
                        if str(s.get("Uzivatel")) == aktualni_uzivatel and str(s.get("ID_zapasu")) == str(z["ID"]):
                            radek_pro_zapis = idx + 2
                            break
                    
                    novy_radek = [
                        aktualni_uzivatel, z['ID'], f"{t_domaci['jmeno']}-{t_hoste['jmeno']}",
                        volba_hlavni, string_skore, "ceka", "ceka", 0, "ceka", "Ano" if chce_zolika else "Ne"
                    ]
                    with st.spinner("Ukládám tiket..."):
                        if radek_pro_zapis: sheet_sazky.update(f"A{radek_pro_zapis}:J{radek_pro_zapis}", [novy_radek])
                        else: sheet_sazky.append_row(novy_radek)
                            
                    st.cache_data.clear()
                    st.success("Tiket byl podán!")
                    st.rerun()

    tabs = st.tabs(["📅 Nabídka zápasů", "📜 Moje tipy", "📊 Statistiky", "⚙️ Admin"])
    tab1, tab2, tab3, tab4 = tabs[0], tabs[1], tabs[2], tabs[3]

    # ==========================================
    # ZÁLOŽKA 1: KURZOVÁ NABÍDKA
    # ==========================================
    with tab1:
        st.subheader("📅 Nabídka zápasů")
        
        # 🟢 OPRAVENO: Tabulka s vynucenou šířkou 100% pro dokonalé dotečení ke krajům
        with st.expander("📊 BODOVACÍ SYSTÉM A PRAVIDLA"):
            st.markdown("""
            <div style="width: 100%; overflow-x: auto;">
                <table style="width: 100%; border-collapse: collapse; color: #FFFFFF; font-family: 'Roboto', sans-serif; font-size: 14px;">
                    <thead>
                        <tr style="border-bottom: 2px solid #2D2D2D; text-align: left;">
                            <th style="padding: 10px; font-weight: bold; color: #FFF200;">⚽ Sázková příležitost</th>
                            <th style="padding: 10px; font-weight: bold; color: #FFF200;">🎯 Co musíš trefit</th>
                            <th style="padding: 10px; text-align: center; font-weight: bold; color: #FFF200;">🏆 Body</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr style="border-bottom: 1px solid #252525;">
                            <td style="padding: 10px; font-weight: bold;">Výhra domácích / hostů</td>
                            <td style="padding: 10px;">Přesný výsledek (v play-off postup)</td>
                            <td style="padding: 10px; text-align: center; font-weight: bold;">2 b.</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #252525;">
                            <td style="padding: 10px; font-weight: bold;">Čistá remíza (X)</td>
                            <td style="padding: 10px;">Zápas skončí nerozhodně (jen ve skupině)</td>
                            <td style="padding: 10px; text-align: center; font-weight: bold;">3 b.</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #252525;">
                            <td style="padding: 10px; font-weight: bold;">Neprohra 10 / 02</td>
                            <td style="padding: 10px;">Pojistka na neprohru (jen ve skupině)</td>
                            <td style="padding: 10px; text-align: center; font-weight: bold;">1 b.</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #252525;">
                            <td style="padding: 10px; font-weight: bold;">Přesné skóre</td>
                            <td style="padding: 10px;">Úplně přesný výsledek (např. 2:1)</td>
                            <td style="padding: 10px; text-align: center; font-weight: bold;">4 b.</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #252525;">
                            <td style="padding: 10px; font-weight: bold;">Rozdíl skóre</td>
                            <td style="padding: 10px;">Správný gólový rozdíl (např. tip 3:1, stav 2:0)</td>
                            <td style="padding: 10px; text-align: center; font-weight: bold;">2 b.</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #2D2D2D;">
                            <td style="padding: 10px; font-weight: bold;">Ostatní remízy</td>
                            <td style="padding: 10px;">Jiné skóre remízy (např. tip 1:1, stav 2:2)</td>
                            <td style="padding: 10px; text-align: center; font-weight: bold;">2 b.</td>
                        </tr>
                    </tbody>
                </table>
            </div>
            <br>
            <p style="margin: 0; font-size: 13.5px; color: #FFFFFF;">
                💡 <b>Poznámka:</b> Tip na přesné skóre se počítá samostatně a nezávisle na hlavní sázce! Žolík 🃏 ti celý zisk ze zápasu zdvojnásobí <i>(Maximum je <b>7 bodů</b>, se žolíkem <b>14 bodů</b>)</i>.
            </p>
            """, unsafe_allow_html=True)
            
        st.markdown("---") # Oddělovací linka před samotnými zápasy
        
        aktualni_cas = datetime.utcnow() + timedelta(hours=2)
        dnes_str = aktualni_cas.strftime("%d.%m.")
        
        skupina_dnesni, skupina_nadchazejici, skupina_odehrane = [], [], []
        
        for z in data_zapasy:
            if str(z.get("Stav", "")).lower() in ["aktivni", "ukonceno"] and str(z.get("ID", "")).strip() != "":
                z_datum_str = z.get("Datum", "")
                zapas_uzamcen, je_dnes, je_v_minulosti = False, False, False
                try:
                    match_dt = datetime.strptime(f"{z_datum_str}.2026", "%d.%m. %H:%M.%Y")
                    if aktualni_cas >= (match_dt - timedelta(minutes=1)): zapas_uzamcen = True
                    if aktualni_cas >= match_dt: je_v_minulosti = True
                    if match_dt.date() == aktualni_cas.date(): je_dnes = True
                except:
                    if z_datum_str.startswith(dnes_str): je_dnes = True
                
                is_vyhodnoceno = any(str(s.get("ID_zapasu")) == str(z["ID"]) and str(s.get("Stav_Tipu", "")).lower() == "vyhodnoceno" for s in vsechny_sazky)
                balicek = {"zapas": z, "uzamcen": zapas_uzamcen}
                
                if is_vyhodnoceno or (je_v_minulosti and not je_dnes) or str(z.get("Stav", "")).lower() == "ukonceno": skupina_odehrane.append(balicek)
                elif je_dnes: skupina_dnesni.append(balicek)
                else: skupina_nadchazejici.append(balicek)
                    
        with st.expander("🔥 DNEŠNÍ ZÁPASY", expanded=True):
            if skupina_dnesni:
                for b in skupina_dnesni: vykresli_detail_zapasu(b["zapas"], b["uzamcen"], moje_sazky)
            else: st.info("Dnes se nehrají žádné zápasy.")
                
        with st.expander("🔮 NADCHÁZEJÍCÍ ZÁPASY", expanded=False):
            if skupina_nadchazejici:
                for b in skupina_nadchazejici: vykresli_detail_zapasu(b["zapas"], b["uzamcen"], moje_sazky)
            else: st.info("Žádné další nadcházející zápasy v programu nejsou.")
                
        with st.expander("📁 ODEHRANÉ A VYHODNOCENÉ ZÁPASY", expanded=False):
            if skupina_odehrane:
                for b in skupina_odehrane: vykresli_detail_zapasu(b["zapas"], b["uzamcen"], moje_sazky)
            else: st.caption("Zatím nebyl odehrán ani vyhodnocen žádný zápas turnaje.")

    # ==========================================
    # ZÁLOŽKA 2: MOJE TIPY A GRAF
    # ==========================================
    with tab2:
        st.subheader("📜 Moje tipy a graf")
        import pandas as pd
        
        vyhodnocene_zapasy = []
        for zp in data_zapasy:
            if any(str(s.get("ID_zapasu")) == str(zp["ID"]) and str(s.get("Stav_Tipu", "")).lower() == "vyhodnoceno" for s in vsechny_sazky): vyhodnocene_zapasy.append(zp)
        try: vyhodnocene_zapasy = sorted(vyhodnocene_zapasy, key=lambda x: datetime.strptime(f"{x['Datum']}.2026", "%d.%m. %H:%M.%Y"))
        except: pass
        
        vsichni_hraci = list(UZIVATELE.keys())
        body_v_case = [{"Zápas": "00. Start", **{h: 0.0 for h in vsichni_hraci}}]
        text_stavy = {h: 0.0 for h in vsichni_hraci}
        
        for idx, zp in enumerate(vyhodnocene_zapasy):
            z_id = str(zp["ID"])
            t_dom = dej_data_tymu(zp['Domaci'])['jmeno']
            t_hos = dej_data_tymu(zp['Hoste'])['jmeno']
            krasny_nazev_zapasu = f"{t_dom} - {t_hos}"
            for h in vsichni_hraci:
                sazka_hrace = next((s for s in vsechny_sazky if str(s.get("ID_zapasu")) == z_id and str(s.get("Uzivatel")) == h), None)
                if sazka_hrace and str(sazka_hrace.get("Stav_Tipu", "")).lower() == "vyhodnoceno": text_stavy[h] += float(sazka_hrace.get("Body_Ziskane", 0))
            cislo_zapasu = str(idx + 1).zfill(2)
            body_v_case.append({"Zápas": f"{cislo_zapasu}. {krasny_nazev_zapasu}", **{h: round(text_stavy[h], 2) for h in vsichni_hraci}})
            
        if len(body_v_case) > 1:
            st.markdown("#### 📈 Grafický vývoj bodů")
            df_wide = pd.DataFrame(body_v_case)
            df_long = df_wide.melt(id_vars=["Zápas"], var_name="Hráč", value_name="Body")
            import altair as alt
            paleta_barev = ["#FFF200", "#00A4E4", "#FF4B4B", "#11998E", "#E0E0E0"]
            barvy_pro_graf = paleta_barev[:len(vsichni_hraci)]
            
            lines = alt.Chart(df_long).mark_line(interpolate="monotone", strokeWidth=4).encode(
                x=alt.X("Zápas:N", axis=alt.Axis(labelAngle=-45, title=None, grid=True, gridColor="#262626", labelColor="white")),
                y=alt.Y("Body:Q", axis=alt.Axis(title="Celkový počet bodů", grid=True, gridColor="#262626", labelColor="white")),
                color=alt.Color("Hráč:N", scale=alt.Scale(domain=vsichni_hraci, range=barvy_pro_graf))
            )
            st.altair_chart(lines, use_container_width=True)
            
        aktualni_cas = datetime.utcnow() + timedelta(hours=2)
        for z in data_zapasy:
            if str(z.get("Stav", "")).lower() in ["aktivni", "ukonceno"] and str(z.get("ID", "")).strip() != "":
                z_datum_str = z.get("Datum", "")
                zapas_uzamcen = False
                try:
                    match_dt = datetime.strptime(f"{z_datum_str}.2026", "%d.%m. %H:%M.%Y")
                    if aktualni_cas >= (match_dt - timedelta(minutes=1)): zapas_uzamcen = True
                except: pass
                
                stavajici_tip = next((s for s in moje_sazky if str(s.get("ID_zapasu")) == str(z["ID"])), None)
                je_zapas_ukoncen = str(z.get("Stav", "")).lower() == "ukonceno"
                
                if zapas_uzamcen or stavajici_tip or je_zapas_ukoncen:
                    t_domaci = dej_data_tymu(z['Domaci'])
                    t_hoste = dej_data_tymu(z['Hoste'])
                    is_vyhodnoceno = stavajici_tip and str(stavajici_tip.get("Stav_Tipu", "")).lower() == "vyhodnoceno"
                    
                    if je_zapas_ukoncen or is_vyhodnoceno: 
                        body_zisk = stavajici_tip.get('Body_Ziskane', 0) if stavajici_tip else 0
                        skore_text = f" ({z.get('Vysledek', '')})" if z.get('Vysledek') else ""
                        titulek_radku = f"✅ {z.get('Datum', '')} | {t_domaci['jmeno']} vs {t_hoste['jmeno']}{skore_text} (+{body_zisk} b.)"
                    elif zapas_uzamcen: titulek_radku = f"🔒 {z.get('Datum', '')} | {t_domaci['jmeno']} vs {t_hoste['jmeno']} (ZAČALO)"
                    else: titulek_radku = f"⏳ {z.get('Datum', '')} | {t_domaci['jmeno']} vs {t_hoste['jmeno']} (ČEKÁ NA VÝKOP)"
                        
                    with st.expander(titulek_radku):
                        if stavajici_tip:
                            if str(stavajici_tip.get("Zolik", "Ne")).lower() == "ano":
                                st.markdown("<div style='background-color: #2a2a15; padding: 8px; border: 1px solid #FFF200; border-radius: 4px; margin-bottom: 12px; text-align: center;'><span style='color: #FFF200; font-weight: bold;'>🃏 ŽOLÍK AKTIVNÍ (2X BODY)</span></div>", unsafe_allow_html=True)
                            
                            c1, c2 = st.columns(2)
                            # Podpora zobrazení starého i nového formátu tabulky
                            t_hl = stavajici_tip.get("Tip_Hlavni", stavajici_tip.get("Tip_1X2", "-"))
                            t_sk = stavajici_tip.get("Tip_Skore", "-")
                            
                            with c1: st.markdown(f"**Hlavní sázka:** `{t_hl}`")
                            with c2: st.markdown(f"**Tip na skóre:** `{t_sk}`")
                            
                            if zapas_uzamcen:
                                st.write("")
                                st.markdown("**Jak sázeli ostatní:**")
                                tipy_ostatnich = [s for s in vsechny_sazky if str(s.get("ID_zapasu")) == str(z["ID"]) and str(s.get("Uzivatel")) != aktualni_uzivatel]
                                for t in tipy_ostatnich:
                                    # Podpora pro oba formáty klíčů hlavní sázky
                                    t_hl = t.get('Tip_Hlavni', t.get('Tip_1X2', '-'))
                                    t_sk = t.get('Tip_Skore', '-')
                                    
                                    # Pokud je zápas už vyhodnocený, vytáhneme body, jinak nedáme nic
                                    if str(t.get("Stav_Tipu", "")).lower() == "vyhodnoceno":
                                        body_text = f" **(+{t.get('Body_Ziskane', 0)} b.)**"
                                    else:
                                        body_text = ""
                                        
                                    st.write(f"👤 **{t['Uzivatel']}**: Hlavní: `{t_hl}` | Skóre: `{t_sk}`{body_text}")
                        else: st.warning("⚠️ Tento zápas jsi netipoval.")

    # ==========================================
    # ZÁLOŽKA 3: STATISTIKY (NATIVNÍ STREAMLIT BEZ HTML)
    # ==========================================
    with tab3:
        st.subheader("🏟️ Statistiky turnaje")

        # --- 🏆 ROZBALOVACÍ PAVOUK TURNAJE NA PRVNÍM MÍSTĚ ---
        with st.expander("🏟️ ZOBRAZIT VYŘAZOVACÍHO PAVOUKA TURNAJE", expanded=False):
            st.write("")
            st.markdown("<h3 style='text-align: center; color: #FFF200; font-family: \"Staatliches\", sans-serif; letter-spacing: 1px; margin-bottom: 20px;'>🏆 VYŘAZOVACÍ PAVOUK (OD 1/16 FINÁLE DO FINÁLE)</h3>", unsafe_allow_html=True)
            
            # Mapa zápasů podle ID pro rychlé vyhledání týmu a výsledku
            p_map = {str(zp.get("ID")): zp for zp in data_zapasy}
            
            # Pomocná vnitřní funkce pro vypsání jednoho zápasu v pavouku (Včetně překladů!)
            def vykresli_konec_pavouka(id_zapasu):
                zp = p_map.get(str(id_zapasu), {})
                
                raw_d = zp.get("Domaci")
                d = dej_data_tymu(raw_d)["jmeno"] if raw_d else "Postupující"
                
                raw_h = zp.get("Hoste")
                h = dej_data_tymu(raw_h)["jmeno"] if raw_h else "Postupující"
                
                v = str(zp.get("Vysledek", "")).strip()
                skore_html = f" <span style='color: #FFF200; font-weight: bold; background: #222222; padding: 2px 6px; border-radius: 4px; margin-left: 5px;'>{v}</span>" if v else ""
                
                st.markdown(f"""
                <div style='background: #1A1A1A; border: 1px solid #2D2D2D; padding: 8px; border-radius: 6px; margin-bottom: 8px; box-shadow: 2px 2px 5px rgba(0,0,0,0.5);'>
                    <div style='font-size: 10px; color: #888888; margin-bottom: 2px; font-weight: bold;'>Zápas #{id_zapasu}</div>
                    <div style='font-size: 12px; color: #FFFFFF; font-weight: 500; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;'>{d}</div>
                    <div style='font-size: 12px; color: #FFFFFF; font-weight: 500; margin-top: 1px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;'>{h}{skore_html}</div>
                </div>
                """, unsafe_allow_html=True)

            # Rozdělení na 5 sloupců pro play-off (ID 73 až 104)
            col_s16, col_o8, col_c4, col_s2, col_fin = st.columns(5)
            
            with col_s16:
                st.markdown("<h6 style='color: #FFF200; border-bottom: 2px solid #FFF200; padding-bottom: 4px; font-family: \"Staatliches\", sans-serif;'>1/16 Finále</h6>", unsafe_allow_html=True)
                for i in range(73, 89): vykresli_konec_pavouka(i)
                
            with col_o8:
                st.markdown("<h6 style='color: #FFF200; border-bottom: 2px solid #FFF200; padding-bottom: 4px; font-family: \"Staatliches\", sans-serif;'>1/8 Finále</h6>", unsafe_allow_html=True)
                st.write("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)
                vykresli_konec_pavouka(89)
                st.write("<div style='margin-top: 50px;'></div>", unsafe_allow_html=True)
                vykresli_konec_pavouka(90)
                st.write("<div style='margin-top: 50px;'></div>", unsafe_allow_html=True)
                vykresli_konec_pavouka(91)
                st.write("<div style='margin-top: 50px;'></div>", unsafe_allow_html=True)
                vykresli_konec_pavouka(92)
                st.write("<div style='margin-top: 50px;'></div>", unsafe_allow_html=True)
                vykresli_konec_pavouka(93)
                st.write("<div style='margin-top: 50px;'></div>", unsafe_allow_html=True)
                vykresli_konec_pavouka(94)
                st.write("<div style='margin-top: 50px;'></div>", unsafe_allow_html=True)
                vykresli_konec_pavouka(95)
                st.write("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)
                vykresli_konec_pavouka(96)
                
            with col_c4:
                st.markdown("<h6 style='color: #FFF200; border-bottom: 2px solid #FFF200; padding-bottom: 4px; font-family: \"Staatliches\", sans-serif;'>Čtvrtfinále</h6>", unsafe_allow_html=True)
                st.write("<div style='margin-top: 75px;'></div>", unsafe_allow_html=True)
                vykresli_konec_pavouka(97)
                st.write("<div style='margin-top: 190px;'></div>", unsafe_allow_html=True)
                vykresli_konec_pavouka(98)
                st.write("<div style='margin-top: 190px;'></div>", unsafe_allow_html=True)
                vykresli_konec_pavouka(99)
                st.write("<div style='margin-top: 190px;'></div>", unsafe_allow_html=True)
                vykresli_konec_pavouka(100)
                
            with col_s2:
                st.markdown("<h6 style='color: #FFF200; border-bottom: 2px solid #FFF200; padding-bottom: 4px; font-family: \"Staatliches\", sans-serif;'>Semifinále</h6>", unsafe_allow_html=True)
                st.write("<div style='margin-top: 175px;'></div>", unsafe_allow_html=True)
                vykresli_konec_pavouka(101)
                st.write("<div style='margin-top: 450px;'></div>", unsafe_allow_html=True)
                vykresli_konec_pavouka(102)
                
            with col_fin:
                st.markdown("<h6 style='color: #00FF00; border-bottom: 2px solid #00FF00; padding-bottom: 4px; font-family: \"Staatliches\", sans-serif;'>FINÁLE</h6>", unsafe_allow_html=True)
                st.write("<div style='margin-top: 360px;'></div>", unsafe_allow_html=True)
                
                zp_f = p_map.get("103", {})
                raw_df = zp_f.get("Domaci")
                d_f = dej_data_tymu(raw_df)["jmeno"] if raw_df else "Finalista 1"
                raw_hf = zp_f.get("Hoste")
                h_f = dej_data_tymu(raw_hf)["jmeno"] if raw_hf else "Finalista 2"
                
                v_f = str(zp_f.get("Vysledek", "")).strip()
                skore_f_html = f" <span style='color: #FFF200; font-weight: bold; background: #121212; padding: 2px 6px; border-radius: 4px; margin-left: 5px;'>{v_f}</span>" if v_f else ""
                
                st.markdown(f"""
                <div style='background: #2A2A15; border: 2px solid #FFF200; padding: 8px; border-radius: 8px; box-shadow: 0px 0px 12px rgba(255,242,0,0.3);'>
                    <div style='font-size: 10px; color: #FFF200; margin-bottom: 4px; font-weight: bold;'>🏆 FINÁLE (#103)</div>
                    <div style='font-size: 11px; color: #FFFFFF; font-weight: bold; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;'>{d_f}</div>
                    <div style='font-size: 11px; color: #FFFFFF; font-weight: bold; margin-top: 2px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;'>{h_f}{skore_f_html}</div>
                </div>
                """, unsafe_allow_html=True)
                
                st.write("<div style='margin-top: 120px;'></div>", unsafe_allow_html=True)
                st.markdown("<h6 style='color: #888888; border-bottom: 1px solid #2D2D2D; padding-bottom: 2px;'>O 3. místo</h6>", unsafe_allow_html=True)
                vykresli_konec_pavouka(104)

        st.write("")

        # --- 📊 TVŮJ KOMPLETNÍ, ORIGINÁLNÍ KÓD STATISTIK (STOPROCENTNĚ ZACHOVANÝ) ---
        ukoncene_zapasy_local = [zp for zp in data_zapasy if str(zp.get("Stav", "")).lower() == "ukonceno" and ":" in str(zp.get("Vysledek", ""))]
        celkem_odehrano_local = len(ukoncene_zapasy_local)

        if celkem_odehrano_local == 0:
            st.info("ℹ️ Turnajové statistiky a DNA hráčů se plně propočítají, jakmile se odehrají první zápasy!")
        else:
            goly_celkem = 0
            remizy_skutecne = 0
            over_25_celkem = 0
            
            nejvyssi_rozdil = -1
            nejvyssi_vyhra_text = "Zatím žádný zápas"

            for zp in ukoncene_zapasy_local:
                try:
                    hg, ag = map(int, str(zp.get("Vysledek")).split(":"))
                    total_g = hg + ag
                    goly_celkem += total_g
                    
                    if hg == ag: 
                        remizy_skutecne += 1
                    if total_g > 2.5: 
                        over_25_celkem += 1
                    
                    rozdil = abs(hg - ag)
                    if rozdil > nejvyssi_rozdil:
                        nejvyssi_rozdil = rozdil
                        t_dom = dej_data_tymu(zp['Domaci'])['jmeno']
                        t_hos = dej_data_tymu(zp['Hoste'])['jmeno']
                        nejvyssi_vyhra_text = f"**{t_dom} vs. {t_hos} {hg}:{ag}** (rozdíl +{rozdil} gólů)"
                except: pass

            avg_goly = round(goly_celkem / celkem_odehrano_local, 2)
            p_remiz = round((remizy_skutecne / celkem_odehrano_local) * 100, 1)
            p_over = round((over_25_celkem / celkem_odehrano_local) * 100, 1)

            c1, c2, c3 = st.columns(3)
            with c1: st.metric("Odehrané zápasy", f"{celkem_odehrano_local} ⚽")
            with c2: st.metric("Gólový průměr", f"{avg_goly} 🔥")
            with c3: st.metric("Zápasy s plichtou", f"{p_remiz} % 🤝")

            st.write("")
            st.markdown(f"**📊 Poměr zápasů Over / Under 2.5 gólů:**")
            st.progress(p_over / 100.0)
            col_b1, col_b2 = st.columns(2)
            with col_b1: st.caption(f"Under 2.5 gólů ({round(100.0 - p_over, 1)} %)")
            with col_b2: st.markdown(f"<div style='text-align: right; font-size: 14px; color: #FFF200; font-weight: bold;'>Over 2.5 gólů ({p_over} %)</div>", unsafe_allow_html=True)

            st.write("")
            st.markdown(f"🏆 **Nejvyšší výhra turnaje:**")
            st.info(nejvyssi_vyhra_text)

        st.markdown("---")
        st.markdown("### 🧬 Sázkařské DNA")

        stats_hraci = {}
        for h in UZIVATELE.keys():
            stats_hraci[h] = {
                "celkem_vyhodnoceno": 0,
                "hlavni_trefy": 0,
                "presny_zasah": 0,
                "rozdil_zasah": 0,
                "ostatni_remizy": 0,
                "pouzite_dvojšance": 0
            }

        for s in vsechny_sazky:
            h = s.get("Uzivatel")
            if h not in stats_hraci: continue
            if str(s.get("Stav_Tipu")).lower() != "vyhodnoceno": continue

            stats_hraci[h]["celkem_vyhodnoceno"] += 1
            if str(s.get("Stav_Hlavni")).lower() == "vyhra":
                stats_hraci[h]["hlavni_trefy"] += 1

            t_hl = str(s.get("Tip_Hlavni", ""))
            if t_hl in ["10", "02"]: stats_hraci[h]["pouzite_dvojšance"] += 1

            st_sk = str(s.get("Stav_Skore", "")).lower()
            if st_sk == "presne": stats_hraci[h]["presny_zasah"] += 1
            elif st_sk == "rozdil": stats_hraci[h]["rozdil_zasah"] += 1
            elif st_sk == "remiza_ostatni": stats_hraci[h]["ostatni_remizy"] += 1

        cols_karty = st.columns(3)
        jmena_hracu = list(stats_hraci.keys())

        for idx, h in enumerate(jmena_hracu):
            if idx >= len(cols_karty): break
            dt = stats_hraci[h]
            
            # Výpočet šňůry (TVŮJ ORIGINÁLNÍ VÝPOČET)
            uziv_sazky = [s for s in vsechny_sazky if str(s.get("Uzivatel")) == h and str(s.get("Stav_Tipu")).lower() == "vyhodnoceno"]
            try: uziv_sazky = sorted(uziv_sazky, key=lambda x: int(x["ID_zapasu"]))
            except: pass
            
            max_snura = 0
            aktualni_snura = 0
            for s in uziv_sazky:
                if str(s.get("Stav_Hlavni")).lower() == "vyhra":
                    aktualni_snura += 1
                    if aktualni_snura > max_snura: max_snura = aktualni_snura
                else: aktualni_snura = 0
            
            acc_hlavni = round((dt["hlavni_trefy"] / dt["celkem_vyhodnoceno"]) * 100, 1) if dt["celkem_vyhodnoceno"] > 0 else 0.0
            stuj_status_local = UZIVATELE[h].get("status", "")

            # Vykreslení karty (TVŮJ ORIGINÁLNÍ NATIVNÍ STREAMLIT DESIGN)
            with cols_karty[idx]:
                st.markdown(f"### {h}")
                if stuj_status_local:
                    st.caption(f"„{stuj_status_local}“")
                
                st.metric("Úspěšnost tipů", f"{acc_hlavni} %")
                st.markdown("---")
                
                st.markdown(f"👑 **Přesné skóre:** `{dt['presny_zasah']}x`")
                st.markdown(f"📐 **Správný rozdíl:** `{dt['rozdil_zasah']}x`")
                st.markdown(f"🤝 **Jiná remíza:** `{dt['ostatni_remizy']}x`")
                st.markdown(f"🛡️ **Pojistka dvojšancí:** `{dt['pouzite_dvojšance']}x`")
                st.markdown(f"🔥 **Nejdelší vítězná šňůra:** `{max_snura} zápasů`")

    # ==========================================
    # ZÁLOŽKA 4: ⚙️ ADMINISTRACE (VÝPOČET PODLE FINÁLNÍCH PRAVIDEL 4-2-2)
    # ==========================================
    with tab4:
        ADMIN_JMENO = "Rader"
        API_KEY_ODDS = "f849ec6e23b62fbf2f9df1eb82ee9915"
        
        if aktualni_uzivatel != ADMIN_JMENO: 
            st.warning("Sem mají přístup pouze administrátoři.")
        else:
            st.subheader("⚙️ Ovládací panel administrátora")
            
            # --- 🎛️ SEKCE: ADMIN PŘEPÍNAČ FÁZE TURNAJE (BEZPEČNÝ ZÁPIS DO ZÁPASY V1) ---
            st.write("---")
            st.markdown("### 🎛️ Nastavení režimu turnaje")
            volba_rezimu = st.checkbox("🏆 AKTIVIVAT REŽIM PLAY-OFF (Skryje remízy, zablokuje remízová skóre)", value=je_playoff)
            
            if st.button("💾 ULOŽIT REŽIM TURNAJE", type="primary"):
                with st.spinner("Zapisuji režim turnaje do buňky V1 v listu Zápasy..."):
                    sheet_z_raw = client.open("Mistrovstvi_Tipovacka").worksheet("Zápasy")
                    hodnota_pro_zapis = "Ano" if volba_rezimu else "Ne"
                    sheet_z_raw.update("V1", [[hodnota_pro_zapis]])
                st.cache_data.clear()
                st.success("Režim turnaje byl úspěšně uložen a aplikován!")
                st.rerun()
            
            if st.button("🔄 Stáhnout čerstvé zápasy", type="secondary"):
                SPORT = "soccer_fifa_world_cup" 
                url = f"https://api.the-odds-api.com/v4/sports/{SPORT}/odds/?apiKey={API_KEY_ODDS}&regions=eu&markets=h2h"
                with st.spinner("Aktualizuji zápasy turnaje..."):
                    odpoved = requests.get(url)
                    if odpoved.status_code != 200: st.error("API selhalo"); st.stop()
                    data_api = odpoved.json()
                    
                    sheet_z = client.open("Mistrovstvi_Tipovacka").worksheet("Zápasy")
                    zapasy_stavejici = sheet_z.get_all_records()
                    hlavicka_zapasy = ["ID", "Domaci", "Hoste", "Datum", "Kurz_1", "Kurz_X", "Kurz_2", "O05", "U05", "O15", "U15", "O25", "U25", "O35", "U35", "O45", "U45", "O55", "U55", "Vysledek", "Stav"]
                    
                    max_id = 0
                    mapa_zapasu = {}
                    for zp in zapasy_stavejici:
                        try:
                            id_val = int(zp.get("ID", 0))
                            if id_val > max_id: max_id = id_val
                        except: pass
                        klic = f"{zp.get('Domaci')} vs {zp.get('Hoste')}"
                        mapa_zapasu[klic] = zp

                    for zapas in data_api:
                        domaci, hoste = zapas["home_team"], zapas["away_team"]
                        klic_zapasu = f"{domaci} vs {hoste}"
                        cas_api_str = zapas.get("commence_time", "")
                        datum_formatovane = ""
                        if cas_api_str:
                            cas_cz = datetime.strptime(cas_api_str, "%Y-%m-%dT%H:%M:%SZ") + timedelta(hours=2)
                            datum_formatovane = cas_cz.strftime("%d.%m. %H:%M")

                        k_1, k_x, k_2 = "", "", ""
                        if zapas.get("bookmakers"):
                            for trh in zapas["bookmakers"][0]["markets"]:
                                if trh["key"] == "h2h":
                                    for t in trh["outcomes"]:
                                        if t["name"] == domaci: k_1 = t["price"]
                                        elif t["name"] == hoste: k_2 = t["price"]
                                        elif t["name"] == "Draw": k_x = t["price"]

                        if klic_zapasu in mapa_zapasu:
                            if str(mapa_zapasu[klic_zapasu].get("Stav")).lower() == "aktivni":
                                if str(k_1) != "": mapa_zapasu[klic_zapasu]["Kurz_1"] = k_1
                                if str(k_x) != "": mapa_zapasu[klic_zapasu]["Kurz_X"] = k_x
                                if str(k_2) != "": mapa_zapasu[klic_zapasu]["Kurz_2"] = k_2
                                if datum_formatovane: mapa_zapasu[klic_zapasu]["Datum"] = datum_formatovane
                        else:
                            max_id += 1
                            mapa_zapasu[klic_zapasu] = {
                                "ID": max_id, "Domaci": domaci, "Hoste": hoste, "Datum": datum_formatovane if datum_formatovane else "Čas neupřesněn",
                                "Kurz_1": k_1, "Kurz_X": k_x, "Kurz_2": k_2, "O05":"", "U05":"", "O15":"", "U15":"", "O25":"", "U25":"", "O35":"", "U35":"", "O45":"", "U45":"", "O55":"", "U55":"",
                                "Vysledek": "", "Stav": "aktivni"
                            }

                    vsechny_zapasy_obj = list(mapa_zapasu.values())
                    try: vsechny_zapasy_obj = sorted(vsechny_zapasy_obj, key=lambda x: int(x["ID"]))
                    except: pass

                    finalni_radky = []
                    for k in vsechny_zapasy_obj:
                        finalni_radky.append([
                            k.get("ID"), k.get("Domaci"), k.get("Hoste"), k.get("Datum"), k.get("Kurz_1"), k.get("Kurz_X"), k.get("Kurz_2"),
                            "","","","","","","","","","","","", k.get("Vysledek",""), k.get("Stav","aktivni")
                        ])

                    sheet_z.clear()
                    sheet_z.append_rows([hlavicka_zapasy] + finalni_radky)
                    st.cache_data.clear(); st.success("✅ Kurzová nabídka synchronizována!"); st.rerun()

            st.markdown("---")
            st.markdown("### 🏆 Vyhodnocení zápasů (Bodový řád 4-2-2)")
            
            if st.button("🏆 Vypočítat a zapsat fixní body", type="primary"):
                SPORT = "soccer_fifa_world_cup"
                url_scores = f"https://api.the-odds-api.com/v4/sports/{SPORT}/scores/?apiKey={API_KEY_ODDS}&daysFrom=3"
                
                with st.spinner("Zjišťuji oficiální stavy a skóre..."):
                    odpoved_scores = requests.get(url_scores)
                    if odpoved_scores.status_code != 200: st.error("API selhalo"); st.stop()
                    data_scores = odpoved_scores.json()
                    
                    dokoncene = {}
                    for z in data_scores:
                        if z.get("completed") and len(z.get("scores", [])) == 2:
                            d_tym, a_tym = z["home_team"], z["away_team"]
                            g_d = next((int(s["score"]) for s in z["scores"] if s["name"] == d_tym), 0)
                            g_h = next((int(s["score"]) for s in z["scores"] if s["name"] != d_tym), 0)
                            dokoncene[f"{d_tym} vs {a_tym}"] = {"home": g_d, "away": g_h}
                    
                    sheet_z = client.open("Mistrovstvi_Tipovacka").worksheet("Zápasy")
                    zapasy_z_tabulky = sheet_z.get_all_records()
                    
                    sheet_s = client.open("Mistrovstvi_Tipovacka").worksheet("Sázky")
                    sazky_list = sheet_s.get_all_records()
                    hlavicka_s = ["Uzivatel", "ID_zapasu", "Zapas", "Tip_Hlavni", "Tip_Skore", "Stav_Hlavni", "Stav_Skore", "Body_Ziskane", "Stav_Tipu", "Zolik"]
                    
                    body_pro_hrace = {}
                    zmeny_v_zapasech = False
                    
                    for j, zp in enumerate(zapasy_z_tabulky):
                        if str(zp.get("Stav")).lower() == "aktivni":
                            klic = f"{zp.get('Domaci')} vs {zp.get('Hoste')}"
                            manualni = str(zp.get("Vysledek", "")).strip()
                            if ":" in manualni:
                                zapasy_z_tabulky[j]["Stav"] = "ukonceno"
                                zmeny_v_zapasech = True
                            elif klic in dokoncene:
                                zapasy_z_tabulky[j]["Vysledek"] = f"{dokoncene[klic]['home']}:{dokoncene[klic]['away']}"
                                zapasy_z_tabulky[j]["Stav"] = "ukonceno"
                                zmeny_v_zapasech = True
                    
                    mapa_zapasu = {str(zp["ID"]): zp for zp in zapasy_z_tabulky}
                    
                    # 🔥 MATEMATICKÝ VÝPOČET BODOVÁNÍ 🔥
                    for i, s in enumerate(sazky_list):
                        if str(s.get("Stav_Tipu", s.get("Stav_Tiketu", ""))).lower() == "ceka":
                            z_id = str(s.get("ID_zapasu"))
                            info_zapas = mapa_zapasu.get(z_id, {})
                            vysledek_zapasu = str(info_zapas.get("Vysledek", "")).strip()
                            
                            if ":" in vysledek_zapasu:
                                try:
                                    # Oficiální skóre z API (u Play-off automaticky s přičteným penalty gólem)
                                    real_home, real_away = map(int, vysledek_zapasu.split(":"))
                                    real_1x2 = "1" if real_home > real_away else ("2" if real_home < real_away else "X")
                                    
                                    t_hlavni = str(s.get("Tip_Hlavni", s.get("Tip_1X2", "")))
                                    tip_skore_str = str(s.get("Tip_Skore", s.get("Kurz_1X2", "0:0")))
                                    tip_home, tip_away = map(int, tip_skore_str.split(":"))
                                    
                                    # Vyhodnocení hlavní sázky (1, X, 2, 10, 02)
                                    hlavni_vyhra = False
                                    if t_hlavni == real_1x2: hlavni_vyhra = True
                                    elif t_hlavni == "10" and real_1x2 in ["1", "X"]: hlavni_vyhra = True
                                    elif t_hlavni == "02" and real_1x2 in ["2", "X"]: hlavni_vyhra = True
                                    
                                    body_zisk = 0.0
                                    s_hlavni = "prohra"
                                    s_skore = "prohra"
                                    
                                    # 1. VYHODNOCENÍ HLAVNÍ SÁZKY
                                    if hlavni_vyhra:
                                        s_hlavni = "vyhra"
                                        if t_hlavni in ["1", "2"]: body_zisk += 2.0
                                        elif t_hlavni == "X": body_zisk += 3.0
                                        elif t_hlavni in ["10", "02"]: body_zisk += 1.0
                                        
                                    # 2. KOMPLETNĚ NEZÁVISLÉ VYHODNOCENÍ SKÓRE (PRO VŠECHNY!)
                                    if tip_home == real_home and tip_away == real_away:
                                        body_zisk += 4.0
                                        s_skore = "presne"
                                    elif real_1x2 == "X" and tip_home == tip_away:
                                        body_zisk += 2.0
                                        s_skore = "remiza_ostatni"
                                    elif (tip_home - tip_away) == (real_home - real_away):
                                        body_zisk += 2.0
                                        s_skore = "rozdil"
                                    
                                    # Žolík násobič
                                    if str(s.get("Zolik", "Ne")).lower() == "ano":
                                        body_zisk = body_zisk * 2
                                    
                                    # Rekonstrukce slovníku pro uložení
                                    sazky_list[i] = {
                                        "Uzivatel": s["Uzivatel"], "ID_zapasu": z_id, "Zapas": s["Zapas"],
                                        "Tip_Hlavni": t_hlavni, "Tip_Skore": tip_skore_str,
                                        "Stav_Hlavni": s_hlavni, "Stav_Skore": s_skore,
                                        "Body_Ziskane": round(body_zisk, 2), "Stav_Tipu": "vyhodnoceno",
                                        "Zolik": s.get("Zolik", "Ne")
                                    }
                                    
                                    hrace = s["Uzivatel"]
                                    body_pro_hrace[hrace] = body_pro_hrace.get(hrace, 0.0) + body_zisk
                                except: pass
                    
                    # Zápis do Google tabulky
                    data_sazky_zapis = []
                    for r in sazky_list:
                        data_sazky_zapis.append([r.get("Uzivatel"), r.get("ID_zapasu"), r.get("Zapas"), r.get("Tip_Hlavni"), r.get("Tip_Skore"), r.get("Stav_Hlavni"), r.get("Stav_Skore"), r.get("Body_Ziskane"), r.get("Stav_Tipu"), r.get("Zolik")])
                    
                    sheet_s.clear()
                    sheet_s.append_rows([hlavicka_s] + data_sazky_zapis)
                    
                    if zmeny_v_zapasech:
                        hlavicka_z = ["ID", "Domaci", "Hoste", "Datum", "Kurz_1", "Kurz_X", "Kurz_2", "O05","U05","O15","U15","O25","U25","O35","U35","O45","U45","O55","U55", "Vysledek", "Stav"]
                        data_zapasy_zapis = [list(r.values()) for r in zapasy_z_tabulky]
                        sheet_z.clear()
                        sheet_z.append_rows([hlavicka_z] + data_zapasy_zapis)
                    
                    # Distribuce bodů uživatelům
                    if body_pro_hrace:
                        sheet_u = client.open("Mistrovstvi_Tipovacka").worksheet("Uzivatele")
                        u_list = sheet_u.get_all_records()
                        for i, r in enumerate(u_list):
                            jm = str(r["Jméno"])
                            if jm in body_pro_hrace:
                                novy_sum = float(r["Body"]) + body_pro_hrace[jm]
                                sheet_u.update_cell(i + 2, 3, round(novy_sum, 2))
                                st.balloons()
                    
                    st.cache_data.clear(); st.success("✅ Všechny hotové sázky přepočítány!"); st.rerun()
