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
                    
                    # 2. Načteme všechny tři tabulky
                    sheet_z = client.open("Mistrovstvi_Tipovacka").worksheet("Zápasy")
                    zapasy_z_tabulky = sheet_z.get_all_records()
                    hlavicka_z = list(zapasy_z_tabulky[0].keys()) if zapasy_z_tabulky else []
                    mapa_zapasu = {str(zp["ID"]): zp for zp in zapasy_z_tabulky}
                    
                    sheet_s = client.open("Mistrovstvi_Tipovacka").worksheet("Sázky")
                    sazky_list = sheet_s.get_all_records()
                    hlavicka_s = list(sazky_list[0].keys()) if sazky_list else []
                    
                    body_pro_hrace = {}
                    zmeny_v_zapasech = False
                    
                    # 3. Projdeme čekající tikety
                    for i, s in enumerate(sazky_list):
                        if str(s.get("Stav_Tipu")).lower() == "ceka":
                            z_id = str(s.get("ID_zapasu"))
                            info_zapas = mapa_zapasu.get(z_id, {})
                            jmeno_domaci = info_zapas.get("Domaci", "")
                            jmeno_hoste = info_zapas.get("Hoste", "")
                            klic_pro_hledani = f"{jmeno_domaci} vs {jmeno_hoste}"
                            has_draw = str(info_zapas.get("Kurz_X", "")).strip() != ""
                            
                            # GOD MODE: Pokud API spí, podíváme se, jestli jsi nevyplnil skóre ručně
                            manualni_vysledek = str(info_zapas.get("Vysledek", "")).strip()
                            h_g, a_g = None, None
                            
                            if ":" in manualni_vysledek:
                                try:
                                    h_g, a_g = map(int, manualni_vysledek.split(":"))
                                except: pass
                            elif klic_pro_hledani in dokoncene:
                                h_g = dokoncene[klic_pro_hledani]["home"]
                                a_g = dokoncene[klic_pro_hledani]["away"]
                                # API zjistilo výsledek! Zapíšeme ho do tabulky Zápasů, ať je to hezké.
                                for j, zp in enumerate(zapasy_z_tabulky):
                                    if str(zp["ID"]) == z_id:
                                        zapasy_z_tabulky[j]["Vysledek"] = f"{h_g}:{a_g}"
                                        zapasy_z_tabulky[j]["Stav"] = "ukonceno"
                                        zmeny_v_zapasech = True
                            
                            # Pokud máme skóre (od API nebo od tebe), vyhodnocujeme tiket
                            if h_g is not None and a_g is not None:
                                total_g = h_g + a_g
                                body_zisk = 0.0
                                
                                # A) Vyhodnocení vítěze (1X2)
                                t_1x2 = str(s["Tip_1X2"])
                                v_1x2 = "prohra"
                                skutecny_vysledek = "1" if h_g > a_g else ("2" if h_g < a_g else "X")
                                
                                if not has_draw and skutecny_vysledek == "X": continue # Remíza v play-off se vyhodnotí až po prodloužení
                                if t_1x2 == skutecny_vysledek: 
                                    v_1x2 = "vyhra"
                                    body_zisk += float(s["Kurz_1X2"])
                                
                                # B) Vyhodnocení gólů (2.5)
                                t_g = str(s["Tip_Goly"])
                                v_g = "prohra"
                                if t_g == "Více" and total_g > 2.5: 
                                    v_g = "vyhra"
                                    body_zisk += float(s["Kurz_Goly"])
                                elif t_g == "Méně" and total_g < 2.5: 
                                    v_g = "vyhra"
                                    body_zisk += float(s["Kurz_Goly"])
                                    
                                # Uložení verdiktu
                                sazky_list[i]["Stav_1X2"] = v_1x2
                                sazky_list[i]["Stav_Goly"] = v_g
                                sazky_list[i]["Body_Ziskane"] = round(body_zisk, 2)
                                sazky_list[i]["Stav_Tipu"] = "vyhodnoceno"
                                
                                hrace = s["Uzivatel"]
                                body_pro_hrace[hrace] = body_pro_hrace.get(hrace, 0.0) + body_zisk
                    
                    # 4. Hromadné zápisy do Google Tabulek
                    # Zápis sázek
                    data_sazky_zapis = [list(r.values()) for r in sazky_list]
                    sheet_s.clear()
                    sheet_s.append_rows([hlavicka_s] + data_sazky_zapis)
                    
                    # Zápis dohranných zápasů
                    if zmeny_v_zapasech:
                        data_zapasy_zapis = [list(r.values()) for r in zapasy_z_tabulky]
                        sheet_z.clear()
                        sheet_z.append_rows([hlavicka_z] + data_zapasy_zapis)
                    
                    # Zápis bodů na konta uživatelů
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
                    st.success("✅ Všechny dostupné zápasy byly vyhodnoceny!")
