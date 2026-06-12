# 📁 Data — Dados Persistentes

## Visão Geral
Arquivos de dados: banco SQLite, CSVs de importação/exportação.

## Arquivos

| Arquivo | Propósito |
|---------|-----------|
| `database.db` | Banco SQLite principal (⚠️ **NÃO commitar** — está no `.gitignore`) |

## ⚠️ Regras
- `database.db` está no `.gitignore` — NUNCA adicionar ao git
- CSVs de importação (export Shopee) podem ficar aqui temporariamente
- Prefira usar o SQLite DB para dados persistentes em vez de CSVs
