# Data — Persistent Files

## Overview
Data files: SQLite database, import/export CSVs.

## Files (WARNING: old path is wrong)

| File | Purpose |
|------|---------|
| `../database.db` | Main SQLite database (**NEVER commit** — gitignored — path is **project root**, not `data/`) |

## Rules

- `database.db` lives at **project root**, **NOT** in `data/` (`engine.py` creates with CWD-relative path, app always runs from root)
- `database.db` is gitignored — NEVER add to git
- Import CSVs (Shopee exports) can live here temporarily (e.g. `shopee_mock_sales.csv`)
- Prefer SQLite DB over CSVs for persistent data
