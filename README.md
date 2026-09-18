# Mansoura Mobility Analytics

A PostgreSQL project exploring a fictional ride-hailing marketplace around Mansoura and Talkha, Egypt. It combines relational database design, schema creation, reproducible synthetic data, business-rule checks, and an operational risk investigation.

SQL is executed from Python Jupyter notebooks using `MAna.database`. PostgreSQL handles relational queries; Python supports generation, validation, and the segment summaries in notebook 04.

## Database model

The model contains 13 tables:

| Area | Tables | Purpose |
|---|---|---|
| Users and vehicles | `accounts`, `passengers`, `drivers`, `vehicles` | Shared accounts, passenger/driver roles, and driver-owned vehicles |
| Geography | `zones`, `zone_routes` | Pickup/drop-off areas and directional route baselines |
| Marketplace | `offers`, `rides` | Offers and trips created from accepted offers |
| Payments | `payment_attempts`, `refunds` | Payment retries, authorizations, captures, and refunds |
| Quality | `passenger_driver_ratings`, `driver_passenger_ratings`, `reports` | Ratings in both directions and ride reports |

An account can be both a passenger and a driver. An offer can exist without a ride; each ride references one offer. A ride can have multiple payment attempts and reports, while each rating direction allows at most one row per ride.

See the [relationship diagram](docs/03_conceptual_erd.md), [foundation model](docs/04_foundation_logical_model.md), and [operational model](docs/05_remaining_logical_model.md). Notebook 03 distinguishes enforced constraints from rules that still need application or database logic.

## Synthetic data

All user details, trips, financial records, ratings, and reports are synthetic—not real customer data. Place names provide context; generated patterns are not evidence of actual conditions in Mansoura.

The default generator uses seed `20260830` and a fixed simulation end timestamp. It produces 180 days of activity with 1,000 passengers, 100 drivers, 20 dual-role accounts, 15 zones, 14,000 offers, and roughly 10,000 rides. Exact counts depend on simulated outcomes.

Records are validated before loading, with PostgreSQL checks afterward. Loading uses `COPY`; existing data is not replaced unless explicitly enabled.

## Setup

Requirements:

- Python 3.12 or newer for the current notebook syntax.
- A running PostgreSQL server and permission to create a database. Development used PostgreSQL 15.
- Git, used to install the separate **MAna** package from GitHub with its `database` extras.

From the project directory in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[notebooks,dev]"
python -m pip install matplotlib pyperclip
python -m pip install "M_Ana_package[database] @ git+https://github.com/mohamed1249/M-Ana.git@main"
Copy-Item .env.example .env
```

MAna is installed from its public GitHub source; no separate local checkout is needed. Create an empty database using pgAdmin or `psql`:

```sql
CREATE DATABASE mansoura_mobility;
ALTER DATABASE mansoura_mobility SET timezone TO 'Africa/Cairo';
```

Edit `.env` with your PostgreSQL host, port, database, username, and password. `.env.example` contains placeholders only. Do not commit real credentials.

Notebooks currently set `project_root` to `C:\Python\projects\pgSQL`. If your checkout is elsewhere, change that value in each notebook's setup cell.

Register the environment and start JupyterLab:

```powershell
python -m ipykernel install --user --name mansoura-mobility --display-name "Python (Mansoura Mobility)"
python -m jupyter lab
```

Choose the **Python (Mansoura Mobility)** kernel and run cells in order.

## Notebook order

| Notebook | Purpose |
|---|---|
| [00 — Connection check](notebooks/00_connection_check.ipynb) | Loads configuration and verifies PostgreSQL access |
| [01 — Database model](notebooks/01_build_database_model.ipynb) | Creates and inspects the 13-table schema |
| [02 — Synthetic data](notebooks/02_generate_synthetic_data.ipynb) | Generates, validates, and optionally loads the dataset |
| [03 — Business rules](notebooks/03_validate_business_rules.ipynb) | Tests constraints with rolled-back writes and documents rule gaps |
| [04 — Promotion risk investigation](notebooks/04_data_scientist_database_case_study.ipynb) | Extracts offer-level data, compares segments in Python, examines cancellations and quality signals, and prepares a filtered ride extract |

Notebook 02 defaults to `LOAD_TO_POSTGRESQL = False`: generation without insertion. Set it to `True` to populate the empty schema. Keep `REPLACE_EXISTING_DATA = False` unless deliberately replacing existing data.

Notebook 01 includes a **disabled** reset command that drops project tables. Leave it disabled to preserve data. Do not rerun schema creation against existing tables unless deliberately rebuilding.

Notebook 04 is exploratory, not a final campaign launch recommendation or proof of causal effects. Its Stage 3 payment-secured count currently includes completed rides only, and its Stage 3 report-rate denominator uses completed rather than started rides. Those measures should not be treated as the defined business KPIs; Stage 5 calculates the started-ride report rate separately.

## Repository layout

```text
docs/                       business rules and model documentation
notebooks/                  schema, generation, validation, and analysis
sql/                        durable database objects when introduced
src/mansoura_mobility/       generator and support code
tests/                      generator tests
.env.example                safe example configuration
```

Exploratory queries stay in notebooks. Reusable migrations, views, and administration SQL belong under `sql/` when introduced; queries do not need duplication.

Run generator tests without changing the database:

```powershell
python -m unittest discover -s tests -v
```

## Configuration safety

Git excludes `.env`, local environment variants, common credential files, PostgreSQL password/service files, and private keys. Only the placeholder `.env.example` is intended for publication. Check notebook outputs before publishing if connection errors or configuration values have been displayed.

## Further documentation

- [Business rules](docs/01_business_rules.md)
- [Database model plan](docs/02_database_model_plan.md)
