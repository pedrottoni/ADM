# Tests — Automated Tests

## Overview
Unit and integration tests.

## Status
🚧 **Prepared for tests — none implemented yet.**

## How to Add Tests
```bash
# Run all tests
python -m pytest tests/

# Run specific file
python -m pytest tests/test_scrapers.py -v
```

## Conventions
- Tests use `pytest`
- File naming: `test_*.py`
- Mock Tavily/Firecrawl in scraper tests (don't call real APIs)
