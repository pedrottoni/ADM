# 📁 Data — Dados Persistentes

## Visão Geral
Arquivos de dados: banco SQLite, CSVs de importação/exportação.

## ⚠️ Arquivos (ATENÇÃO: caminho antigo está errado)

| Arquivo | Propósito |
|---------|-----------|
| `../database.db` | Banco SQLite principal (⚠️ **NÃO commitar** — está no `.gitignore` — caminho é **raiz do projeto**, não `data/`) |

## ⚠️ Regras

- O `database.db` mora na **raiz**, **não** em `data/` (`engine.py` cria com path relativo ao CWD, e o app é sempre rodado da raiz)
- `database.db` está no `.gitignore` — NUNCA adicionar ao git
- CSVs de importação (export Shopee) podem ficar aqui temporariamente (ex: `shopee_mock_sales.csv`)
- Prefira usar o SQLite DB para dados persistentes em vez de CSVs
