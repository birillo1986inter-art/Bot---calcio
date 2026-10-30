<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Quantum Cup Football - Dashboard</title>
    <style>
        :root {
            --bg-main: #0b0f19;
            --bg-card: #151d2a;
            --bg-hover: #212d42;
            --accent-blue: #2563eb;
            --accent-green: #10b981;
            --accent-gold: #f59e0b;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --border: #1e293b;
        }
        
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, sans-serif; }
        body { background-color: var(--bg-main); color: var(--text-main); padding: 12px; max-width: 1400px; margin: 0 auto; }

        header {
            text-align: center; margin-bottom: 16px; padding: 16px;
            background: var(--bg-card); border-radius: 12px; border: 1px solid var(--border);
        }
        h1 { font-size: 1.6rem; color: var(--accent-gold); }
        .subtitle { color: var(--text-muted); font-size: 0.85rem; }

        .dashboard-container { display: grid; grid-template-columns: 1fr; gap: 16px; }
        @media (min-width: 850px) { .dashboard-container { grid-template-columns: 280px 1fr; } }

        .sidebar { background: var(--bg-card); border-radius: 12px; padding: 14px; border: 1px solid var(--border); }
        .sidebar h2 { font-size: 0.9rem; color: var(--text-muted); margin-bottom: 12px; text-transform: uppercase; }
        .league-list { display: flex; flex-direction: column; gap: 8px; }

        .league-btn {
            display: flex; align-items: center; gap: 10px; background: var(--bg-main);
            color: var(--text-main); padding: 10px 12px; border-radius: 8px;
            border: 1px solid var(--border); cursor: pointer; font-weight: 500; width: 100%; text-align: left;
        }
        .league-btn:hover, .league-btn.active { background: var(--bg-hover); border-color: var(--accent-blue); }

        .main-content { display: flex; flex-direction: column; gap: 16px; }
        .content-header {
            background: var(--bg-card); padding: 14px 18px; border-radius: 12px;
            border: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center;
        }

        .match-card {
            background: var(--bg-card); border-radius: 12px; padding: 16px;
            border: 1px solid var(--border); display: flex; flex-direction: column; gap: 12px;
        }
        .match-header { display: flex; justify-content: space-between; color: var(--text-muted); font-size: 0.8rem; font-weight: 600; }
        .match-teams { display: flex; justify-content: space-between; align-items: center; font-size: 1.1rem; font-weight: bold; }
        .vs { color: var(--accent-gold); font-size: 0.85rem; }

        .odds-grid {
            display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px;
            background: var(--bg-main); padding: 10px; border-radius: 8px;
        }
        .odd-box {
            display: flex; flex-direction: column; align-items: center;
            background: var(--bg-card); padding: 6px; border-radius: 6px; border: 1px solid var(--border); font-size: 0.8rem;
        }
        .odd-label { color: var(--text-muted); font-size: 0.7rem; }
        .odd-val { color: var(--accent-blue); font-weight: bold; margin-top: 2px; }

        .prediction-box {
            background: rgba(37, 99, 235, 0.1); border: 1px solid var(--accent-blue);
            border-radius: 8px; padding: 12px; display: flex; flex-direction: column; gap: 6px;
        }
        .prono-title { color: var(--accent-gold); font-size: 0.85rem; font-weight: bold; text-transform: uppercase; }
        .prono-badge { background: var(--accent-green); color: black; font-weight: bold; padding: 4px 10px; border-radius: 4px; font-size: 0.85rem; width: fit-content; }
        .prono-stats { color: var(--text-muted); font-size: 0.8rem; }
    </style>
