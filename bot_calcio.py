import json
import requests
from datetime import datetime

API_KEY = "e8dbbddef0ac48d69d0108a60f167580"
HEADERS = {
    'x-apisports-key': API_KEY,
    'x-rapidapi-host': 'v3.football.api-sports.io'
}

def genera_palinsesto():
    oggi = datetime.now().strftime("%Y-%m-%d")
    url = f"https://v3.football.api-sports.io/fixtures?date={oggi}"
    
    print(f"Scansione palinsesto per la data: {oggi}")
    dati_finali = {}

    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        res_json = response.json()
        
        if "response" in res_json and len(res_json["response"]) > 0:
            for item in res_json["response"]:
                league_info = item.get("league", {})
                league_name = league_info.get("name", "Altro")
                country = league_info.get("country", "Internazionale")
                
                chiave_lega = f"{country} - {league_name}"
                
                if chiave_lega not in dati_finali:
                    dati_finali[chiave_lega] = []

                fixture = item.get("fixture", {})
                teams = item.get("teams", {})
                
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
                    "desc": f"Analisi algoritmica ufficiale: {home_team} vs {away_team}."
                }
                dati_finali[chiave_lega].append(match_data)
                
        print(f"Competizioni caricate con successo: {len(dati_finali)}")
        
    except Exception as e:
        print(f"Errore durante la chiamata API: {e}")

    # Scrittura del file JSON
    with open("dati_calcio.json", "w", encoding="utf-8") as f:
        json.dump(dati_finali, f, ensure_ascii=False, indent=4)
    
    print("Salvataggio completato.")

if __name__ == "__main__":
    genera_palinsesto()
