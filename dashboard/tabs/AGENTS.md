# 📑 Dashboard Tabs — Renderização por Aba

## Visão Geral
Cada arquivo exporta uma função `render(user, agents)` que desenha uma tab do dashboard. São carregadas por `dashboard/app.py` via `TAB_RENDERERS`.

## Tabs

| Arquivo / Key | Label | O que faz |
|---------------|-------|-----------|
| `resumo.py` | 🏠 Resumo | KPIs, top vendas, progresso XP, missões ativas, alertas estoque |
| `financeiro.py` | 💰 Financeiro | Tesouraria: resumo financeiro, registrar venda, despesas, upload dados |
| `marketing.py` | 📢 Marketing | Análise de campanhas, gerador de prompts Midjourney |
| `atendimento.py` | 🤝 Atendimento | Gerador de respostas (formal/casual/empático), análise sentimento |
| `anuncios.py` | 📦 Meus Anúncios | **A maior tab**. CRUD produtos, upload massa, kits, estoque, importar CSV |
| `concorrencia.py` | 🔍 Concorrência | Monitor de preços (delega para `competitor_view.py`) |
| `configuracoes.py` | ⚙️ Configurações | Provider LLM, API keys (delega para `settings_view.py`) |

## Como Usar

### Para tarefa "Meus Anúncios" (gestão de produtos):
1. **Arquivo principal:** `dashboard/tabs/anuncios.py`
2. **Modelos de dados:** `core/database/models.py` (Product, ProductVariation, InventoryItem, ProductComponent)
3. **Services:** `core/sales_service.py`, `agents/product_agent.py`

### Para tarefa "Financeiro":
1. Abrir `dashboard/tabs/financeiro.py`
2. Abrir `core/database/models.py` (Transaction)
3. Abrir `agents/finance_agent.py`

### Para adicionar nova tab:
1. Criar arquivo com `def render(user, agents):`
2. Adicionar a `TAB_RENDERERS` em `__init__.py`
3. Adicionar em `dashboard/app.py` (tab_labels + tab_keys)

## ⚠️ Regras
- NUNCA importe `dashboard/components/` no nível do módulo (só dentro da função render)
- Use `agents["finance_agent"]` etc para acessar agentes
- Mantenha imports locais dentro da função quando forem raros