</head>
<body>

    <header>
        <h1>Quantum Cup Football</h1>
        <p class="subtitle">Analisi Live & Algoritmo Pronostici</p>
    </header>

    <div class="dashboard-container">
        <div class="sidebar">
            <h2>Campionati</h2>
            <div class="league-list">
                <button class="league-btn active" onclick="loadLeague('ITA', this)"><span>🇮🇹</span> Italia - Serie A</button>
                <button class="league-btn" onclick="loadLeague('ENG', this)"><span>🏴󠁧󠁢󠁥󠁮󠁧󠁿</span> Inghilterra - Premier</button>
                <button class="league-btn" onclick="loadLeague('ESP', this)"><span>🇪🇸</span> Spagna - LaLiga</button>
                <button class="league-btn" onclick="loadLeague('GER', this)"><span>🇩🇪</span> Germania - Bundesliga</button>
                <button class="league-btn" onclick="loadLeague('FRA', this)"><span>🇫🇷</span> Francia - Ligue 1</button>
            </div>
        </div>

        <div class="main-content">
            <div class="content-header">
                <h3 id="selectedLeagueTitle">Campionato Selezionato</h3>
                <span id="matchCount" style="color: var(--accent-green); font-weight: bold;">Caricamento...</span>
            </div>

            <div id="matchesContainer"></div>
        </div>
    </div>

    <script>
        let currentLeague = 'ITA';

        async function loadLeague(code, btnElement) {
            if (btnElement) {
                document.querySelectorAll('.league-btn').forEach(b => b.classList.remove('active'));
                btnElement.classList.add('active');
            }

            currentLeague = code;
            const container = document.getElementById('matchesContainer');
            
            try {
                const response = await fetch('./dati_calcio.json?v=' + new Date().getTime());
                const database = await response.json();
                const matches = database[code] || [];
                
                document.getElementById('matchCount').innerText = `${matches.length} Match Trovati`;

                if (matches.length === 0) {
                    container.innerHTML = '<p style="color: var(--text-muted); padding: 20px;">Nessuna partita in palinsesto per questo campionato oggi.</p>';
                    return;
                }

                let html = '';
                matches.forEach(m => {
                    html += `
                        <div class="match-card">
                            <div class="match-header">
                                <span>OGGI - ${m.time}</span>
                                <span>ANALISI REAL-TIME</span>
                            </div>
                            <div class="match-teams">
                                <span>${m.home}</span>
                                <span class="vs">VS</span>
                                <span>${m.away}</span>
                            </div>

                            <div class="odds-grid">
                                <div class="odd-box"><span class="odd-label">1</span><span class="odd-val">${m.odds['1']}</span></div>
                                <div class="odd-box"><span class="odd-label">X</span><span class="odd-val">${m.odds['X']}</span></div>
                                <div class="odd-box"><span class="odd-label">2</span><span class="odd-val">${m.odds['2']}</span></div>
                                <div class="odd-box"><span class="odd-label">1X</span><span class="odd-val">${m.odds['1X']}</span></div>
                                <div class="odd-box"><span class="odd-label">12</span><span class="odd-val">${m.odds['12']}</span></div>
                                <div class="odd-box"><span class="odd-label">X2</span><span class="odd-val">${m.odds['X2']}</span></div>
                                <div class="odd-box"><span class="odd-label">O 1.5</span><span class="odd-val">${m.odds['O1.5']}</span></div>
                                <div class="odd-box"><span class="odd-label">O 2.5</span><span class="odd-val">${m.odds['O2.5']}</span></div>
                                <div class="odd-box"><span class="odd-label">O 3.5</span><span class="odd-val">${m.odds['O3.5']}</span></div>
                            </div>

                            <div class="prediction-box">
                                <span class="prono-title">Pronostico Calcolato (Affidabilità ${m.confidence})</span>
                                <span class="prono-badge">${m.prono}</span>
                                <span class="prono-stats">${m.desc}</span>
                            </div>
                        </div>
                    `;
                });

                container.innerHTML = html;
            } catch (error) {
                container.innerHTML = '<p style="color: var(--text-muted); padding: 20px;">Attendi il primo avvio del bot per la scansione del palinsesto...</p>';
            }
        }

        // Caricamento automatico
        loadLeague('ITA', null);
    </script>
</body>
</html>
