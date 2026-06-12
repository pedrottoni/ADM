# 📊 Dashboard — Interface Streamlit

## Visão Geral
Frontend Streamlit do ADM. Entry point em `app.py`, cada tab é um módulo separado em `tabs/`.

## Arquivos

| Arquivo | Propósito |
|---------|-----------|
| `app.py` | **Entry point**. Inicializa DB, agents, sidebar. Cria 7 tabs e delega renderização |
| `main.py` | ⚠️ **Depreciado**. Redireciona para `app.py` |

## Submódulos

### `tabs/` → [AGENTS.md](./tabs/AGENTS.md)
Uma função `render(user, agents)` por tab.

### `components/` → [AGENTS.md](./components/AGENTS.md)
Componentes UI reutilizáveis (concorrência, configurações).

## Como Usar

### Para rodar o dashboard:
```bash
streamlit run dashboard/app.py
```

### Para adicionar uma nova tab:
1. Criar `dashboard/tabs/nova_tab.py` com função `render(user, agents)`
2. Adicionar em `dashboard/tabs/__init__.py` → `TAB_RENDERERS`
3. Adicionar label + key em `dashboard/app.py`

### Para tarefa "quero mexer na tab Financeiro":
1. Abrir `dashboard/app.py` (entry point)
2. Abrir `dashboard/tabs/financeiro.py` (render da tab)
3. `core/` e `core/database/` se precisar de dados

## Dependências
- `agents/` — todas as tabs usam agents
- `core/` — config, llm_client
- `core/database/` — models + engine
- `dashboard/tabs/AGENTS.md` — documentação por tab
