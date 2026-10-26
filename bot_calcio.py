import requests
import datetime

# ================= CONFIGURAZIONE =================
# API Football
API_KEY = "e8dbbddef0ac48d69d0108a60f167580"

# Telegram
TELEGRAM_BOT_TOKEN = "8245305133:AAETS2UpZ5RqqoDFizGSxIzE8Cb5iwrIX2Y"
TELEGRAM_CHAT_ID = "661442573"

DATE = datetime.date.today().strftime("%Y-%m-%d") 
HEADERS = {
    'x-apisports-key': API_KEY
}

# Campionati d'interesse (Serie A, Serie B, Premier, Liga, Bundesliga, Ligue 1, Champions, Europa League)
TARGET_LEAGUES = [135, 136, 39, 140, 78, 61, 2, 3] 

# I tuoi bookmaker preferiti in ordine di priorità
PREFERRED_BOOKMAKERS = ["Bet365", "GoldBet", "Lottomatica", "Sisal", "Snai"]
# ==================================================

def invia_telegram(messaggio):
    """Funzione per inviare la notifica o il riepilogo sul tuo canale/chat Telegram"""
    if not TELEGRAM_BOT_TOKEN:
        print("⚠️ Token Telegram non configurato.")
        return
        
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID, 
        "text": messaggio, 
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("📤 Notifica inviata con successo su Telegram!")
        else:
            print(f"❌ Errore invio Telegram: {response.text}")
    except Exception as e:
        print(f"⚠️ Errore di connessione a Telegram: {e}")

def avvia_script():
    fixtures_url = f"https://v3.football.api-sports.io/fixtures?date={DATE}"
    print(f"📥 [1 Chiamata] Scaricamento palinsesto per il {DATE}...")
    
    res = requests.get(fixtures_url, headers=HEADERS)
    if res.status_code != 200:
        print(f"❌ Errore nel palinsesto: {res.status_code} - {res.text}")
        return
        
    fixtures = res.json().get('response', [])
    print(f"✅ Trovate {len(fixtures)} partite totali nel mondo.")

    # Filtra per le leghe scelte
    filtered_fixtures = [
        f for f in fixtures 
        if not TARGET_LEAGUES or f['league']['id'] in TARGET_LEAGUES
    ]
    print(f"🎯 Partite filtrate per le tue leghe d'interesse: {len(filtered_fixtures)}")
    print(f"⚠️ Questo script consumerà circa {len(filtered_fixtures) + 1} chiamate API su 100.\n")
    print("-" * 50)

    output_lines = []
    output_lines.append(f"=== PALINSESTO E QUOTE DEL {DATE} ===\n")

    for match in filtered_fixtures:
        fixture_id = match['fixture']['id']
        home = match['teams']['home']['name']
        away = match['teams']['away']['name']
        league = match['league']['name']
        country = match['league']['country']
        
        print(f"🔍 Controllo quote per: {home} vs {away}...")
        
        odds_url = f"https://v3.football.api-sports.io/odds?fixture={fixture_id}"
        res_odds = requests.get(odds_url, headers=HEADERS)
        
        if res_odds.status_code != 200:
            continue
            
        odds_data = res_odds.json().get('response', [])
        if not odds_data:
            print("   ⚠️ Nessuna quota trovata.")
            continue
            
        bookmakers = odds_data[0].get('bookmakers', [])
        if not bookmakers:
            continue
            
        # Ricerca del bookmaker in base alla priorità stabilita
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
                
        match_header = f"\n📌 [{country} - {league}] {home} vs {away} (ID: {fixture_id})"
        bookie_info = f"   📊 Bookmaker utilizzato: {selected_bk.get('name')}"
        
        output_lines.append(match_header)
        output_lines.append(bookie_info)
        
        # Estrazione dei mercati richiesti
        for bet in selected_bk.get('bets', []):
            bet_id = bet.get('id')
            bet_name = bet.get('name')
            
            is_target = False
            label = ""
            
            if bet_id == 1:
                is_target, label = True, "1X2 Finale"
            elif bet_id == 12:
                is_target, label = True, "Doppia Chance"
            elif bet_id == 8:
                is_target, label = True, "Gol / No Gol"
            elif bet_id == 3:
                values_filtered = [v for v in bet.get('values', []) if "1.5" in str(v.get('value'))]
                if values_filtered:
                    is_target, label = True, "Over/Under 1.5"
                    bet['values'] = values_filtered
            elif any(keyword in bet_name.lower() for keyword in ["multi", "combo", "goal", "score"]):
                is_target, label = True, bet_name

            if is_target:
                values_str = [f"{v.get('value')}: {v.get('odd')}" for v in bet.get('values', [])]
                line_market = f"      🔹 {label}: {', '.join(values_str)}"
                output_lines.append(line_market)

    # Scrittura del file di testo locale
    filename = f"palinsesto_quote_{DATE}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(output_lines))
        
    print(f"\n✨ Fatto! Risultati salvati con successo nel file: {filename}")
    
    # Invio della notifica su Telegram
    invia_telegram(f"⚽ *Palinsesto Calcio generato!*\nData: {DATE}\nFile salvato con successo.")

if __name__ == "__main__":
    avvia_script()
