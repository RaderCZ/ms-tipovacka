import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests
from datetime import datetime, timedelta

# --- 🎨 TUNING IFORTUNA.CZ + FONT ROBOTO (ABSOLUTNÍ FIX PRO TEXTY TLAČÍTEK PŘI HOVERU) ---
st.set_page_config(page_title="MS 2026 - Tipovačka", page_icon="⚽", layout="centered")

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
    status = str(radek.get("Status", "")).strip() # Načte status, pokud existuje
    UZIVATELE[jmeno] = {"heslo": heslo, "body": body, "status": status}

# --- HLAVNÍ TITULEK ---
st.title("⚽ MS 26 TIPOVAČKA")

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
        "Curaçao": {"jmeno": "Curaçao", "kod": "cw"}, "Haiti": {"jmeno": "Haiti", "kod": "ht"}, "Panama": {"jmeno": "Panama", "kod": "pa"}, "New Zealand": {"jmeno": "Nový Zéland", "kod": "nz"},
        
     # --- MLS TÝMY PRO TESTOVÁNÍ ---
        "Atlanta United FC": {"jmeno": "Atlanta Utd", "kod": "us"},
        "Austin FC": {"jmeno": "Austin FC", "kod": "us"},
        "Charlotte FC": {"jmeno": "Charlotte FC", "kod": "us"},
        "Chicago Fire": {"jmeno": "Chicago Fire", "kod": "us"},
        "Chicago Fire FC": {"jmeno": "Chicago Fire", "kod": "us"},
        "FC Cincinnati": {"jmeno": "FC Cincinnati", "kod": "us"},
        "Colorado Rapids": {"jmeno": "Colorado Rapids", "kod": "us"},
        "Columbus Crew SC": {"jmeno": "Columbus Crew SC", "kod": "us"},
        "FC Dallas": {"jmeno": "FC Dallas", "kod": "us"},
        "D.C. United": {"jmeno": "D.C. United", "kod": "us"},
        "Houston Dynamo": {"jmeno": "Houston Dynamo", "kod": "us"},
        "Sporting Kansas City": {"jmeno": "Sporting KC", "kod": "us"},
        "LA Galaxy": {"jmeno": "LA Galaxy", "kod": "us"},
        "Los Angeles FC": {"jmeno": "Los Angeles FC", "kod": "us"},
        "Inter Miami CF": {"jmeno": "Inter Miami", "kod": "us"},
        "Minnesota United FC": {"jmeno": "Minnesota Utd", "kod": "us"},
        "CF Montreal": {"jmeno": "CF Montreal", "kod": "ca"},
        "Nashville SC": {"jmeno": "Nashville SC", "kod": "us"},
        "New England Revolution": {"jmeno": "NE Revolution", "kod": "us"},
        "New York City FC": {"jmeno": "New York City", "kod": "us"},
        "New York Red Bulls": {"jmeno": "NY Red Bulls", "kod": "us"},
        "Orlando City SC": {"jmeno": "Orlando City", "kod": "us"},
        "Philadelphia Union": {"jmeno": "Philadelphia", "kod": "us"},
        "Portland Timbers": {"jmeno": "Portland Timbers", "kod": "us"},
        "Real Salt Lake": {"jmeno": "Real Salt Lake", "kod": "us"},
        "San Diego FC": {"jmeno": "San Diego", "kod": "us"},
        "San Jose Earthquakes": {"jmeno": "San Jose", "kod": "us"},
        "Seattle Sounders FC": {"jmeno": "Seattle Sounders", "kod": "us"},
        "St. Louis City SC": {"jmeno": "St. Louis City", "kod": "us"},
        "Toronto FC": {"jmeno": "Toronto FC", "kod": "ca"},
        "Vancouver Whitecaps FC": {"jmeno": "Vancouver", "kod": "ca"}   
    }
    
    def dej_data_tymu(tym_z_api):
        return PREKLAD_TYMU.get(tym_z_api, {"jmeno": tym_z_api, "kod": "un"})
        
    aktualni_uzivatel = st.session_state["uzivatel"]
    aktualni_body = UZIVATELE[aktualni_uzivatel]["body"]
    
    # --- SIDEBAR ---
    st.sidebar.write(f"👤 Hráč: **{aktualni_uzivatel}**")
    st.sidebar.write(f"✨ Body: **{aktualni_body} b.**")
    
    if st.sidebar.button("Odhlásit se"):
        st.session_state["prihlasen"] = False
        st.session_state["uzivatel"] = ""
        st.rerun()
        
    # --- BANTER BOX: NASTAVENÍ STATUSU ---
    st.sidebar.write("")
    stuj_status = UZIVATELE[aktualni_uzivatel].get("status", "")
    novy_status = st.sidebar.text_input("💬 Rýpni si do ostatních:", value=stuj_status, max_chars=60, key="banter_input")
    
    if novy_status != stuj_status:
        if st.sidebar.button("💾 Uložit status", type="secondary", key="btn_uložit_status"):
            with st.spinner("Ukládám status..."):
                sheet_u = client.open("Mistrovstvi_Tipovacka").worksheet("Uzivatele")
                u_list = sheet_u.get_all_records()
                for i, r in enumerate(u_list):
                    if str(r["Jméno"]) == aktualni_uzivatel:
                        # Sloupec D je 4. sloupec v tabulce
                        sheet_u.update_cell(i + 2, 4, novy_status)
                        break
            st.cache_data.clear()
            st.rerun()    
        
    st.sidebar.markdown("---")
    st.sidebar.subheader("🏆 Průběžné pořadí")
    
    # --- OPRAVENÝ ŽEBŘÍČEK: ABSOLUTNÍ ZAROVNÁNÍ BEZ MARKDOWN CHYB ---
    serazeni_hraci = sorted(UZIVATELE.items(), key=lambda x: x[1]['body'], reverse=True)
    medaile = ["🥇", "🥈", "🥉"]
    
    for i, (jm, dt) in enumerate(serazeni_hraci):
        znak = medaile[i] if i < len(medaile) else "🏅"
        
        # Určíme styl podle toho, zda jde o přihlášeného uživatele (tučná žlutá) nebo ostatní (bílá)
        if jm == aktualni_uzivatel:
            styl_jmena = "font-weight: bold; color: #FFF200; font-size: 16px;"
        else:
            styl_jmena = "color: #FFFFFF; font-size: 16px;"
            
        # Vytvoření textu statusu s mírným odsazením zleva, aby seděl přesně pod jménem
        text_statusu = f"<div style='color: #aaaaaa; font-style: italic; font-size: 13px; margin-top: 2px; padding-left: 22px;'>„{dt['status']}“</div>" if dt['status'] else ""
        
        # Složení celého řádku do jednoho stabilního HTML bloku
        html_radek = f"""
        <div style='margin-bottom: 14px; line-height: 1.2;'>
            <span style='{styl_jmena}'>{i+1}. {znak} {jm} — {dt['body']} b.</span>
            {text_statusu}
        </div>
        """
        st.sidebar.markdown(html_radek, unsafe_allow_html=True)

    vsechny_sazky = nacti_sazky()
    moje_sazky = [s for s in vsechny_sazky if str(s.get("Uzivatel", "")) == aktualni_uzivatel]
    data_zapasy = nacti_zapasy()

    # ==========================================
    # 🛠 POMOCNÁ FUNKCE PRO VYKRESLENÍ DETAILU ZÁPASU (S ODPOČTEM ČASU)
    # ==========================================
    def vykresli_detail_zapasu(z, zapas_uzamcen, moje_sazky):
        stavajici_tip = next((s for s in moje_sazky if str(s.get("ID_zapasu")) == str(z["ID"])), None)
        t_domaci = dej_data_tymu(z['Domaci'])
        t_hoste = dej_data_tymu(z['Hoste'])
        has_draw = str(z.get("Kurz_X", "")).strip() != ""
        
        je_zapas_ukoncen = str(z.get("Stav", "")).lower() == "ukonceno"
        skore_text = f" ({z.get('Vysledek', '')})" if z.get('Vysledek') else ""
        
        # --- VÝPOČET ODPOČTU DO TITULKU ---
        odpocet_titulek = ""
        vnitrni_odpocet_html = ""
        
        if not je_zapas_ukoncen and not zapas_uzamcen:
            try:
                match_dt = datetime.strptime(f"{z.get('Datum', '')}.2026", "%d.%m. %H:%M.%Y")
                lock_dt = match_dt - timedelta(minutes=1) # Tipy se zamykají minutu před výkopem
                aktualni_cas = datetime.utcnow() + timedelta(hours=2) # Stabilní CZ čas
                diff = lock_dt - aktualni_cas
                
                if diff.total_seconds() > 0:
                    dny = diff.days
                    hodiny, sekundy = divmod(diff.seconds, 3600)
                    minuty, _ = divmod(sekundy, 60)
                    
                    # Nastavení barev a textů podle urgentnosti
                    if dny > 0:
                        cas_text = f"{dny} d. {hodiny} hod."
                        barva = "#888888" # Nenápadná šedá pro zápasy v dalších dnech
                    elif hodiny > 0:
                        cas_text = f"{hodiny} hod. {minuty} min."
                        barva = "#FFF200" # Fortuna žlutá (hraje se dneska!)
                        odpocet_titulek = f" ⏱️ ({hodiny}h {minuty}m)" # Přidáme i do zavřeného řádku
                    else:
                        cas_text = f"{minuty} minut!!"
                        barva = "#FF4B4B" # Výstražná červená (poslední hodina!)
                        odpocet_titulek = f" 🚨 ({minuty}m!)"
                    
                    vnitrni_odpocet_html = f"""
                    <div style='text-align: center; margin-top: -10px; margin-bottom: 15px; font-size: 13px; color: {barva}; font-weight: 500;'>
                        ⏳ Do uzamčení tipů zbývá: <span style='font-weight: bold; text-transform: uppercase;'>{cas_text}</span>
                    </div>
                    """
            except:
                pass
        
        # Dynamická tvorba titulku podle reálného stavu zápasu
        if je_zapas_ukoncen:
            titulek_radku = f"✅ {z.get('Datum', '')} | {t_domaci['jmeno']} vs {t_hoste['jmeno']}{skore_text} (ODEHRÁNO)"
        elif zapas_uzamcen:
            titulek_radku = f"🔒 {z.get('Datum', '')} | {t_domaci['jmeno']} vs {t_hoste['jmeno']} (TIPY UZAVŘENY)"
        else:
            titulek_radku = f"📅 {z.get('Datum', '')} | {t_domaci['jmeno']} vs {t_hoste['jmeno']}{odpocet_titulek}"
        
        with st.expander(titulek_radku):
            st.write("")
            if not has_draw:
                st.warning("🚨 **PLAY-OFF ZÁPAS:** Sázka na remízu není možná. Tipuje se **VÍTĚZ DO ROZHODNUTÍ**.")
            
            # --- START: VLAJKY VEDLE SEBE (FLEXBOX) ---
            img_domaci = f"<img src='https://flagcdn.com/w160/{t_domaci['kod']}.png' width='70' style='border-radius: 4px;'><br>" if t_domaci['kod'] != "un" else ""
            img_hoste = f"<img src='https://flagcdn.com/w160/{t_hoste['kod']}.png' width='70' style='border-radius: 4px;'><br>" if t_hoste['kod'] != "un" else ""
            
            if je_zapas_ukoncen and z.get('Vysledek'):
                stred_text = str(z.get('Vysledek'))
                stred_color = "#FFF200"
            else:
                stred_text = "VS"
                stred_color = "#888888"
            
            html_vlajky = f"""
            <div style='display: flex; justify-content: space-between; align-items: center; width: 100%; margin-top: 10px;'>
                <div style='flex: 1; text-align: center;'>{img_domaci}<div style='font-size: 20px; font-weight: bold; margin-top: 5px;'>{t_domaci['jmeno']}</div></div>
                <div style='flex: 0.5; text-align: center;'><h2 style='color: {stred_color}; margin: 0; letter-spacing: 0px;'>{stred_text}</h2></div>
                <div style='flex: 1; text-align: center;'>{img_hoste}<div style='font-size: 20px; font-weight: bold; margin-top: 5px;'>{t_hoste['jmeno']}</div></div>
            </div>
            """
            st.markdown(html_vlajky, unsafe_allow_html=True)
            st.markdown("---")
            # --- KONEC: VLAJKY VEDLE SEBE ---
            
            # Vykreslení vnitřního odpočtu (pokud je zápas aktivní)
            if vnitrni_odpocet_html:
                st.markdown(vnitrni_odpocet_html, unsafe_allow_html=True)
            
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

    tab1, tab2, tab3 = st.tabs(["📅 Kurzová nabídka", "📜 Moje tipy", "⚙️ Admin"])

    # ==========================================
    # ZÁLOŽKA 1: KURZOVÁ NABÍDKA
    # ==========================================
    with tab1:
        st.subheader("📅 Nabídka zápasů")
        
        # --- OPRAVA ČASU: Vynucení CZ času ---
        aktualni_cas = datetime.utcnow() + timedelta(hours=2)
        dnes_str = aktualni_cas.strftime("%d.%m.")
        
        skupina_dnesni, skupina_nadchazejici, skupina_odehrane = [], [], []
        
        for z in data_zapasy:
            if str(z.get("Stav", "")).lower() in ["aktivni", "ukonceno"] and str(z.get("ID", "")).strip() != "":
                z_datum_str = z.get("Datum", "")
                zapas_uzamcen, je_dnes, je_v_minulosti = False, False, False
                try:
                    match_dt = datetime.strptime(f"{z_datum_str}.2026", "%d.%m. %H:%M.%Y")
                    # Místo datetime.now() používáme náš aktualni_cas
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
    # ZÁLOŽKA 2: MATCH CENTER / GRAF SÁZEK
    # ==========================================
    with tab2:
        st.subheader("📜 Moje tipy a graf")
        st.write("Tady uvidíš své aktuální i vyhodnocené tipy spolu s grafem přírůstku bodů.")
        
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
        aktualni_cas = datetime.utcnow() + timedelta(hours=2) # OPRAVA ČASU
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
                
                # Rozšířená podmínka: Zobrazíme, pokud zápas začal, byl vsazen, NEBO je už ukončený
                if zapas_uzamcen or stavajici_tip or je_zapas_ukoncen:
                    t_domaci = dej_data_tymu(z['Domaci'])
                    t_hoste = dej_data_tymu(z['Hoste'])
                    has_draw = str(z.get("Kurz_X", "")).strip() != ""
                    is_vyhodnoceno = stavajici_tip and str(stavajici_tip.get("Stav_Tipu", "")).lower() == "vyhodnoceno"
                    
                    # HLAVNÍ FIX: Pokud je zápas ukončen turnajově NEBO vyhodnocen u hráče
                    if je_zapas_ukoncen or is_vyhodnoceno: 
                        body_zisk = stavajici_tip.get('Body_Ziskane', 0) if stavajici_tip else 0
                        skore_text = f" ({z.get('Vysledek', '')})" if z.get('Vysledek') else ""
                        titulek_radku = f"✅ {z.get('Datum', '')} | {t_domaci['jmeno']} vs {t_hoste['jmeno']}{skore_text} (+{body_zisk} b.)"
                    elif zapas_uzamcen: 
                        titulek_radku = f"🔒 {z.get('Datum', '')} | {t_domaci['jmeno']} vs {t_hoste['jmeno']} (ZAČALO)"
                    else: 
                        titulek_radku = f"⏳ {z.get('Datum', '')} | {t_domaci['jmeno']} vs {t_hoste['jmeno']} (ČEKÁ NA VÝKOP)"
                        
                    with st.expander(titulek_radku):
                        st.write("")
                        # --- START: VLAJKY VEDLE SEBE (FLEXBOX) PRO ZÁLOŽKU 2 ---
                        img_domaci = f"<img src='https://flagcdn.com/w160/{t_domaci['kod']}.png' width='70' style='border-radius: 4px;'><br>" if t_domaci['kod'] != "un" else ""
                        img_hoste = f"<img src='https://flagcdn.com/w160/{t_hoste['kod']}.png' width='70' style='border-radius: 4px;'><br>" if t_hoste['kod'] != "un" else ""
                        
                        # Dynamický text a barva pro středový prvek v Historii tipů
                        if je_zapas_ukoncen and z.get('Vysledek'):
                            stred_text = str(z.get('Vysledek'))
                            stred_color = "#FFF200" # Zářivě žlutá Fortuna pro konečné skóre
                        else:
                            stred_text = "VS"
                            stred_color = "#888888"
                        
                        html_vlajky = f"""
                        <div style='display: flex; justify-content: space-between; align-items: center; width: 100%; margin-top: 10px;'>
                            <div style='flex: 1; text-align: center;'>{img_domaci}<div style='font-size: 20px; font-weight: bold; margin-top: 5px;'>{t_domaci['jmeno']}</div></div>
                            <div style='flex: 0.5; text-align: center;'><h2 style='color: {stred_color}; margin: 0; letter-spacing: 0px;'>{stred_text}</h2></div>
                            <div style='flex: 1; text-align: center;'>{img_hoste}<div style='font-size: 20px; font-weight: bold; margin-top: 5px;'>{t_hoste['jmeno']}</div></div>
                        </div>
                        """
                        st.markdown(html_vlajky, unsafe_allow_html=True)
                        st.markdown("---")
                        # --- KONEC: VLAJKY VEDLE SEBE ---
                        
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
                                st.info(f"{i_goly} **Počet gólů:** {tip_moj_goly} (kurz {stavajici_tip['Kurz_Goly']})")
                        else: st.warning("⚠️ Tento zápas jsi bohužel nestihl natipovat.")
                            
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
                SPORT = "soccer_usa_mls" 
                url = f"https://api.the-odds-api.com/v4/sports/{SPORT}/odds/?apiKey={API_KEY_ODDS}&regions=eu&markets=h2h,totals"
                with st.spinner("Aktualizuji kurzovou nabídku..."):
                    odpoved = requests.get(url)
                    if odpoved.status_code != 200: st.error(f"Chyba API: {odpoved.text}"); st.stop()
                    data_api = odpoved.json()
                    
                    # 1. Načteme stávající zápasy z tabulky, abychom je NESMAZALI
                    sheet_z = client.open("Mistrovstvi_Tipovacka").worksheet("Zápasy")
                    zapasy_stavejici = sheet_z.get_all_records()
                    hlavicka_zapasy = ["ID", "Domaci", "Hoste", "Datum", "Kurz_1", "Kurz_X", "Kurz_2", "O05", "U05", "O15", "U15", "O25", "U25", "O35", "U35", "O45", "U45", "O55", "U55", "Vysledek", "Stav"]
                    
                    # Najdeme nejvyšší stávající ID a vytvoříme si index zápasů podle jména
                    max_id = 0
                    mapa_zapasu = {}
                    for zp in zapasy_stavejici:
                        try:
                            id_val = int(zp.get("ID", 0))
                            if id_val > max_id: max_id = id_val
                        except: pass
                        klic = f"{zp.get('Domaci')} vs {zp.get('Hoste')}"
                        mapa_zapasu[klic] = zp

                    # 2. Zpracujeme čerstvá data z API
                    for zapas in data_api:
                        domaci, hoste = zapas["home_team"], zapas["away_team"]
                        klic_zapasu = f"{domaci} vs {hoste}"
                        
                        cas_api_str = zapas.get("commence_time", "")
                        datum_formatovane = ""
                        if cas_api_str:
                            cas_cz = datetime.strptime(cas_api_str, "%Y-%m-%dT%H:%M:%SZ") + timedelta(hours=2)
                            datum_formatovane = cas_cz.strftime("%d.%m. %H:%M")

                        # Vytáhneme kurzy z API
                        k_1, k_x, k_2, o25, u25 = "", "", "", "", ""
                        if zapas.get("bookmakers"):
                            for trh in zapas["bookmakers"][0]["markets"]:
                                if trh["key"] == "h2h":
                                    for t in trh["outcomes"]:
                                        if t["name"] == domaci: k_1 = t["price"]
                                        elif t["name"] == hoste: k_2 = t["price"]
                                        elif t["name"] == "Draw": k_x = t["price"]
                                if trh["key"] == "totals":
                                    for t in trh["outcomes"]:
                                        if t.get("point") == 2.5:
                                            if t["name"] == "Over": o25 = t["price"]
                                            elif t["name"] == "Under": u25 = t["price"]

                        if klic_zapasu in mapa_zapasu:
                            # ZÁPAS UŽ MÁME: Pokud je stále aktivní, pouze aktualizujeme kurzy a čas
                            if str(mapa_zapasu[klic_zapasu].get("Stav")).lower() == "aktivni":
                                mapa_zapasu[klic_zapasu]["Kurz_1"] = k_1
                                mapa_zapasu[klic_zapasu]["Kurz_X"] = k_x
                                mapa_zapasu[klic_zapasu]["Kurz_2"] = k_2
                                mapa_zapasu[klic_zapasu]["O25"] = o25
                                mapa_zapasu[klic_zapasu]["U25"] = u25
                                if datum_formatovane: mapa_zapasu[klic_zapasu]["Datum"] = datum_formatovane
                        else:
                            # NOVÝ ZÁPAS: Přiřadíme mu nové unikátní ID a založíme ho
                            max_id += 1
                            mapa_zapasu[klic_zapasu] = {
                                "ID": max_id, "Domaci": domaci, "Hoste": hoste, "Datum": datum_formatovane if datum_formatovane else "Čas neupřesněn",
                                "Kurz_1": k_1, "Kurz_X": k_x, "Kurz_2": k_2, "O05": "", "U05": "", "O15": "", "U15": "",
                                "O25": o25, "U25": u25, "O35": "", "U35": "", "O45": "", "U45": "", "O55": "", "U55": "",
                                "Vysledek": "", "Stav": "aktivni"
                            }

                    # 3. Seřadíme zápasy podle ID, abychom udrželi chronologii
                    vsechny_zapasy_obj = list(mapa_zapasu.values())
                    try:
                        vsechny_zapasy_obj = sorted(vsechny_zapasy_obj, key=lambda x: int(x["ID"]))
                    except: pass

                    # Převod objektů zpět na čisté řádky pro Google Sheets
                    finalni_radky = []
                    for k in vsechny_zapasy_obj:
                        finalni_radky.append([
                            k.get("ID"), k.get("Domaci"), k.get("Hoste"), k.get("Datum"),
                            k.get("Kurz_1"), k.get("Kurz_X"), k.get("Kurz_2"),
                            k.get("O05",""), k.get("U05",""), k.get("O15",""), k.get("U15",""),
                            k.get("O25"), k.get("U25"),
                            k.get("O35",""), k.get("U35",""), k.get("O45",""), k.get("U45",""), k.get("O55",""), k.get("U55",""),
                            k.get("Vysledek",""), k.get("Stav","aktivni")
                        ])

                    # 4. Bezpečné přepsání celé tabulky (včetně zachování historie)
                    sheet_z.clear()
                    sheet_z.append_rows([hlavicka_zapasy] + finalni_radky)
                    st.cache_data.clear()
                    st.success("✅ Kurzová nabídka byla bezpečně aktualizována a nové zápasy přidány!")
                    st.rerun()

            st.markdown("---")

            if st.button("🏆 Vyhodnotit výsledky zápasů a rozdat body", type="secondary"):
                SPORT = "soccer_usa_mls"
                url_scores = f"https://api.the-odds-api.com/v4/sports/{SPORT}/scores/?apiKey={API_KEY_ODDS}&daysFrom=3"
                
                with st.spinner("Zjišťuji výsledky z API a Google Tabulky..."):
                    odpoved_scores = requests.get(url_scores)
                    if odpoved_scores.status_code != 200: st.error(f"Chyba API: {odpoved_scores.text}"); st.stop()
                    data_scores = odpoved_scores.json()
                    
                    # 1. Získáme oficiálně dokončené zápasy z API
                    dokoncene = {}
                    for z in data_scores:
                        if z.get("completed") and len(z.get("scores", [])) == 2:
                            d_tym, a_tym = z["home_team"], z["away_team"]
                            g_d = next((int(s["score"]) for s in z["scores"] if s["name"] == d_tym), 0)
                            g_h = next((int(s["score"]) for s in z["scores"] if s["name"] != d_tym), 0)
                            dokoncene[f"{d_tym} vs {a_tym}"] = {"home": g_d, "away": g_h}
                    
                    # 2. Načteme tabulky
                    sheet_z = client.open("Mistrovstvi_Tipovacka").worksheet("Zápasy")
                    zapasy_z_tabulky = sheet_z.get_all_records()
                    hlavicka_z = list(zapasy_z_tabulky[0].keys()) if zapasy_z_tabulky else []
                    
                    sheet_s = client.open("Mistrovstvi_Tipovacka").worksheet("Sázky")
                    sazky_list = sheet_s.get_all_records()
                    hlavicka_s = list(sazky_list[0].keys()) if sazky_list else []
                    
                    body_pro_hrace = {}
                    zmeny_v_zapasech = False
                    
                    # --- KROK A: AKTUALIZACE VŠECH ZÁPASŮ (NEZÁVISLE NA SÁZKÁCH) ---
                    for j, zp in enumerate(zapasy_z_tabulky):
                        if str(zp.get("Stav")).lower() == "aktivni":
                            z_id = str(zp.get("ID"))
                            jmeno_domaci = zp.get("Domaci", "")
                            jmeno_hoste = zp.get("Hoste", "")
                            klic_pro_hledani = f"{jmeno_domaci} vs {jmeno_hoste}"
                            manualni_vysledek = str(zp.get("Vysledek", "")).strip()
                            
                            # Kontrola manuálního skóre s dvojtečkou
                            if ":" in manualni_vysledek:
                                zapasy_z_tabulky[j]["Stav"] = "ukonceno"
                                zmeny_v_zapasech = True
                            # Kontrola automatického skóre z API
                            elif klic_pro_hledani in dokoncene:
                                h_g = dokoncene[klic_pro_hledani]["home"]
                                a_g = dokoncene[klic_pro_hledani]["away"]
                                zapasy_z_tabulky[j]["Vysledek"] = f"{h_g}:{a_g}"
                                zapasy_z_tabulky[j]["Stav"] = "ukonceno"
                                zmeny_v_zapasech = True
                    
                    # Vytvoříme si novou mapu zápasů už s doplněnými výsledky
                    mapa_zapasu = {str(zp["ID"]): zp for zp in zapasy_z_tabulky}
                    
                    # --- KROK B: VYHODNOCENÍ EXISTUJÍCÍCH SÁZEK ---
                    for i, s in enumerate(sazky_list):
                        if str(s.get("Stav_Tipu")).lower() == "ceka":
                            z_id = str(s.get("ID_zapasu"))
                            info_zapas = mapa_zapasu.get(z_id, {})
                            vysledek_zapasu = str(info_zapas.get("Vysledek", "")).strip()
                            has_draw = str(info_zapas.get("Kurz_X", "")).strip() != ""
                            
                            if ":" in vysledek_zapasu:
                                try:
                                    h_g, a_g = map(int, vysledek_zapasu.split(":"))
                                    total_g = h_g + a_g
                                    body_zisk = 0.0
                                    
                                    # Vyhodnocení 1X2
                                    t_1x2 = str(s["Tip_1X2"])
                                    v_1x2 = "prohra"
                                    skutecny_vysledek = "1" if h_g > a_g else ("2" if h_g < a_g else "X")
                                    
                                    if not has_draw and skutecny_vysledek == "X": continue 
                                    if t_1x2 == skutecny_vysledek: 
                                        v_1x2 = "vyhra"
                                        body_zisk += float(s["Kurz_1X2"])
                                    
                                    # Vyhodnocení gólů
                                    t_g = str(s["Tip_Goly"])
                                    v_g = "prohra"
                                    if t_g == "Více" and total_g > 2.5: 
                                        v_g = "vyhra"
                                        body_zisk += float(s["Kurz_Goly"])
                                    elif t_g == "Méně" and total_g < 2.5: 
                                        v_g = "vyhra"
                                        body_zisk += float(s["Kurz_Goly"])
                                        
                                    sazky_list[i]["Stav_1X2"] = v_1x2
                                    sazky_list[i]["Stav_Goly"] = v_g
                                    sazky_list[i]["Body_Ziskane"] = round(body_zisk, 2)
                                    sazky_list[i]["Stav_Tipu"] = "vyhodnoceno"
                                    
                                    hrace = s["Uzivatel"]
                                    body_pro_hrace[hrace] = body_pro_hrace.get(hrace, 0.0) + body_zisk
                                except: pass
                    
                    # 4. Zápisy změn zpět do tabulek
                    data_sazky_zapis = [list(r.values()) for r in sazky_list]
                    sheet_s.clear()
                    sheet_s.append_rows([hlavicka_s] + data_sazky_zapis)
                    
                    if zmeny_v_zapasech:
                        data_zapasy_zapis = [list(r.values()) for r in zapasy_z_tabulky]
                        sheet_z.clear()
                        sheet_z.append_rows([hlavicka_z] + data_zapasy_zapis)
                    
                    if body_pro_hrace:
                        sheet_u = client.open("Mistrovstvi_Tipovacka").worksheet("Uzivatele")
                        u_list = sheet_u.get_all_records()
                        for i, r in enumerate(u_list):
                            jm = str(r["Jméno"])
                            if jm in body_pro_hrace:
                                novy_sum = float(r["Body"]) + body_pro_hrace[jm]
                                sheet_u.update_cell(i + 2, 3, round(novy_sum, 2))
                                st.balloons()
                                st.success(f"🎉 {jm} získal {round(body_pro_hrace[jm], 2)} bodů!")
                    
                    st.cache_data.clear()
                    st.success("✅ Všechny dohrané zápasy v programu byly úspěšně uzavřeny!")
                    st.rerun()
