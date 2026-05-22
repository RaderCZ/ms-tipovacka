import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests
from datetime import datetime, timedelta

# --- 🎨 TUNING IFORTUNA.CZ + FONT ROBOTO (ABSOLUTNÍ FIX PRO TEXTY TLAČÍTEK PŘI HOVERU) ---
st.set_page_config(page_title="Naše MS Tipovačka", page_icon="⚽", layout="centered")

st.markdown("""
    <style>
    /* IMPORT EXKLUZIVNÍCH FONTŮ Z GOOGLE FONTS (STAATLICHES + ROBOTO) */
    @import url('https://fonts.googleapis.com/css2?family=Staatliches&family=Roboto:wght@400;500;700&display=swap');

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
    
    /* Tlačítko odhlášení v sidebaru (Výchozí stav) */
    [data-testid="stSidebar"] .stButton button {
        background-color: #262626 !important;
        border: 1px solid #333333 !important;
        color: #FF4B4B !important;
        border-radius: 4px !important;
        width: 100% !important;
    }
    /* 🚨 HOVER FIX PRO SIDEBAR TLAČÍTKO (Odhlásit se) - po najetí zežlutí a text ZČERNÁ */
    [data-testid="stSidebar"] .stButton button:hover,
    [data-testid="stSidebar"] .stButton button:hover *,
    [data-testid="stSidebar"] .stButton button:hover p,
    [data-testid="stSidebar"] .stButton button:hover span {
        background-color: #FFF200 !important;
        color: #000000 !important;
    }

    /* 3. VSTUPNÍ POLE A FORMULÁŘE */
    div[data-testid="stTextInput"] input {
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

    /* 4. TLAČÍTKA - ABSOLUTNÍ NEPRŮSTŘELNÝ HOVER FIX PRO TEXTY ⬛🟡 */
    div.stButton > button {
        border-radius: 4px !important;
        font-weight: 800 !important;
        letter-spacing: 0.5px !important;
        text-transform: uppercase !important;
        transition: all 0.15s ease-in-out !important;
    }
    
    /* Žluté sázkové tlačítko Fortuna (Výchozí stav) */
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
    /* Žluté sázkové tlačítko Fortuna (Hover stav) */
    div.stButton > button[kind="primary"]:hover,
    div.stButton > button[kind="primary"]:hover *,
    div.stButton > button[kind="primary"]:hover p,
    div.stButton > button[kind="primary"]:hover span {
        background-color: #FFE600 !important;
        color: #000000 !important;
        box-shadow: 0 4px 14px rgba(255, 242, 0, 0.3) !important;
    }
    
    /* Sekundární tlačítka - Přihlásit se / Admin (Výchozí stav) */
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
    /* 🚨 HOVER FIX PRO SEKUNDÁRNÍ TLAČÍTKA (Přihlásit se) - po najetí zežlutí a text ZČERNÁ */
    div.stButton > button[kind="secondary"]:hover,
    div.stButton > button[kind="secondary"]:hover *,
    div.stButton > button[kind="secondary"]:hover p,
    div.stButton > button[kind="secondary"]:hover span {
        background-color: #FFF200 !important;
        color: #000000 !important;
        border-color: #FFF200 !important;
    }

    /* Schování nástrojů u grafu */
    div[data-testid="stChartToolbar"] button:not(:first-child) {
        display: none !important;
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
    
    /* 7. INFORMAČNÍ LIŠTY */
    div[data-testid="stNotification"] {
        background-color: #1A1A1A !important;
        border: 1px solid #2D2D2D !important;
        border-left: 5px solid #FFF200 !important;
        border-radius: 6px !important;
    }
    div[data-testid="stNotification"] p {
        color: #FFFFFF !important;
    }
    </style>
""", unsafe_allow_html=True)


# --- NAPOJENÍ NA GOOGLE TABULKY (HYBRIDNÍ PRO LOKÁL I ONLINE) ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

