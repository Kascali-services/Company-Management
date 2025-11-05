# Unternehmen Management System

Ein modernes Web-Anwendung zur Verwaltung von Unternehmen und deren Kontaktpersonen, gebaut mit FastAPI, PostgreSQL und Tailwind CSS.

## 🚀 Features

- ✅ **CRUD Operationen** für Unternehmen und Personen
- ✅ **Dashboard** mit moderner UI (Tailwind CSS)
- ✅ **Pagination** (20 Einträge pro Seite)
- ✅ **Suche & Filter** (Name, Stadt, PLZ, Bundesland)
- ✅ **Sortierung** nach allen Spalten (aufsteigend/absteigend)
- ✅ **Validation** - PLZ (5 Ziffern), Bundesländer (16 deutsche Bundesländer)
- ✅ **Export** - CSV und Excel Format
- ✅ **Responsive Design** - funktioniert auf Desktop, Tablet und Mobile
- ✅ **Detailansicht** mit allen Personen (Ansprechpartner & Empfehler)

## 📋 Datenmodell

### Unternehmen
- **name**: Name des Unternehmens
- **bundesland**: Eines der 16 deutschen Bundesländer (validiert)
- **stadt**: Stadt
- **plz**: Postleitzahl (5 Ziffern, validiert)
- **strasse**: Straßenname
- **hausnummer**: Hausnummer
- **ansprechpartner_id**: Optional - Referenz zu einer Person mit Rolle "Ansprechpartner"

### Person
- **vorname**: Vorname
- **nachname**: Nachname
- **email**: Email (optional)
- **telefon**: Telefonnummer (optional)
- **funktion**: Mitarbeiter oder Azubi
- **rolle**: Ansprechpartner oder Empfehler
- **firma_id**: Referenz zum Unternehmen

**Regeln:**
- Ein Unternehmen kann **einen** Ansprechpartner haben (nullable)
- Ein Unternehmen kann **mehrere** Empfehler haben (nullable)
- Eine Person gehört zu **einem** Unternehmen
- Beim Löschen eines Unternehmens werden alle zugehörigen Personen gelöscht

## 🛠️ Technologie-Stack

- **Backend**: FastAPI 0.104.1
- **Database**: PostgreSQL 15
- **ORM**: SQLAlchemy 2.0
- **Frontend**: Jinja2 Templates + Vanilla JavaScript
- **Styling**: Tailwind CSS (CDN)
- **Icons**: Font Awesome 6.4
- **Export**: openpyxl (Excel), csv (CSV)
- **Container**: Docker + Docker Compose

## 📦 Installation & Start

### Voraussetzungen
- Docker & Docker Compose installiert
- Git installiert

### 1. Repository klonen
```bash
git clone <repository-url>
cd unternehmen-management
```

### 2. Projekt starten
```bash
# Containers starten (erster Start kann etwas dauern)
docker-compose up -d

# Logs ansehen
docker-compose logs -f
```

### 3. Anwendung öffnen
Öffnen Sie Ihren Browser und navigieren Sie zu:
```
http://localhost:8000
```

Die API-Dokumentation ist verfügbar unter:
```
http://localhost:8000/docs (Swagger UI)
http://localhost:8000/redoc (ReDoc)
```

## 🔧 Konfiguration

Die Konfiguration erfolgt über die `.env` Datei:

```env
# PostgreSQL Konfiguration
POSTGRES_USER=admin
POSTGRES_PASSWORD=securepassword123
POSTGRES_DB=companies_db
POSTGRES_PORT=5432

# Application Konfiguration
APP_PORT=8000
DATABASE_URL=postgresql://admin:securepassword123@db:5432/companies_db
```

**⚠️ Wichtig**: Ändern Sie das PostgreSQL Passwort für Production!

## 📁 Projektstruktur

```
.
├── main.py                 # FastAPI Backend
├── requirements.txt        # Python Dependencies
├── Dockerfile             # Docker Image für FastAPI
├── docker-compose.yml     # Docker Compose Konfiguration
├── .env                   # Umgebungsvariablen
├── README.md              # Diese Datei
├── templates/
│   └── index.html         # Jinja2 Template (Dashboard)
└── static/
    └── app.js             # JavaScript (Frontend Logic)
```

