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

# Lista vuota = Prende TUTTE le partite e i campionati del mondo per oggi
TARGET_LEAGUES = [] 

# I tuoi bookmaker preferiti in ordine di priorità
PREFERRED_BOOKMAKERS = ["Bet365", "GoldBet", "Lottomatica", "Sisal", "Snai"]
# ==================================================

def invia_telegram_lunghi(testo):
    """Funzione per inviare messaggi lunghi dividendoli nei limiti di Telegram"""
    if not TELEGRAM_BOT_TOKEN:
        print("⚠️ Token Telegram non configurato.")
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
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                print("📤 Messaggio inviato con successo su Telegram!")
            else:
                print(f"❌ Errore invio Telegram: {response.text}")
        except Exception as e:
            print(f"⚠️ Errore di connessione a Telegram: {e}")

def avvia_script():
    fixtures_url = f"https://v3.football.api-sports.io/fixtures?date={DATE}"
    print(f"📥 Scaricamento palinsesto completo per il {DATE}...")
    
    res = requests.get(fixtures_url, headers=HEADERS)
    if res.status_code != 200:
        print(f"❌ Errore nel palinsesto: {res.status_code} - {res.text}")
        return
        
    fixtures = res.json().get('response', [])
    print(f"✅ Trovate {len(fixtures)} partite totali nel mondo.")

    output_lines = []
    output_lines.append(f"⚽ *PALINSESTO E QUOTE DEL {DATE}* ⚽\n")

    matches_processed = 0

    for match in fixtures:
        fixture_id = match['fixture']['id']
        
        # Estrazione dell'orario della partita (formato HH:MM)
        utc_date = match['fixture']['date']
        match_time = utc_date.split('T')[1][:5] if 'T' in utc_date else ""

        home = match['teams']['home']['name']
        away = match['teams']['away']['name']
        league = match['league']['name']
        country = match['league']['country']
        
        odds_url = f"https://v3.football.api-sports.io/odds?fixture={fixture_id}"
        res_odds = requests.get(odds_url, headers=HEADERS)
        
        if res_odds.status_code != 200:
            continue
            
        odds_data = res_odds.json().get('response', [])
        if not odds_data:
            continue
            
        bookmakers = odds_data[0].get('bookmakers', [])
        if not bookmakers:
            continue
            
        # Ricerca del bookmaker in base alla priorità
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
                
        # Intestazione della partita con orario in evidenza
        match_header = f"\n──────────────────\n🏆 *{country} - {league}*\n⏰ *Orario:* `{match_time}`\n⚽ *{home} vs {away}*\n📊 *Bookmaker:* {selected_bk.get('name')}"
        
        match_markets = []
        for bet in selected_bk.get('bets', []):
            bet_id = bet.get('id')
            
            is_target = False
            label = ""
            
            if bet_id == 1:
                is_target, label = True, "1X2 Finale"
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
            output_lines.extend(match_markets)
            matches_processed += 1

    # Unisce tutto il testo
    testo_finale = "\n".join(output_lines)

    # Salvataggio del file di testo di riserva nel repository
    filename = f"palinsesto_quote_{DATE}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(testo_finale)
        
    print(f"\n✨ Fatto! Analizzate {matches_processed} partite con quote. Risultati salvati in: {filename}")
    
    # Invio diretto del palinsesto formattato su Telegram
    invia_telegram_lunghi(testo_finale)

if __name__ == "__main__":
    avvia_script()
