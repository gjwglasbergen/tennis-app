# Goofies Tennis Tracker 🎾

Een web-applicatie om tenniswedstrijden van je vrienden live te volgen en bij te houden. Perfect voor het delen van scores met toeschouwers die niet ter plaatse kunnen zijn!

## Features ✨

### Score Tracking
- **Real-time puntentelling**: Klik op de naam van een speler om een punt toe te kennen
- **Automatische scoreberekening**: De app berekent automatisch game, set en match scores volgens de officiële tennisregels
- **Advantage (AD) support**: Optioneel spelen met of zonder voordeel bij deuce (40-40)
- **Undo functie**: Maakte je een fout? Draai de laatste actie terug met één klik

### Live Streaming
- **Automatische updates**: View-pagina ververst elke 5 seconden automatisch
- **Multiple viewers**: Meerdere mensen kunnen tegelijkertijd dezelfde wedstrijd volgen
- **Active status indicators**: 
  - 🟢 Groene bol = Match is actief
  - 🔴 Rode bol = Match is inactief (gewonnen of 30+ minuten geen activiteit)

### Match Management
- **Overzicht**: Bekijk alle wedstrijden in één lijst
- **Configureerbare settings**:
  - Aantal games om een set te winnen (standaard 6)
  - Best-of aantal sets (standaard 3)
  - Wie serveert eerst
  - Met of zonder Advantage

## Installatie 🚀

### Vereisten
- Docker Desktop
- Docker Compose

### Quick Start

1. **Clone de repository**
   ```bash
   git clone https://github.com/PowerPioneer/tennis-app.git
   cd tennis-app
   ```

2. **Start de applicatie**
   ```bash
   docker-compose up -d
   ```

3. **Open in je browser**
   ```
   http://localhost:5000
   ```

Dat is alles! De applicatie draait nu en je kunt wedstrijden beginnen te tracken.

## Gebruik 📖

### Een nieuwe wedstrijd aanmaken

1. Ga naar de homepage
2. Klik op "Create Match" of navigeer naar `/create-match`
3. Vul de volgende gegevens in:
   - Naam van Speler 1
   - Naam van Speler 2
   - Aantal games om te winnen (standaard: 6)
   - Best of aantal sets (standaard: 3)
   - Wie serveert eerst
   - Met Advantage (AD): Ja/Nee
4. Klik op "Maak wedstrijd aan"

### Scores bijhouden

1. Ga naar "Matches" om alle wedstrijden te zien
2. Klik op "View" bij de gewenste wedstrijd
3. Of ga direct naar `/match/<id>/edit` voor de edit-modus
4. Klik op de naam van de speler die het punt wint
5. De score wordt automatisch bijgewerkt
6. Gebruik de "Undo" knop als je een fout hebt gemaakt

### Een wedstrijd live volgen

1. Ga naar "Matches"
2. Klik op "View" bij de wedstrijd die je wilt volgen
3. De scores worden automatisch elke 5 seconden ververst
4. Deel de URL met vrienden zodat zij ook mee kunnen kijken!

## Technische Details 🔧

### Tech Stack
- **Backend**: Flask (Python)
- **Database**: SQLite
- **Frontend**: Bootstrap 5, Vanilla JavaScript
- **Containerization**: Docker & Docker Compose
- **Tennis Logic**: `tennis` Python package

### Project Structuur
```
tennis-app/
├── src/
│   ├── app.py              # Flask applicatie en routes
│   ├── models.py           # Database models
│   ├── config.py           # Configuratie
│   ├── static/
│   │   └── css/
│   │       └── style.css   # Custom styling
│   └── templates/          # HTML templates
│       ├── base.html
│       ├── index.html
│       ├── creatematch.html
│       ├── editmatch.html
│       ├── viewmatch.html
│       └── matches.html
├── data/                   # SQLite database (persists via volume)
├── docker-compose.yaml
├── Dockerfile
└── requirements.txt
```

### API Endpoints

| Endpoint | Methode | Beschrijving |
|----------|---------|--------------|
| `/` | GET | Homepage |
| `/create-match` | GET, POST | Nieuwe wedstrijd aanmaken |
| `/matches` | GET | Overzicht van alle wedstrijden |
| `/match/<id>` | GET | Wedstrijd bekijken (view-only) |
| `/match/<id>/edit` | GET | Wedstrijd bewerken (scores toevoegen) |
| `/match/<id>/add-point` | POST | Punt toevoegen aan speler |
| `/match/<id>/undo` | POST | Laatste actie ongedaan maken |
| `/match/<id>/data` | GET | Match data als JSON (voor live updates) |

### Database Schema

**MatchModel**
- `id`: Integer (Primary Key)
- `player1`: String - Naam eerste speler
- `player2`: String - Naam tweede speler
- `date_created`: DateTime - Aanmaakdatum
- `last_updated`: DateTime - Laatste update
- `active`: Boolean - Is match actief?
- `data`: Text (JSON) - Match state
- `backup_data`: Text (JSON) - Backup voor undo

## Beveiliging 🔒

- **CSRF Protection**: Alle formulieren zijn beschermd tegen Cross-Site Request Forgery
- **Input Validation**: Alle gebruikersinvoer wordt gevalideerd
- **Error Handling**: Robuuste error handling voorkomt crashes

## Ontwikkeling 🛠️

### Lokaal ontwikkelen

```bash
# Start de container
docker-compose up

# De applicatie draait in development mode met:
# - Auto-reload bij code wijzigingen
# - Debug mode enabled
# - Volume mounting voor live updates
```

### Database reset

Als je de database wilt resetten:

```bash
docker-compose exec web rm /data/app.db
docker-compose restart web
```

## Contact 📧

Heb je vragen, suggesties of wil je bijdragen? Open een issue of pull request!

---

**Geniet van het volgen van je tenniswedstrijden! 🎾🏆**
