import requests
import datetime

# ================= CONFIGURAZIONE =================
API_KEY = "e8dbbddef0ac48d69d0108a60f167580"
TELEGRAM_BOT_TOKEN = "8245305133:AAETS2UpZ5RqqoDFizGSxIzE8Cb5iwrIX2Y"
TELEGRAM_CHAT_ID = "661442573"

# Prende in automatico la data odierna del giorno in cui gira lo script
DATE = datetime.date.today().strftime("%Y-%m-%d") 
HEADERS = {
    'x-apisports-key': API_KEY
}

# Lista vuota = Prende TUTTE le partite del mondo per la giornata odierna
TARGET_LEAGUES = [] 

PREFERRED_BOOKMAKERS = ["Bet365", "GoldBet", "Lottomatica", "Sisal", "Snai"]
# ==================================================

def invia_telegram_lunghi(testo):
    if not TELEGRAM_BOT_TOKEN:
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    max_length = 4000
    chunks = [testo[i:i+max_length] for i in range(0, len(testo), max_length)]
    
    for chunk in chunks:
        payload = {
            "chat_id": TELEGRAM_CHAT_ID, 
            "text": chunk, 
            "parse_mode": "Markdown"
        }
        try:
            requests.post(url, json=payload)
        except Exception:
            pass

def calcola_pronostico(mercati_dict):
    try:
        home_win = float(mercati_dict.get('1', {}).get('Home', 0))
        away_win = float(mercati_dict.get('1', {}).get('Away', 0))
        
        if home_win > 0 and away_win > 0:
            if home_win < 1.50:
                return "🎯 *Pronostico:* `1 (Favorito netto)`"
            elif away_win < 1.50:
                return "🎯 *Pronostico:* `2 (Favorito netto)`"
            elif home_win < 1.85:
                return "🎯 *Pronostico:* `1X` (Casetta solida)"
            elif away_win < 1.85:
                return "🎯 *Pronostico:* `X2` (Ospite favorito)"
            elif abs(home_win - away_win) < 0.3:
                return "🎯 *Pronostico:* `Goal` o `1X / X2` (Equilibrata)"
            else:
                return "🎯 *Pronostico:* `Over 1.5` / `Doppia Chance`"
    except Exception:
        pass
    return "🎯 *Pronostico:* `Studio consigliato`"

def avvia_script():
    # Scarica l'intero palinsesto della giornata odierna (DATA)
    fixtures_url = f"https://v3.football.api-sports.io/fixtures?date={DATE}"
    print(f"📥 Scaricamento palinsesto completo per il giorno {DATE}...")
    
    res = requests.get(fixtures_url, headers=HEADERS)
    if res.status_code != 200:
        print(f"❌ Errore nel palinsesto: {res.status_code}")
        return
        
    fixtures = res.json().get('response', [])
    print(f"✅ Trovate {len(fixtures)} partite totali in programma oggi.")

    output_lines = []
    output_lines.append(f"⚽ *PALINSESTO E QUOTE DEL {DATE}* ⚽\n")

    matches_processed = 0

    for match in fixtures:
        fixture_id = match['fixture']['id']
        
        utc_date = match['fixture']['date']
        match_time = utc_date.split('T')[1][:5] if 'T' in utc_date else ""

        home = match['teams']['home']['name']
        away = match['teams']['away']['name']
        league = match['league']['name']
        country = match['league']['country']
        
        # Interroga le quote per questa specifica partita del giorno
        odds_url = f"https://v3.football.api-sports.io/odds?fixture={fixture_id}"
        res_odds = requests.get(odds_url, headers=HEADERS)
        
        selected_bk = None
        match_markets = []
        dati_per_pronostico = {}

        if res_odds.status_code == 200:
            odds_data = res_odds.json().get('response', [])
            if odds_data:
                bookmakers = odds_data[0].get('bookmakers', [])
                for pref in PREFERRED_BOOKMAKERS:
                    for bk in bookmakers:
                        if pref.lower() in bk.get('name', '').lower():
                            selected_bk = bk
                            break
                    if selected_bk:
                        break
                if not selected_bk and bookmakers:
                    selected_bk = bookmakers[0]

        # Se troviamo il bookmaker e le quote, estraiamo i mercati principali puliti
        if selected_bk:
            bk_name = selected_bk.get('name')
            for bet in selected_bk.get('bets', []):
                bet_id = bet.get('id')
                is_target = False
                label = ""
                
                if bet_id == 1:
                    is_target, label = True, "1X2 Finale"
                    dati_per_pronostico['1'] = {v.get('value'): v.get('odd') for v in bet.get('values', [])}
                elif bet_id == 12:
                    is_target, label = True, "Doppia Chance"
                elif bet_id == 8:
                    is_target, label = True, "Gol / No Gol"
                elif bet_id == 3:
                    values_filtered = [v for v in bet.get('values', []) if str(v.get('value')) in ["Over 1.5", "Under 1.5", "Over 2.5", "Under 2.5"]]
                    if values_filtered:
                        is_target, label = True, "Under/Over 1.5 & 2.5"
                        bet['values'] = values_filtered

                if is_target:
                    values_str = [f"*{v.get('value')}*: `{v.get('odd')}`" for v in bet.get('values', [])]
                    line_market = f"  🔹 *{label}:* " + " | ".join(values_str)
                    match_markets.append(line_market)

        # Costruiamo il blocco della partita
        match_header = f"\n──────────────────\n🏆 *{country} - {league}*\n⏰ *Orario:* `{match_time}`\n⚽ *{home} vs {away}*"
        
        if selected_bk and match_markets:
            match_header += f"\n📊 *Bookmaker:* {selected_bk.get('name')}"
            output_lines.append(match_header)
            pronostico_line = calcola_pronostico(dati_per_pronostico)
            output_lines.append(f"  {pronostico_line}")
            output_lines.extend(match_markets)
        else:
            # Se per quella partita del giorno i bookmaker non hanno ancora messo le quote,
            # lo script mostra comunque l'incontro in programma con l'orario!
            match_header += f"\n📊 *Bookmaker:* `Quote in fase di pubblicazione`"
            output_lines.append(match_header)
            output_lines.append(f"  ⏳ *Stato:* Partita in programma oggi (quote non ancora disponibili)")

        matches_processed += 1

    testo_finale = "\n".join(output_lines)

    filename = f"palinsesto_quote_{DATE}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(testo_finale)
        
    print(f"\n✨ Fatto! Elaborate {matches_processed} partite per la data {DATE}. Salvate in: {filename}")
    invia_telegram_lunghi(testo_finale)

if __name__ == "__main__":
    avvia_script()
