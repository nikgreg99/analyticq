 AnalyticQ
 
**AnalyticQ** è una piattaforma per l'esecuzione automatizzata di analisi **SAST** (Static Application Security Testing) su repository Git o archivi di codice caricati manualmente. Orchestra diversi tool di analisi statica (uno o più per linguaggio) all'interno di container Docker isolati, normalizza i risultati in un formato comune e li espone tramite API REST e una dashboard web, con possibilità di esportare i report in PDF, CSV, JSON e HTML.
 
## Indice
 
- [Caratteristiche principali](#caratteristiche-principali)
- [Architettura](#architettura)
- [Tool SAST supportati](#tool-sast-supportati)
- [Stack tecnologico](#stack-tecnologico)
- [Struttura del repository](#struttura-del-repository)
- [Requisiti](#requisiti)
- [Avvio rapido con Docker Compose](#avvio-rapido-con-docker-compose)
- [Configurazione](#configurazione)
- [Build delle immagini dei tool SAST](#build-delle-immagini-dei-tool-sast)
- [Sviluppo locale](#sviluppo-locale)
- [API principali](#api-principali)
- [Licenza](#licenza)
## Caratteristiche principali
 
- **Analisi da Git o da upload**: avvia una scansione a partire dall'URL di un repository Git (con branch specifico) oppure caricando archivi di file direttamente dalla UI.
- **Esecuzione isolata dei tool**: ogni tool SAST viene eseguito in un container Docker dedicato (tramite Docker-in-Docker), garantendo isolamento e riproducibilità.
- **Multi-linguaggio**: rilevamento automatico dei linguaggi presenti nel codice e selezione dei tool pertinenti.
- **Normalizzazione dei risultati**: gli output eterogenei dei vari tool vengono convertiti in un modello dati comune (issue, severità, confidenza, metriche).
- **Elaborazione asincrona**: le scansioni vengono gestite in background tramite Celery e RabbitMQ, con tracciamento dello stato dell'analisi.
- **Persistenza e storico**: i risultati delle scansioni sono salvati su PostgreSQL e consultabili/paginabili via API.
- **Reportistica**: generazione di report in PDF, CSV, JSON e HTML a partire dai risultati aggregati.
- **Dashboard web**: interfaccia React per avviare analisi, monitorarne l'avanzamento, esplorare le issue e scaricare i report.
## Architettura
 
Il sistema è composto dai seguenti servizi (vedi `docker-compose.yml`):
 
| Servizio | Descrizione |
|---|---|
| `analyticq-frontend` | Web app React (Vite + Chakra UI) servita sulla porta `8080` (mappata su `5173` interna) |
| `analyticq-backend` | API FastAPI che espone gli endpoint di analisi, scansione, report e gestione tool, sulla porta `8000` |
| `postgres` | Database PostgreSQL per la persistenza di scan, issue e statistiche |
| `docker-dind` | Docker-in-Docker, usato dal backend per eseguire i container dei singoli tool SAST in isolamento |
 
Il backend clona/estrae il codice da analizzare, individua i linguaggi presenti, seleziona i tool SAST registrati per ciascun linguaggio, li esegue come container tramite `docker-dind`, effettua il parsing degli output nel modello dati comune di AnalyticQ e salva i risultati su PostgreSQL, rendendoli disponibili via API e nella dashboard.
 
## Tool SAST supportati
 
La configurazione dei tool è definita in [`sast-tools-config.json`](./sast-tools-config.json) e le relative immagini Docker si trovano in [`sast-tools/`](./sast-tools):
 
| Linguaggio | Tool |
|---|---|
| Python | Bandit, Flake8, Pylint, Pyright |
| Go | Staticcheck, Gosec |
| C / C++ | Flawfinder, Cppcheck |
| PHP | PHPStan |
| Ruby | RuboCop, Brakeman |
| JavaScript | ESLint, njsscan |
| Java | Checkstyle, SpotBugs |
| Multi-linguaggio | Bearer |
 
## Stack tecnologico
 
**Backend**
- Python, [FastAPI](https://fastapi.tiangolo.com/) + Uvicorn
- SQLAlchemy (async) + Alembic per le migrazioni, PostgreSQL (`asyncpg`)
- Celery + RabbitMQ per l'elaborazione asincrona
- `aiodocker` / Docker SDK per orchestrare i container dei tool SAST
- GitPython per la gestione dei repository Git
- Generazione report con Jinja2, xhtml2pdf/reportlab, pypdf
**Frontend**
- React 19 + Vite
- Chakra UI, Framer Motion
- Redux Toolkit / React Redux
- React Router, Axios, react-dropzone, react-csv
**Infrastruttura**
- Docker & Docker Compose
- Docker-in-Docker (`docker:dind`) per l'esecuzione isolata dei tool
## Struttura del repository
 
```
analyticq/
├── analyticq-backend/          # API FastAPI, motore di analisi, manager Docker/DB/Celery
│   ├── analyticq/
│   │   ├── api/                 # Router REST (analyze, scans, tools, issues, report, stats, health)
│   │   ├── engine/               # Discovery/registro tool, analyzer, parser degli output
│   │   ├── manager/               # Gestione container Docker, immagini, DB, Celery
│   │   ├── model/ & schemas/      # Modelli dati e DTO
│   │   ├── repository/            # Accesso ai dati (scan, issue, statistiche)
│   │   ├── report/                # Generatori di report (CSV, JSON, HTML, PDF)
│   │   └── service/                # Logica applicativa (scan, issue, report, git auth)
│   ├── alembic/                  # Migrazioni database
│   ├── tests/                     # Test suite
│   └── Dockerfile
├── analyticq-frontend/          # Dashboard React (Vite)
│   └── Dockerfile
├── sast-tools/                   # Dockerfile/config per ciascun tool SAST, per linguaggio
├── sast-tools-config.json        # Registro dei tool SAST disponibili
├── build_sast_tools.sh / Build-SASTools.ps1   # Build delle immagini dei tool SAST (bash/PowerShell)
├── pull_sast_tools.sh / Pull-SASTools.ps1     # Pull delle immagini dei tool SAST già pubblicate
├── scripts/                      # Script di utilità (gestione release, aggiornamento requirements)
├── docker-compose.yml            # Orchestrazione dei servizi
├── .env.sample                   # Esempio di configurazione ambiente
└── LICENSE                       # GPL-3.0
```
 
## Requisiti
 
- Docker e Docker Compose
- Git installato sulla macchina (richiesto anche dal backend per clonare i repository)
- Per lo sviluppo locale del frontend: Node.js (compatibile con Vite 6 / React 19)
- Per lo sviluppo locale del backend: Python 3.x
## Avvio rapido con Docker Compose
 
1. Clona il repository:
```bash
   git clone https://github.com/nikgreg99/analyticq.git
   cd analyticq
```
 
2. Copia il file di esempio delle variabili d'ambiente e personalizzalo:
```bash
   cp .env.sample .env
```
 
3. Avvia lo stack:
```bash
   docker compose up -d --build
```
 
4. Servizi disponibili:
   - Frontend: [http://localhost:8080](http://localhost:8080)
   - Backend API: [http://localhost:8000](http://localhost:8000) (documentazione OpenAPI su `/docs`)
## Configurazione
 
Le variabili d'ambiente principali (vedi [`.env.sample`](./.env.sample)) includono:
 
- **Frontend/API**: `VITE_API_PROTOCOL`, `VITE_API_HOST`, `VITE_API_PORT`, `VITE_PORT`
- **Backend**: `SECRET_KEY`, `SECRET_KEY_PROFILE`, `ANALYTICQ_DB_URL`, `ANALYTICQ_FRONTEND_CORS_URL`
- **PostgreSQL**: `POSTGRES_ROOT_USER`, `POSTGRES_ROOT_PASSWORD`, `POSTGRES_NON_ROOT_USER`, `POSTGRES_NON_ROOT_PASSWORD`, `POSTGRES_DB`, `POSTGRES_PORT`
- **RabbitMQ / Celery**: `RABBITMQ_HOST`, `RABBITMQ_AMQP_PORT`, `RABBITMQ_MANAGEMENT_PORT`, `RABBITMQ_DEFAULT_USER`, `RABBITMQ_DEFAULT_PASS`, `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND`
- **Docker**: `DOCKER_VERSION`, `DOCKER_REGISTRY`, `DOCKER_REGISTRY_USER`, `DOCKER_REGISRY_TOKEN`, `DOCKER_STREAM_LOG`
> Nota: il file `.env.sample` fornito nel repository contiene alcuni valori segnaposto/di esempio: verificane e completane il contenuto (in particolare le variabili PostgreSQL non presenti in chiaro nel sample) prima dell'avvio in produzione.
 
## Build delle immagini dei tool SAST
 
Le immagini Docker dei singoli tool SAST possono essere costruite localmente o scaricate da un registry:
 
```bash
# Build locale delle immagini a partire da sast-tools/
./build_sast_tools.sh
 
# Pull delle immagini già pubblicate (es. su un registry come ghcr.io)
./pull_sast_tools.sh
```
 
Sono disponibili anche gli equivalenti PowerShell (`Build-SASTools.ps1`, `Pull-SASTools.ps1`) per ambienti Windows.
 
## Sviluppo locale
 
**Backend**
```bash
cd analyticq-backend
pip install -r requirements.txt
python start.py
```
 
**Frontend**
```bash
cd analyticq-frontend
npm install
npm run dev
```
 
Altri comandi utili del frontend: `npm run lint`, `npm run format`, `npm run build`, `npm run preview`.
 
## API principali
 
Il backend espone (tra gli altri) i seguenti gruppi di endpoint FastAPI:
 
- `POST /analyze/git` — avvia un'analisi su un repository Git (URL, branch, path di configurazione, timeout)
- `POST /analyze/files` — avvia un'analisi su file/archivi caricati
- `GET /analyze/status/{analysis_id}` — stato e risultati di un'analisi in corso
- `GET /scans/` — elenco paginato delle scansioni
- `GET /scans/{scan_id}` — dettaglio di una scansione
- `GET /scans/tool/{tool_name}` — scansioni filtrate per tool
- `GET /tools/list/all` e `GET /tools/list/{language}` — tool SAST registrati, globalmente o per linguaggio
- `GET /tools/supported-languages` — linguaggi supportati
- Router aggiuntivi per **issue**, **report** e **statistiche**
La documentazione interattiva completa è disponibile su `/docs` (Swagger UI) una volta avviato il backend.


# Nota
Il progetto rimane comunque aperto a ulteriori miglioramenti, in particolare per quanto riguarda:
 
- **Ottimizzazione del motore di analisi**: parallelizzazione ed efficienza nell'esecuzione dei tool SAST, gestione di codebase di grandi dimensioni e riduzione dei tempi di scansione.
- **Qualità dei risultati**: affinamento della normalizzazione delle issue tra i vari tool, riduzione dei falsi positivi e arricchimento delle metriche/statistiche.
- **Sicurezza e hardening**: gestione più robusta di credenziali e segreti, isolamento più stringente dei container di analisi, controlli di accesso alle API.
- **Osservabilità**: logging strutturato, metriche e monitoraggio dello stato delle scansioni e dei worker Celery.
- **Copertura tool/linguaggi**: aggiunta di nuovi tool SAST e supporto a ulteriori linguaggi.
Contributi, segnalazioni e suggerimenti sono benvenuti tramite issue o pull request.
 
## Licenza
 
Distribuito sotto licenza **GPL-3.0**. Vedi il file [`LICENSE`](./LICENSE) per i dettagli.
 