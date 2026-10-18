# GitHub Analytics ETL Pipeline

A small ETL pipeline in Python that extracts issues from the GitHUb REST API, normalizes them, computes how long each issue took to close, and loads the result into a PostgreSQL database running in DOcker.

```text
GitHub API -> extract.py -> transform.py -> load.py -> PostgreSQL (Docker)

```text

## Features

- **Extract:** paginated fetch of a repository's from the Github API, authenticated with a personal acces token.
- **Transform:** normalizes each issue into a flat record and derives `time_to_close_hours` for closed issues.
- **Load:** creates the table in needed and upserts rows by primary key, so re-running the pipeline updates existing issues instead for duplicating them.
- **Config via `.env`:** repository, token and database credentials are never hardcoded.

## Tech Stack

- Python 3.14
- `psycopg` (v3, binary build) for PostgreSQL
- `python-dotenv` for configuration
- PostgreSQL in Docker Compose

## Project structure

```text

|-- extract.py                  # GitHub API client (paginated issue fetch)
|-- transform.py                # normalize_issue() and time_to_close_hours()
|-- transform.py                # normalize_issue() and time_to_close_hours()
|-- load.py                     # schema creation and upsert into Potgres
|-- main.pu                     # orchestrates extract -> transform -> load
|-- docker-compose.yml          # PostgreSQL service
|-- requirements.txt
|-- .env.example                # configuration template

```

## Getting started

### 1. Clone and create a virtual enviroment

```bash
git clone https://github.com/whoismarce/github-analytics-etl-pipeline.git
cd github-analytics-etl-pipeline

python -m venv venv
source venv/Scripts/activate      # Git Bash on Windows
# source venv/bin/activate        # macOs / Linux

pip install -r requirements.txt

```text

### 2. COnfigure enviroment variables

```bash
cp .env.example .env

```

Edit `.env`:

```dotenv
GITHUB_TOKEN=your_github_personal_access_token
GITHUB_REPO=owner/repo
DB_HOST=localhost
DB_PORT=5432
DB_NAME=github_analytics
DB_USER=etl_user
DB_PASSWORD=etl_password

```

- `GITHUB_REPO` must be in `owner/repo` format (for example `microsoft/vscode`).
- Create the token in GitHub under *Settings > Developer settings > Personal access token.* Never commit `.env`; it is listed in `.gitignore`.

### 3. Start PostgreSQL

```bash
docker-compose up -d
```

Expected output:

```text
[INFO] etl: Starting ETL run for microsft/vscode
[INFO] ectract: Fetching microsoft/vscode issues page 1
[INFO] etl: Extrated and transformed 100 issues.
[INFO] load: LOaded/updated 100 rows.
[INFO] etl: ETL run complete.

```

By default the pipeline reads up to 5 pages of issues per run (`max_pages=5` in `main.py`)

## Data model

Table `issues`:

| Column                | Type        | Description                                      |
|-----------------------|-------------|--------------------------------------------------|
| `id`                  | BIGINT (PK) | GitHub issue id                                  |
| `number`              | INT         | Issue number within the repository               |
| `title`               | TEXT        | Issue title                                      |
| `state`               | TEXT        | `open` or `closed`                               |
| `is_pull_request`     | BOOLEAN     | The GitHub issues endpoint also returns PRs      |
| `created_at`          | TIMESTAMPTZ | Creation timestamp                               |
| `closed_at`           | TIMESTAMPTZ | Closing timestamp (null while open)              |
| `comments`            | INT         | Number of comments                               |
| `author`              | TEXT        | GitHub login of the author                       |
| `time_to_close_hours` | NUMERIC     | Hours between creation and closing (null if open)|

## Example queries

Connect to the database:

```bash
docker exec -it github-analytics-etl-pipeline-postgres-1  \
psql -u etl_user -d github_analytics

```

Slowest issues to close:

```sql
SELECT number, title, time_to_close_hours
FROM issues
WHERE state = 'closed' AND is_pull_request = false
ORDER BY time_to_close_hours DESC
LIMIT 10;

```

Average time to close, by author:

```sql
SELECT author, COUNT(*) AS issues, ROUND(AVG(time_to_close_hours), 2)
AS avg_hours
FROM issues
WHERE state = 'closed'
GROUP BY author
ORDER BY issues DESC
LIMIT 10;

```

<!-- Add a screebshot of a query result here, e.g. !>[Query result](docs/query-result.png) -->

## Notes

- The pipeline is idempotent: rows are upserted on `id`, updating
`state`, `closed_at`, `comments` and `time_to_close_hours` when an issue changes.
- `psycopg` (v3) is used instead of `psycopg2-binary`, which does not currently install cleanly on Python 3.14 for Windows.

## Possible improvements

- Incremental loads using the API's `since` parameter.
- Retry and rate-limit handling for the GitHub API.
- Scheduling with GitHub Actions or cron.
- Unit tests for `transform.py`.