if "gspread_creds" in st.secrets:
    # Online verze na serveru (vezme si klíč z tajného nastavení Streamlitu)
    import json
    creds_dict = dict(st.secrets["gspread_creds"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
else:
    # Lokální verze u tebe v PC
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)

client = gspread.authorize(creds)

# --- 🧠 PAMĚŤOVÉ FUNKCE (OCHRANA PŘED ERROR 429) ---
@st.cache_data(ttl=30)
def nacti_uzivatele():
    return client.open("Mistrovstvi_Tipovacka").worksheet("Uzivatele").get_all_records()

@st.cache_data(ttl=30)
def nacti_zapasy():
    return client.open("Mistrovstvi_Tipovacka").worksheet("Zápasy").get_all_records()

@st.cache_data(ttl=30)
def nacti_sazky():
    return client.open("Mistrovstvi_Tipovacka").worksheet("Sázky").get_all_records()

# --- NAČTENÍ DATA PŘES PAMĚŤ ---
data_uzivatele = nacti_uzivatele()
UZIVATELE = {}
for radek in data_uzivatele:
    jmeno = str(radek["Jméno"])
    heslo = str(radek["Heslo"])
    body = radek["Body"]
    UZIVATELE[jmeno] = {"heslo": heslo, "body": body}

# --- HLAVNÍ TITULEK ---
st.title("⚽ MS Fotbal - Kurzová Tipovačka")

if "prihlasen" not in st.session_state:
    st.session_state["prihlasen"] = False
    st.session_state["uzivatel"] = ""

# ==========================================
# OBRAZOVKA: PŘIHLÁŠENÍ
# ==========================================
if not st.session_state["prihlasen"]:
    st.subheader("Přihlášení do systému")
    jmeno = st.text_input("Jméno")
    heslo = st.text_input("Heslo", type="password")
    
    if st.button("Přihlásit se", type="secondary"):
        if jmeno in UZIVATELE and UZIVATELE[jmeno]["heslo"] == heslo:
            st.session_state["prihlasen"] = True
            st.session_state["uzivatel"] = jmeno
            st.success(f"Vítej, {jmeno}!")
            st.rerun()
        else:
            st.error("Nesprávné jméno nebo heslo!")

# ==========================================
# OBRAZOVKA: PO PŘIHLÁŠENÍ
# ==========================================
else:
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
    aktualni_body = UZIVATELE[aktualni_uzivatel]["body"]
    
    # --- SIDEBAR ---
    st.sidebar.write(f"👤 Přihlášen: **{aktualni_uzivatel}**")
    st.sidebar.write(f"✨ Tvoje body: **{aktualni_body} b.**")
    
    if st.sidebar.button("Odhlásit se"):
        st.session_state["prihlasen"] = False
        st.session_state["uzivatel"] = ""
        st.rerun()
        
    st.sidebar.markdown("---")
    st.sidebar.subheader("🏆 Průběžné pořadí")
    
    serazeni_hraci = sorted(UZIVATELE.items(), key=lambda x: x[1]['body'], reverse=True)
    medaile = ["🥇", "🥈", "🥉"]
    for i, (jm, dt) in enumerate(serazeni_hraci):
        znak = medaile[i] if i < len(medaile) else "🏅"
        if jm == aktualni_uzivatel:
            st.sidebar.markdown(f"**{i+1}\. {znak} {jm} — {dt['body']} b.**")
        else:
            st.sidebar.markdown(f"{i+1}\. {znak} {jm} — {dt['body']} b.")

    vsechny_sazky = nacti_sazky()
    moje_sazky = [s for s in vsechny_sazky if str(s.get("Uzivatel", "")) == aktualni_uzivatel]
    data_zapasy = nacti_zapasy()

    # ==========================================
    # 🛠 POMOCNÁ FUNKCE PRO VYKRESLENÍ DETAILU ZÁPASU
    # ==========================================
    def vykresli_detail_zapasu(z, zapas_uzamcen, moje_sazky):
        stavajici_tip = next((s for s in moje_sazky if str(s.get("ID_zapasu")) == str(z["ID"])), None)
        t_domaci = dej_data_tymu(z['Domaci'])
        t_hoste = dej_data_tymu(z['Hoste'])
        has_draw = str(z.get("Kurz_X", "")).strip() != ""
        
        titulek_radku = f"📅 {z.get('Datum', '')} | {t_domaci['jmeno']} vs {t_hoste['jmeno']}"
        if zapas_uzamcen: titulek_radku = f"🔒 {titulek_radku} (TIPY UZAVŘENY)"
        
        with st.expander(titulek_radku):
            st.write("")
            if not has_draw:
                st.warning("🚨 **PLAY-OFF ZÁPAS:** Sázka na remízu není možná. Tipuje se **VÍTĚZ DO ROZHODNUTÍ**.")
            
            # --- START: VLAJKY VEDLE SEBE (FLEXBOX) ---
            img_domaci = f"<img src='https://flagcdn.com/w160/{t_domaci['kod']}.png' width='70' style='border-radius: 4px;'><br>" if t_domaci['kod'] != "un" else ""
            img_hoste = f"<img src='https://flagcdn.com/w160/{t_hoste['kod']}.png' width='70' style='border-radius: 4px;'><br>" if t_hoste['kod'] != "un" else ""
            
            html_vlajky = f"""
            <div style='display: flex; justify-content: space-between; align-items: center; width: 100%; margin-top: 10px;'>
                <div style='flex: 1; text-align: center;'>
                    {img_domaci}
                    <div style='font-size: 20px; font-weight: bold; margin-top: 5px;'>{t_domaci['jmeno']}</div>
                </div>
                <div style='flex: 0.5; text-align: center;'>
                    <h2 style='color: #888888; margin: 0;'>VS</h2>
                </div>
                <div style='flex: 1; text-align: center;'>
                    {img_hoste}
                    <div style='font-size: 20px; font-weight: bold; margin-top: 5px;'>{t_hoste['jmeno']}</div>
                </div>
            </div>
            """
            st.markdown(html_vlajky, unsafe_allow_html=True)
            st.markdown("---")
            # --- KONEC: VLAJKY VEDLE SEBE ---
            
            if zapas_uzamcen:
                if stavajici_tip:
                    st.success("🔒 Tipy jsou uzavřeny. Zde je tvůj zapsaný tiket:")
                    c1, c2 = st.columns(2)
                    with c1:
                        if stavajici_tip['Tip_1X2'] == "X": tip_moj_1x2 = "Remíza"
                        else:
                            tip_moj_1x2 = f"Výhra {t_domaci['jmeno']}" if stavajici_tip['Tip_1X2'] == "1" else f"Výhra {t_hoste['jmeno']}"
                            if not has_draw: tip_moj_1x2 += " (do rozhodnutí)"
                        st.info(f"**Výsledek zápasu:** {tip_moj_1x2}")
                    with c2:
                        tip_moj_goly = f"{stavajici_tip['Tip_Goly']} než 2.5 gólu" if stavajici_tip['Tip_Goly'] != "Nenasazeno" else "Nevsadil góly"
                        st.info(f"**Počet gólů (2.5):** {tip_moj_goly}")
                else: st.warning("🔒 Zápas již odstartoval. Tento zápas jsi nestihl natipovat.")
            else:
                if stavajici_tip: st.warning("⚠️ Na tento zápas už máš vsazeno. Níže můžeš svůj tip kdykoliv upravit.")
                else: st.write("Navol si své tipy níže:")
                    
                moznat_1x2 = ["1", "X", "2"] if has_draw else ["1", "2"]
                moznat_goly = ["Více", "Méně"]
                idx_1x2 = moznat_1x2.index(str(stavajici_tip["Tip_1X2"])) if stavajici_tip and str(stavajici_tip["Tip_1X2"]) in moznat_1x2 else 0
                idx_goly = moznat_goly.index(str(stavajici_tip["Tip_Goly"])) if stavajici_tip and str(stavajici_tip["Tip_Goly"]) in moznat_goly else 0
                
                col1, col2 = st.columns(2)
                ma_1x2 = str(z.get("Kurz_1", "")).strip() != ""
                volba_1x2 = "Nenasazeno"
                k_1x2 = 0.0
                with col1:
                    st.write("**Výsledek zápasu**")
                    if ma_1x2:
                        volba_1x2 = st.radio(
                            "Tip na vítěze:", moznat_1x2, index=idx_1x2,
                            format_func=lambda x: f"1 ({t_domaci['jmeno']} @ {z['Kurz_1']})" if x=="1" and has_draw else (
                                f"1 (Postup: {t_domaci['jmeno']} @ {z['Kurz_1']})" if x=="1" and not has_draw else (
                                    f"X (Remíza @ {z['Kurz_X']})" if x=="X" else (
                                        f"2 ({t_hoste['jmeno']} @ {z['Kurz_2']})" if x=="2" and has_draw else f"2 (Postup: {t_hoste['jmeno']} @ {z['Kurz_2']})"
                                    )
                                )
                            ), key=f"r_1x2_{z['ID']}"
                        )
                        k_1x2 = float(z['Kurz_1']) if volba_1x2 == "1" else (float(z['Kurz_X']) if volba_1x2 == "X" else float(z['Kurz_2']))
                    else: st.warning("⚠️ Kurzy na vítěze nejsou k dispozici.")
                
                ma_goly = str(z.get("O25", "")).strip() != ""
                volba_goly = "Nenasazeno"
                k_goly = 0.0
                with col2:
                    st.write("**Počet gólů (Hranice 2.5)**")
                    if ma_goly:
                        volba_goly = st.radio(
                            "Tip na góly:", moznat_goly, index=idx_goly,
                            format_func=lambda x: f"Více než 2.5 g. (@ {z['O25']})" if x=="Více" else f"Méně než 2.5 g. (@ {z['U25']})",
                            key=f"r_g_{z['ID']}"
                        )
                        k_goly = float(z['O25']) if volba_goly == "Více" else float(z['U25'])
                    else: st.info("ℹ️ Kurzy na góly nejsou k dispozici.")
                        
                max_body = round(k_1x2 + k_goly, 2)
                if ma_1x2 or ma_goly:
                    st.info(f"💡 Potenciální zisk v případě úspěchu: **{max_body} bodů**.")
                    text_tlacitka = "🔄 AKTUALIZOVAT TIKET" if stavajici_tip else "💾 VSADIT TIKET"
                    
                    if st.button(text_tlacitka, key=f"btn_{z['ID']}", type="primary"):
                        sheet_sazky = client.open("Mistrovstvi_Tipovacka").worksheet("Sázky")
                        vsechny_sazky_aktualni = sheet_sazky.get_all_records()
                        
                        radek_pro_zapis = None
                        for idx, s in enumerate(vsechny_sazky_aktualni):
                            if str(s.get("Uzivatel")) == aktualni_uzivatel and str(s.get("ID_zapasu")) == str(z["ID"]):
                                radek_pro_zapis = idx + 2
                                break
                        
                        novy_radek = [
                            aktualni_uzivatel, z['ID'], f"{t_domaci['jmeno']}-{t_hoste['jmeno']}",
                            volba_1x2, k_1x2, volba_goly, k_goly,
                            "ceka" if ma_1x2 else "prohra", "ceka" if ma_goly else "prohra", 0, "ceka"
                        ]
                        with st.spinner("Odesílám tiket..."):
                            if radek_pro_zapis: sheet_sazky.update(f"A{radek_pro_zapis}:K{radek_pro_zapis}", [novy_radek])
                            else: sheet_sazky.append_row(novy_radek)
                                
                        st.cache_data.clear()
                        st.success("Tiket byl podán!")
                        st.rerun()

    tab1, tab2, tab3 = st.tabs(["🔮 Kurzová nabídka", "📜 Moje tipy", "⚙️ Admin"])

    # ==========================================
    # ZÁLOŽKA 1: KURZOVÁ NABÍDKA
    # ==========================================
    with tab1:
        st.subheader("🔮 Nabídka zápasů")
        
        skupina_dnesni, skupina_nadchazejici, skupina_odehrane = [], [], []
        dnes_str = datetime.now().strftime("%d.%m.")
        
        for z in data_zapasy:
            if str(z.get("Stav", "")).lower() == "aktivni" and str(z.get("ID", "")).strip() != "":
                z_datum_str = z.get("Datum", "")
                zapas_uzamcen, je_dnes, je_v_minulosti = False, False, False
                try:
                    match_dt = datetime.strptime(f"{z_datum_str}.2026", "%d.%m. %H:%M.%Y")
                    if datetime.now() >= (match_dt - timedelta(minutes=1)): zapas_uzamcen = True
                    if datetime.now() >= match_dt: je_v_minulosti = True
                    if match_dt.date() == datetime.now().date(): je_dnes = True
                except:
                    if z_datum_str.startswith(dnes_str): je_dnes = True
                
                is_vyhodnoceno = any(str(s.get("ID_zapasu")) == str(z["ID"]) and str(s.get("Stav_Tipu", "")).lower() == "vyhodnoceno" for s in vsechny_sazky)
                balicek = {"zapas": z, "uzamcen": zapas_uzamcen}
                
                if is_vyhodnoceno or (je_v_minulosti and not je_dnes): skupina_odehrane.append(balicek)
                elif je_dnes: skupina_dnesni.append(balicek)
                else: skupina_nadchazejici.append(balicek)
                    
        with st.expander("🔥 DNEŠNÍ ZÁPASY", expanded=True):
            if skupina_dnesni:
                for b in skupina_dnesni: vykresli_detail_zapasu(b["zapas"], b["uzamcen"], moje_sazky)
            else: st.info("Dnes se nehrají žádné zápasy.")
                
        with st.expander("📅 NADCHÁZEJÍCÍ ZÁPASY", expanded=False):
            if skupina_nadchazejici:
                for b in skupina_nadchazejici: vykresli_detail_zapasu(b["zapas"], b["uzamcen"], moje_sazky)
            else: st.info("Žádné další nadcházející zápasy v programu nejsou.")
                
        with st.expander("📁 ODEHRANÉ A VYHODNOCENÉ ZÁPASY", expanded=False):
            if skupina_odehrane:
                for b in skupina_odehrane: vykresli_detail_zapasu(b["zapas"], b["uzamcen"], moje_sazky)
            else: st.caption("Zatím nebyl odehrán ani vyhodnocen žádný zápas turnaje.")

    # ==========================================
    # ZÁLOŽKA 2: MATCH CENTER / GRAF SÁZEK
    # ==========================================
    with tab2:
        st.subheader("📝 Moje tipy a přehled sázek")
        st.write("Zde vidíš přehled svých tipů a úspěšnosti. Jakmile zápas reálně odstartuje, přímo pod tvým tipem uvidíš, jak sázeli ostatní.")
        
        # --- 📈 GRAPH S TOP FORTUNA STYLEM ---
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
            radek_grafu = {"Zápas": f"{cislo_zapasu}. {krasny_nazev_zapasu}"}
            for h in vsichni_hraci: radek_grafu[h] = round(text_stavy[h], 2)
            body_v_case.append(radek_grafu)
            
        if len(body_v_case) > 1:
            st.markdown("#### 📈 Grafický vývoj bodů")
            df_wide = pd.DataFrame(body_v_case)
            df_long = df_wide.melt(id_vars=["Zápas"], var_name="Hráč", value_name="Body")
            
            import altair as alt
            paleta_barev = ["#FFF200", "#00A4E4", "#FF4B4B", "#11998E", "#E0E0E0"]
            barvy_pro_graf = paleta_barev[:len(vsichni_hraci)]
            
            lines = alt.Chart(df_long).mark_line(interpolate="monotone", strokeWidth=4).encode(
                x=alt.X("Zápas:N", axis=alt.Axis(labelAngle=-45, title=None, grid=True, gridColor="#262626", labelColor="white")),
                y=alt.Y("Body:Q", axis=alt.Axis(title="Celkový počet bodů", grid=True, gridColor="#262626", labelColor="white", titleColor="white")),
                color=alt.Color("Hráč:N", scale=alt.Scale(domain=vsichni_hraci, range=barvy_pro_graf), legend=alt.Legend(title="Hráči", titleColor="white", labelColor="white")),
            )
            points = alt.Chart(df_long).mark_point(size=85, filled=True, stroke="#121212", strokeWidth=2).encode(
                x=alt.X("Zápas:N"), y=alt.Y("Body:Q"), color=alt.Color("Hráč:N"),
                tooltip=[alt.Tooltip("Hráč:N"), alt.Tooltip("Body:Q", title="Celkem bodů")]
            )
            konecny_graf = alt.layer(lines, points).properties(height=350, background="#1A1A1A").configure_view(strokeWidth=0)
            st.altair_chart(konecny_graf, use_container_width=True)
            st.markdown("<br>", unsafe_allow_html=True)
            
        # --- VÝPIS TIKETŮ ---
        for z in data_zapasy:
            if str(z.get("Stav", "")).lower() == "aktivni" and str(z.get("ID", "")).strip() != "":
                z_datum_str = z.get("Datum", "")
                zapas_uzamcen = False
                try:
                    match_dt = datetime.strptime(f"{z_datum_str}.2026", "%d.%m. %H:%M.%Y")
                    if datetime.now() >= (match_dt - timedelta(minutes=1)): zapas_uzamcen = True
                except: pass
                
                stavajici_tip = next((s for s in moje_sazky if str(s.get("ID_zapasu")) == str(z["ID"])), None)
                if zapas_uzamcen or stavajici_tip:
                    t_domaci = dej_data_tymu(z['Domaci'])
                    t_hoste = dej_data_tymu(z['Hoste'])
                    has_draw = str(z.get("Kurz_X", "")).strip() != ""
                    is_vyhodnoceno = stavajici_tip and str(stavajici_tip.get("Stav_Tipu", "")).lower() == "vyhodnoceno"
                    
                    if is_vyhodnoceno: titulek_radku = f"✅ {z.get('Datum', '')} | {t_domaci['jmeno']} vs {t_hoste['jmeno']} (+{stavajici_tip.get('Body_Ziskane', 0)} b.)"
                    elif zapas_uzamcen: titulek_radku = f"🔒 {z.get('Datum', '')} | {t_domaci['jmeno']} vs {t_hoste['jmeno']} (ZAČALO)"
                    else: titulek_radku = f"⏳ {z.get('Datum', '')} | {t_domaci['jmeno']} vs {t_hoste['jmeno']} (ČEKÁ NA VÝKOP)"
                        
                    with st.expander(titulek_radku):
                        st.write("")
                        v_col1, v_col2, v_col3 = st.columns([3, 1, 3])
                        with v_col1:
                            if t_domaci['kod'] != "un": st.markdown(f"<div style='text-align: center;'><img src='https://flagcdn.com/w160/{t_domaci['kod']}.png' width='70'></div>", unsafe_allow_html=True)
                            st.markdown(f"<div style='text-align: center; font-size: 22px; font-weight: bold; margin-top: 10px;'>{t_domaci['jmeno']}</div>", unsafe_allow_html=True)
                        with v_col2: st.markdown("<h2 style='text-align: center; color: #888888; margin-top: 20px;'>VS</h2>", unsafe_allow_html=True)
                        with v_col3:
                            if t_hoste['kod'] != "un": st.markdown(f"<div style='text-align: center;'><img src='https://flagcdn.com/w160/{t_hoste['kod']}.png' width='70'></div>", unsafe_allow_html=True)
                            st.markdown(f"<div style='text-align: center; font-size: 22px; font-weight: bold; margin-top: 10px;'>{t_hoste['jmeno']}</div>", unsafe_allow_html=True)
                        st.markdown("---")
                        
                        if stavajici_tip:
                            if is_vyhodnoceno: st.markdown(f"🏆 **Tiket vyhodnocen! Zisk: {stavajici_tip.get('Body_Ziskane', 0)} b.**")
                            else: st.markdown("**Tvůj podaný tiket:**")
                                
                            c1, c2 = st.columns(2)
                            with c1:
                                if stavajici_tip['Tip_1X2'] == "X": tip_moj_1x2 = "Remíza"
                                else:
                                    tip_moj_1x2 = f"Výhra {t_domaci['jmeno']}" if stavajici_tip['Tip_1X2'] == "1" else f"Výhra {t_hoste['jmeno']}"
                                    if not has_draw: tip_moj_1x2 += " (do rozhodnutí)"
                                i_1x2 = "🟢" if is_vyhodnoceno and stavajici_tip.get('Stav_1X2') == "vyhra" else ("🔴" if is_vyhodnoceno else "")
                                st.info(f"{i_1x2} **Výsledek:** {tip_moj_1x2} (kurz {stavajici_tip['Kurz_1X2']})")
                            with c2:
                                tip_moj_goly = f"{stavajici_tip['Tip_Goly']} než 2.5 gólu" if stavajici_tip['Tip_Goly'] != "Nenasazeno" else "Nevsadil góly"
                                i_goly = "🟢" if is_vyhodnoceno and stavajici_tip.get('Stav_Goly') == "vyhra" else ("🔴" if is_vyhodnoceno else "")
                                st.info(f"{i_goly} **Počet gólů (2.5):** {tip_moj_goly} (kurz {stavajici_tip['Kurz_Goly']})")
                        else: st.warning("⚠️ Tento zápas jsi nestihl natipovat.")
                            
                        if zapas_uzamcen:
                            st.write("")
                            st.markdown("**Jak sázeli ostatní:**")
                            tipy_ostatnich = [s for s in vsechny_sazky if str(s.get("ID_zapasu")) == str(z["ID"]) and str(s.get("Uzivatel")) != aktualni_uzivatel]
                            if tipy_ostatnich:
                                for t in tipy_ostatnich:
                                    if t['Tip_1X2'] == "X": tip_1x2_text = "Remíza"
                                    else:
                                        tip_1x2_text = f"Výhra {t_domaci['jmeno']}" if t['Tip_1X2'] == "1" else f"Výhra {t_hoste['jmeno']}"
                                        if not has_draw: tip_1x2_text += " (do rozhodnutí)"
                                    tip_goly_text = f"{t['Tip_Goly']} než 2.5 gólu" if t['Tip_Goly'] != "Nenasazeno" else "Nevsadil góly"
                                    st.write(f"👤 **{t['Uzivatel']}**: {tip_1x2_text} ({t['Kurz_1X2']}) | {tip_goly_text} ({t['Kurz_Goly']})")
                            else: st.caption("Nikdo jiný z hráčů na tento zápas nenasadil žádný tip.")                    

    # ==========================================
    # ZÁLOŽKA 3: ADMINISTRACE (OPRAVENÁ VERZE)
    # ==========================================
    with tab3:
        ADMIN_JMENO = "Rader"
        API_KEY_ODDS = "f849ec6e23b62fbf2f9df1eb82ee9915"
        
        if aktualni_uzivatel != ADMIN_JMENO: st.warning("Sem mají přístup pouze administrátoři.")
        else:
            st.subheader("⚙️ Ovládací panel administrátora")
            if st.button("🔄 Stáhnout čerstvé zápasy a kurzy", type="secondary"):
                SPORT = "soccer_fifa_world_cup" 
                # OPRAVENO: Odstraněn neplatný trh 'outcomes', stahujeme prověřenou klasiku
                url = f"https://api.the-odds-api.com/v4/sports/{SPORT}/odds/?apiKey={API_KEY_ODDS}&regions=eu&markets=h2h,totals"
                with st.spinner("Stahuji data..."):
                    odpoved = requests.get(url)
                    if odpoved.status_code != 200: st.error(f"Chyba: {odpoved.text}"); st.stop()
                    data = odpoved.json()
                    sloucene_zapasy = {}

                    for zapas in data:
                        domaci, hoste = zapas["home_team"], zapas["away_team"]
                        cas_api_str = zapas.get("commence_time", "")
                        if cas_api_str:
                            cas_cz = datetime.strptime(cas_api_str, "%Y-%m-%dT%H:%M:%SZ") + timedelta(hours=2)
                            datum_formatovane = cas_cz.strftime("%d.%m. %H:%M")
                        else: datum_formatovane = ""
                        klic_zapasu = f"{domaci} vs {hoste}"

                        if klic_zapasu not in sloucene_zapasy:
                            sloucene_zapasy[klic_zapasu] = {
                                "domaci": domaci, "hoste": hoste, "datum": datum_formatovane,
                                "k_1": "", "k_x": "", "k_2": "", "o25": "", "u25": ""
                            }
                        if datum_formatovane and not sloucene_zapasy[klic_zapasu]["datum"]: sloucene_zapasy[klic_zapasu]["datum"] = datum_formatovane
                        if zapas.get("bookmakers"):
                            for trh in zapas["bookmakers"][0]["markets"]:
                                if trh["key"] == "h2h":
                                    for t in trh["outcomes"]:
                                        if t["name"] == domaci: sloucene_zapasy[klic_zapasu]["k_1"] = t["price"]
                                        elif t["name"] == hoste: sloucene_zapasy[klic_zapasu]["k_2"] = t["price"]
                                        elif t["name"] == "Draw": sloucene_zapasy[klic_zapasu]["k_x"] = t["price"]
                                if trh["key"] == "totals":
                                    for t in trh["outcomes"]:
                                        if t.get("point") == 2.5:
                                            if t["name"] == "Over": sloucene_zapasy[klic_zapasu]["o25"] = t["price"]
                                            elif t["name"] == "Under": sloucene_zapasy[klic_zapasu]["u25"] = t["price"]

                    nové_zápasy = []
                    serazene_klice = sorted(sloucene_zapasy.keys(), key=lambda k: sloucene_zapasy[k]["datum"] if sloucene_zapasy[k]["datum"] else "99.99. 99:99")

                    for i, klic in enumerate(serazene_klice):
                        z = sloucene_zapasy[klic]
                        finilni_datum = z["datum"] if z["datum"] else "Čas neupřesněn"

                        nové_zápasy.append([
                            i + 1, z["domaci"], z["hoste"], finilni_datum, z["k_1"], z["k_x"], z["k_2"],
                            "", "", "", "", z["o25"], z["u25"], "", "", "", "", "", "", "", "aktivni"
                        ])
                    
                    if nové_zápasy:
                        hlavicka_zapasy = ["ID", "Domaci", "Hoste", "Datum", "Kurz_1", "Kurz_X", "Kurz_2", "O05", "U05", "O15", "U15", "O25", "U25", "O35", "U35", "O45", "U45", "O55", "U55", "Vysledek", "Stav"]
                        sheet_z = client.open("Mistrovstvi_Tipovacka").worksheet("Zápasy")
                        sheet_z.clear()
                        sheet_z.append_rows([hlavicka_zapasy] + nové_zápasy)
                        st.cache_data.clear(); st.success(f"Nahráno {len(nové_zápasy)} zápasů!"); st.rerun()

            st.markdown("---")

            if st.button("🏆 Vyhodnotit výsledky zápasů a rozdat body", type="secondary"):
                SPORT = "soccer_fifa_world_cup"
                url_scores = f"https://api.the-odds-api.com/v4/sports/{SPORT}/scores/?apiKey={API_KEY_ODDS}&daysFrom=3"
                with st.spinner("Vyhodnocuji..."):
                    odpoved_scores = requests.get(url_scores)
                    if odpoved_scores.status_code != 200: st.error(f"Chyba API: {odpoved_scores.text}"); st.stop()
                    data_scores = odpoved_scores.json()
                    dokoncene = {}
                    for z in data_scores:
                        if z.get("completed") and len(z.get("scores", [])) == 2:
                            d_tym = z["home_team"]
                            g_d = next((int(s["score"]) for s in z["scores"] if s["name"] == d_tym), 0)
                            g_h = next((int(s["score"]) for s in z["scores"] if s["name"] != d_tym), 0)
                            dokoncene[z["id"]] = {"home": g_d, "away": g_h}
                    
                    # OPRAVENO: Správný název listu v mapování, aby to nevyhodilo error na neexistující list
                    zapasy_z_tabulky = client.open("Mistrovstvi_Tipovacka").worksheet("Zápasy").get_all_records()
                    mapa_zapasu = {str(zp["ID"]): zp for zp in zapasy_z_tabulky}
                    sheet_s = client.open("Mistrovstvi_Tipovacka").worksheet("Sázky")
                    sazky_list = sheet_s.get_all_records()
                    hlavicka_s = list(sazky_list[0].keys()) if sazky_list else []
                    body_pro_hrace = {}
                    
                    for i, s in enumerate(sazky_list):
                        if str(s.get("Stav_Tipu")).lower() == "ceka":
                            z_id = str(s.get("ID_zapasu"))
                            info_zapas = mapa_zapasu.get(z_id, {})
                            has_draw = str(info_zapas.get("Kurz_X", "")).strip() != ""
                            manualni_vysledek = str(info_zapas.get("Vysledek", "")).strip()
                            
                            if z_id in dokoncene or manualni_vysledek in ["1", "X", "2"]:
                                h_g = dokoncene[z_id]["home"] if z_id in dokoncene else 0
                                a_g = dokoncene[z_id]["away"] if z_id in dokoncene else 0
                                total_g = h_g + a_g
                                body_zisk = 0.0
                                t_1x2 = str(s["Tip_1X2"])
                                v_1x2 = "prohra"
                                
                                skutecny_vysledek = ""
                                if manualni_vysledek in ["1", "X", "2"]: skutecny_vysledek = manualni_vysledek
                                elif z_id in dokoncene:
                                    if h_g > a_g: skutecny_vysledek = "1"
                                    elif h_g < a_g: skutecny_vysledek = "2"
                                    else: skutecny_vysledek = "X"
                                
                                if not has_draw and skutecny_vysledek == "X" and manualni_vysledek not in ["1", "2"]: continue
                                if t_1x2 == skutecny_vysledek: v_1x2 = "vyhra"; body_zisk += float(s["Kurz_1X2"])
                                
                                if z_id in dokoncene:
                                    t_g = str(s["Tip_Goly"])
                                    v_g = "prohra"
                                    if t_g == "Více" and total_g > 2.5: v_g = "vyhra"; body_zisk += float(s["Kurz_Goly"])
                                    elif t_g == "Méně" and total_g < 2.5: v_g = "vyhra"; body_zisk += float(s["Kurz_Goly"])
                                else: v_g = "prohra"
                                    
                                sazky_list[i]["Stav_1X2"] = v_1x2
                                sazky_list[i]["Stav_Goly"] = v_g
                                sazky_list[i]["Body_Ziskane"] = round(body_zisk, 2)
                                sazky_list[i]["Stav_Tipu"] = "vyhodnoceno"
                                hrace = s["Uzivatel"]
                                body_pro_hrace[hrace] = body_pro_hrace.get(hrace, 0.0) + body_zisk
                    
                    data_sazky_zapis = [list(r.values()) for r in sazky_list]
                    sheet_s.clear()
                    sheet_s.append_rows([hlavicka_s] + data_sazky_zapis)
                    
                    if body_pro_hrace:
                        sheet_u = client.open("Mistrovstvi_Tipovacka").worksheet("Uzivatele")
                        u_list = sheet_u.get_all_records()
                        for i, r in enumerate(u_list):
                            jm = str(r["Jméno"])
                            if jm in body_pro_hrace:
                                novy_sum = float(r["Body"]) + body_pro_hrace[jm]
                                sheet_u.update_cell(i + 2, 3, round(novy_sum, 2))
                                st.balloons(); st.success(f"🎉 {jm} získal {round(body_pro_hrace[jm], 2)} bodů!")
                    st.cache_data.clear(); st.success("✅ Vyhodnoceno!"); st.rerun()
