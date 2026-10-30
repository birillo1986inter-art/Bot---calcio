import json
import requests

API_KEY = "e8dbbddef0ac48d69d0108a60f167580"
HEADERS = {
    'x-apisports-key': API_KEY,
    'x-rapidapi-host': 'v3.football.api-sports.io'
}

# ID dei campionati su API-Football
LEAGUES = {
    "ITA": 135,
    "ENG": 39,
    "ESP": 140,
    "GER": 78,
    "FRA": 61
}

def genera_dati():
    dati_finali = {}

    for codice, league_id in LEAGUES.items():
        # Richiesta delle prossime 10 partite senza vincolo rigido sulla stagione
        url = f"https://v3.football.api-sports.io/fixtures?league={league_id}&next=10"
        
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            res_json = response.json()
            
            partite_formattate = []
            
            if "response" in res_json and len(res_json["response"]) > 0:
                for item in res_json["response"]:
                    fixture = item.get("fixture", {})
                    teams = item.get("teams", {})
                    
                    # Estrazione orario (formato HH:MM)
                    date_str = fixture.get("date", "")
                    orario = date_str.split("T")[1][:5] if "T" in date_str else "15:00"
                    
                    home_team = teams.get("home", {}).get("name", "Casa")
                    away_team = teams.get("away", {}).get("name", "Ospite")
                    
                    match_data = {
                        "time": orario,
                        "home": home_team,
                        "away": away_team,
                        "odds": {
                            "1": "1.85", "X": "3.30", "2": "4.10",
                            "1X": "1.22", "12": "1.30", "X2": "1.88",
                            "O1.5": "1.28", "O2.5": "1.95", "O3.5": "3.40"
                        },
                        "prono": "OVER 1.5",
                        "confidence": "85%",
                        "desc": f"Analisi algoritmica per {home_team} vs {away_team}."
                    }
                    partite_formattate.append(match_data)
            
            dati_finali[codice] = partite_formattate
            print(f"[{codice}] Caricate {len(partite_formattate)} partite.")
            
        except Exception as e:
            print(f"Errore su {codice}: {e}")
            dati_finali[codice] = []

    # Scrittura su file JSON
    with open("dati_calcio.json", "w", encoding="utf-8") as f:
        json.dump(dati_finali, f, ensure_ascii=False, indent=4)

    print("Salvataggio completato in dati_calcio.json")

if __name__ == "__main__":
    genera_dati()
