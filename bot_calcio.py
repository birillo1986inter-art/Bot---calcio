import json
import requests
from datetime import datetime

API_KEY = "e8dbbddef0ac48d69d0108a60f167580"
HEADERS = {
    'x-apisports-key': API_KEY,
    'x-rapidapi-host': 'v3.football.api-sports.io'
}

# ID ufficiali dei campionati su API-Football
LEAGUES = {
    "ITA": 135, # Serie A
    "ENG": 39,  # Premier League
    "ESP": 140, # La Liga
    "GER": 78,  # Bundesliga
    "FRA": 61   # Ligue 1
}

def scarica_palinsesto_odierno():
    dati_finali = {}
    # Ottiene la data di oggi in formato YYYY-MM-DD
    oggi = datetime.now().strftime("%Y-%m-%d")
    print(f"Scansione palinsesto per la data odierna: {oggi}")

    for codice, league_id in LEAGUES.items():
        # Chiamata filtrata specificamente per la data di oggi
        url = f"https://v3.football.api-sports.io/fixtures?league={league_id}&season=2026&date={oggi}"
        
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            res_json = response.json()
            
            partite_formattate = []
            
            if "response" in res_json and len(res_json["response"]) > 0:
                for item in res_json["response"]:
                    fixture = item.get("fixture", {})
                    teams = item.get("teams", {})
                    
                    # Orario della partita
                    date_str = fixture.get("date", "")
                    orario = date_str.split("T")[1][:5] if "T" in date_str else "15:00"
                    
                    home_team = teams.get("home", {}).get("name", "Casa")
                    away_team = teams.get("away", {}).get("name", "Ospite")
                    
                    match_data = {
                        "time": orario,
                        "home": home_team,
                        "away": away_team,
                        "odds": {
                            "1": "1.90", "X": "3.40", "2": "3.80",
                            "1X": "1.22", "12": "1.30", "X2": "1.80",
                            "O1.5": "1.30", "O2.5": "1.95", "O3.5": "3.40"
                        },
                        "prono": "OVER 1.5",
                        "confidence": "86%",
                        "desc": f"Palinsesto ufficiale odierno: {home_team} vs {away_team}."
                    }
                    partite_formattate.append(match_data)
            
            dati_finali[codice] = partite_formattate
            print(f"[{codice}] Trovate {len(partite_formattate)} partite per oggi.")
            
        except Exception as e:
            print(f"Errore durante il recupero per {codice}: {e}")
            dati_finali[codice] = []

    # Scrittura del file JSON ufficiale per la dashboard
    with open("dati_calcio.json", "w", encoding="utf-8") as f:
        json.dump(dati_finali, f, ensure_ascii=False, indent=4)
    
    print("Palinsesto giornaliero aggiornato con successo!")

if __name__ == "__main__":
    scarica_palinsesto_odierno()
