import requests
import datetime

# ================= CONFIGURAZIONE =================
API_KEY = "e8dbbddef0ac48d69d0108a60f167580"
TELEGRAM_BOT_TOKEN = "8245305133:AAETS2UpZ5RqqoDFizGSxIzE8Cb5iwrIX2Y"
TELEGRAM_CHAT_ID = "661442573"

DATE = datetime.date.today().strftime("%Y-%m-%d") 
HEADERS = {
    'x-apisports-key': API_KEY
}

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
    # 1. Scarichiamo tutte le quote dell'intera giornata in un'unica chiamata massiva
    odds_url = f"https://v3.football.api-sports.io/odds?date={DATE}"
    print(f"📥 Scaricamento massivo delle quote per il giorno {DATE}...")
    
    res_odds = requests.get(odds_url, headers=HEADERS)
    if res_odds.status_code != 200:
        print(f"❌ Errore nel recupero delle quote: {res_odds.status_code}")
        return
        
    all_odds = res_odds.json().get('response', [])
    print(f"✅ Trovati dati di quote per {len(all_odds)} partite.")

    output_lines = []
    output_lines.append(f"⚽ *PALINSESTO E PRONOSTICI DEL {DATE}* ⚽\n")

    matches_processed = 0

    for item in all_odds:
        fixture = item.get('fixture', {})
        league = item.get('league', {})
        teams = item.get('teams', {})
        bookmakers = item.get('bookmakers', [])

        fixture_id = fixture.get('id')
        utc_date = fixture.get('date', '')
        match_time = utc_date.split('T')[1][:5] if 'T' in utc_date else ""

        home = teams.get('home', {}).get('name', '')
        away = teams.get('away', {}).get('name', '')
        league_name = league.get('name', '')
        country = league.get('country', '')

        # Seleziona il bookmaker preferito
        selected_bk = None
        for pref in PREFERRED_BOOKMAKERS:
            for bk in bookmakers:
                if pref.lower() in bk.get('name', '').lower():
                    selected_bk = bk
                    break
            if selected_bk:
                break
        
        if not selected_bk and bookmakers:
            selected_bk = bookmakers[0]

        if not selected_bk:
            continue

        match_header = f"\n──────────────────\n🏆 *{country} - {league_name}*\n⏰ *Orario:* `{match_time}`\n⚽ *{home} vs {away}*\n📊 *Bookmaker:* {selected_bk.get('name')}"
        
        match_markets = []
        dati_per_pronostico = {}

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

        if match_markets:
            output_lines.append(match_header)
            pronostico_line = calcola_pronostico(dati_per_pronostico)
            output_lines.append(f"  {pronostico_line}")
            output_lines.extend(match_markets)
            matches_processed += 1

    testo_finale = "\n".join(output_lines)

    filename = f"palinsesto_quote_{DATE}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(testo_finale)
        
    print(f"\n✨ Fatto! Elaborate {matches_processed} partite con quote e pronostici. Salvate in: {filename}")
    invia_telegram_lunghi(testo_finale)

if __name__ == "__main__":
    avvia_script()
