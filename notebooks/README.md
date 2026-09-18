# Notebooks

PostgreSQL is the system being studied; notebooks provide the working interface.

Notebook structure:

1. Context or objective
2. SQL statement
3. Result
4. Short observation

SQL handles relational extraction, filtering, joins, related-record summaries, and timestamp calculations. Python handles connections, validation, synthetic generation, and the segment summaries and conditional formatting in notebook 04.

- `00_connection_check.ipynb` verifies the local PostgreSQL configuration.
- `01_build_database_model.ipynb` defines and inspects the first-version schema.
- `02_generate_synthetic_data.ipynb` generates, validates, and loads the deterministic synthetic dataset.
- `03_validate_business_rules.ipynb` uses rolled-back writes to test constraints and expose cross-table rule gaps.
- `04_data_scientist_database_case_study.ipynb` extracts offer-level data, compares segments in Python, examines cancellations, ratings, and reports, and prepares a filtered investigation extract. It does not include a final campaign decision or an index experiment.

Additional notebooks are added when a distinct dataset or SQL topic requires one.
