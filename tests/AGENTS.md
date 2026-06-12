# 🧪 Tests — Testes Automatizados

## Visão Geral
Testes unitários e de integração.

## Status
🚧 **Pasta preparada para testes — nenhum implementado ainda.**

## Como Adicionar Testes
```bash
# Rodar todos os testes
python -m pytest tests/

# Rodar um arquivo específico
python -m pytest tests/test_scrapers.py -v
```

## Convenções
- Testes usam `pytest`
- Nome dos arquivos: `test_*.py`
- Mock Tavily/Firecrawl em testes de scraper (não chamar API real)
