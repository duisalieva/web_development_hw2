# Rate My Mort! 🐭💗

A playful rating website made with **Flask, PostgreSQL, and Docker Compose**. Visitors give Mort a score from **1 to 10** and receive a funny reaction. Votes are saved in PostgreSQL; statistics are available through the API (without extra elements on the simple page).

This project extends the first **Hello Sabog!** Flask + Docker homework into a **two-container** web application.

## What it does

- Displays Mort's picture and lets a visitor vote from 1–10.
- Returns a different reaction for ratings 1–3, 4–6, 7–9, and 10.
- Saves every vote in PostgreSQL and reads all ratings to calculate statistics.
- Makes vote statistics (total, average, mode, range, and distribution) available at `GET /api/stats`. The page intentionally displays only Mort, the rating buttons, and the reaction.
- Persists PostgreSQL data in a named Docker volume even after containers are recreated.

## Run the application

**Requirements:** Docker Desktop with Docker Compose.

1. Ensure `.env` exists next to `compose.yaml`. If `.env` is missing (for example, after downloading the public project archive), create it from `.env.example` and set `POSTGRES_PASSWORD` to a strong, private value:

   ```bash
   cp .env.example .env
   ```

2. Start both containers from this folder:

   ```bash
   docker compose up --build
   ```

   You can also use just `docker compose up` (Compose builds a missing backend image automatically).

3. Open **http://localhost:5050** in your browser. Host port 5050 is used to avoid a common macOS conflict on port 5000; Flask still listens on internal port 5000.

Both the PostgreSQL table and its initial structure are created automatically. No separate SQL commands are required.

### API endpoints

| Method | URL | Description |
| --- | --- | --- |
| `GET` | `/` | Web page |
| `GET` | `/api/stats` | Reads rating statistics from PostgreSQL |
| `POST` | `/api/rate` | Validates a rating (1–10), writes it to PostgreSQL, and returns Mort's reaction plus updated statistics |

Example rating request:

```bash
curl -X POST http://localhost:5050/api/rate \
  -H 'Content-Type: application/json' \
  -d '{"rating":10}'
```

Example statistics request:

```bash
curl http://localhost:5050/api/stats
```

Invalid values like `0`, `11`, and strings produce a **400 Bad Request** response. Valid ratings produce a **201 Created** response.

### Test PostgreSQL directly

```bash
docker compose exec db sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT * FROM ratings ORDER BY id DESC LIMIT 10;"'
```

### Show persistent storage

1. Vote on the website and check the total with `curl http://localhost:5050/api/stats`.
2. Stop and remove the containers (but **keep the volume**):

   ```bash
   docker compose down
   ```

3. Start again with `docker compose up`.
4. Run `curl http://localhost:5050/api/stats` again: the saved votes remain unchanged.

The named volume is `mort_postgres_data` (Compose prefixes it with the project name). **Do not use `docker compose down -v`** for this demonstration: `-v` intentionally deletes the volume and its data.

### Architecture

```text
Browser
   |
   | http://localhost:5050
   v
Flask backend (custom Dockerfile)
   |
   | PostgreSQL connection (host = db, internal port 5432)
   v
PostgreSQL 17 (db service)
   |
   v
Named Docker volume: mort_postgres_data
```

`compose.yaml` configures the services, a private Docker network, the browser-facing port, database credentials from environment variables, a health check, and the `depends_on` startup condition.

**Security:** Real credentials belong only in `.env`. `.env` is listed in both `.gitignore` and `.dockerignore` and **must not** be committed to GitHub. `.env.example` has dummy credentials only. The PostgreSQL port is not exposed to the host.

## File structure

```text
Rate_My_Mort/
├── app.py              # Flask backend, SQL reads/writes, API and reactions
├── compose.yaml        # Two Docker services + network + named volume
├── Dockerfile           # Custom backend image
├── requirements.txt    # Flask + PostgreSQL driver
├── templates/
│   └── index.html      # Website layout
├── static/
│   ├── app.js          # Vote submission and reaction
│   ├── styles.css      # Minimal website layout
│   └── mort.svg        # Bundled cartoon illustration/fallback
├── .env                # Local only! Never push to GitHub.
├── .env.example        # Public configuration template
├── .gitignore
├── .dockerignore
└── README.md
```

### Add your original Mort photo

The original `static/mort.jpeg` was referenced in the first homework, but was **not included in the files available for this version**. To keep the project ready to run, it comes with a bundled `static/mort.svg` illustration. **If you copy your original picture to `static/mort.jpeg`, the backend automatically prefers it**. Then rebuild (`docker compose up --build`) and reload the page.

## Submitting this homework

1. Push this folder to a **public GitHub repo** (the `.env` file stays ignored).
2. Attach the actual `.env` file **separately in the assignment system**, as requested by the instructor. It contains a password; share it only with the instructor through the designated secure submission channel.
3. Submit the GitHub link and click **Turn in**.

## Short defense script (English)

> For my second assignment, I extended my first Flask app, Hello Sabog, into a multi-container project called Rate My Mort. Visitors can rate Mort from one to ten. Flask validates each vote, writes it into the PostgreSQL database using an SQL INSERT statement, and sends a funny reaction depending on the score. The statistics endpoint uses SQL SELECT and GROUP BY to read votes and calculate the total, average, most popular score, range, and rating distribution. I kept the interface minimal, but the API still provides these statistics. Docker Compose starts two services: backend and db. The backend image is built from my custom Dockerfile. Both services communicate over a Docker network using the service name db. The PostgreSQL service has a health check, and the backend waits until it is ready. I store credentials in environment variables from .env, and this file is excluded from GitHub. Finally, PostgreSQL data is kept in a named Docker volume. Even after docker compose down and docker compose up, the ratings remain available.