## 🎯 API Endpoints

### Unternehmen
- `GET /api/unternehmen` - Liste aller Unternehmen (mit Pagination, Suche, Sort)
- `GET /api/unternehmen/{id}` - Details eines Unternehmens
- `POST /api/unternehmen` - Neues Unternehmen erstellen
- `PUT /api/unternehmen/{id}` - Unternehmen aktualisieren
- `DELETE /api/unternehmen/{id}` - Unternehmen löschen

### Personen
- `POST /api/unternehmen/{id}/personen` - Person zu Unternehmen hinzufügen
- `PUT /api/personen/{id}` - Person aktualisieren
- `DELETE /api/personen/{id}` - Person löschen

### Export
- `GET /api/export/csv` - CSV Export aller Unternehmen
- `GET /api/export/excel` - Excel Export aller Unternehmen

### Query Parameter (GET /api/unternehmen)
- `skip`: Anzahl zu überspringender Einträge (default: 0)
- `limit`: Maximale Anzahl zurückgegebener Einträge (default: 20, max: 100)
- `search`: Suchbegriff (durchsucht Name, Stadt, PLZ, Bundesland)
- `sort_by`: Sortier-Spalte (name, bundesland, stadt, plz)
- `sort_order`: Sortier-Reihenfolge (asc, desc)

## 🎨 Dashboard Features

### Hauptfunktionen
1. **Suchfeld**: Echtzeit-Suche über alle relevanten Felder
2. **Sortierung**: Klicken Sie auf Spaltenüberschriften zum Sortieren
3. **Pagination**: Navigation durch große Datenmengen
4. **CRUD Actions**: Erstellen, Anzeigen, Bearbeiten, Löschen
5. **Export**: CSV/Excel Download mit einem Klick

### Detailansicht
- Vollständige Unternehmensinformationen
- Ansprechpartner (mit Edit/Delete Optionen)
- Liste aller Empfehler (mit Edit/Delete Optionen)
- Schnelles Hinzufügen neuer Personen

## 🔐 Sicherheit & Best Practices

- ✅ SQL Injection Schutz durch SQLAlchemy ORM
- ✅ Input Validation mit Pydantic
- ✅ XSS Schutz durch HTML Escaping
- ✅ CORS kann in main.py konfiguriert werden
- ⚠️ **Keine Authentifizierung** (wird später via Gateway implementiert)

## 🐛 Troubleshooting

### Container starten nicht
```bash
# Prüfen Sie Docker Status
docker ps

# Logs prüfen
docker-compose logs

# Containers neu starten
docker-compose down
docker-compose up -d --build
```

### Datenbank Connection Fehler
```bash
# Prüfen Sie ob PostgreSQL läuft
docker-compose ps

# Database Container neu starten
docker-compose restart db
```

### Port bereits belegt
Ändern Sie `APP_PORT` in der `.env` Datei:
```env
APP_PORT=8001
```

## 🚀 Produktions-Deployment

Für Production sollten Sie:

1. **Passwörter ändern** in `.env`
2. **Environment Variables** sicher speichern (nicht in Git committen)
3. **HTTPS aktivieren** (z.B. mit Nginx + Let's Encrypt)
4. **Logging konfigurieren** (siehe FastAPI Docs)
5. **Health Checks** implementieren
6. **Backups** für PostgreSQL einrichten
7. **Resource Limits** in docker-compose.yml setzen

## 📚 Weitere Entwicklung

Mögliche Erweiterungen:
- 🔐 Authentifizierung & Autorisierung (JWT)
- 📊 Analytics Dashboard
- 📧 Email Benachrichtigungen
- 📱 Progressive Web App (PWA)
- 🌍 Mehrsprachigkeit (i18n)
- 📄 PDF Export
- 🔍 Erweiterte Filteroptionen
- 📊 Statistiken & Diagramme

## 🤝 Support

Bei Fragen oder Problemen:
1. Prüfen Sie die Logs: `docker-compose logs`
2. Prüfen Sie die API Docs: `http://localhost:8000/docs`
3. Erstellen Sie ein Issue im Repository

## 📝 Lizenz

Dieses Projekt ist für interne Nutzung entwickelt.

---

**Made with ❤️ using FastAPI & Tailwind CSS**