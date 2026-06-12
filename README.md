# 🚀 Shopee Growth Quest — ADM

Dashboard inteligente para gestão de loja **Shopee** no nicho **saúde / bem-estar / suplementos**.

> 🏪 Loja Nutri Active — polivitamínicos, vitamina K2, suplementos DailyLife

---

## ✨ Funcionalidades

| Tab | Descrição |
|-----|-----------|
| 🏠 **Resumo** | KPIs, top vendas, progresso XP, missões, alertas de estoque |
| 💰 **Financeiro** | Tesouraria (receitas/despesas), registrar vendas, COGS, gráficos |
| 📢 **Marketing** | Análise de campanhas, gerador de prompts Midjourney |
| 🤝 **Atendimento** | Gerador de respostas (3 tons), análise de sentimento |
| 📦 **Meus Anúncios** | CRUD produtos, kits, upload massa, importar/exportar CSV |
| 🔍 **Concorrência** | Monitor de preços Shopee, Amazon, Enjoei (Tavily + Firecrawl) |
| ⚙️ **Configurações** | Provider LLM, API keys, toggle IA |

---

## 🧱 Arquitetura

```
dashboard/app.py          ← Entry point (Streamlit)
├── tabs/resumo.py        ← Render por tab
├── tabs/financeiro.py
├── tabs/marketing.py
├── tabs/atendimento.py
├── tabs/anuncios.py       ← Gestão de produtos (módulo maior)
├── tabs/concorrencia.py
├── tabs/configuracoes.py
├── components/            ← Componentes reutilizáveis
│   ├── competitor_view.py
│   └── settings_view.py

agents/                    ← Agentes IA (Product, Finance, Ads, Customer)
core/                      ← Serviços centrais
├── llm_client.py          ← LLM multi-provider (Gemini, OpenRouter, NVIDIA)
├── config.py              ← Config (.env)
├── competitor_service.py  ← Monitor concorrência
├── sales_service.py       ← Vendas
├── database/              ← SQLModel + SQLite
│   ├── models.py          ← 9 tabelas
│   ├── engine.py
│   └── migrations/
└── gamification/          ← XP, níveis, missões

scrapers/                  ← Coleta de preços (Tavily + Firecrawl)
├── shopee_scraper.py
├── amazon_scraper.py
├── enjoei_scraper.py
└── web_scraper.py
```

---

## 🚀 Como Rodar

```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Configurar .env (copie .env.example ou edite diretamente)
#    Precisa de: TAVILY_API_KEY, FIRECRAWL_API_KEY, GEMINI_API_KEY (ou OPENROUTER_API_KEY)

# 3. Rodar
streamlit run dashboard/app.py
```

Ou clique duas vezes em `run_app.bat`.

---

## 📊 Estado Atual

| Métrica | Valor |
|---------|-------|
| Produtos cadastrados | **39** |
| Itens de inventário | **13** |
| Transações registradas | **281** |
| Receita total | **R$ 10.440,00** |
| Lucro estimado | **~R$ 8.000** (76% margem) |

---

## 🧠 Navegação para IA (Hermes / Claude)

Este projeto usa **AGENTS.md** em cada pasta para otimizar o contexto de modelos de IA:

1. **Raiz**: [`AGENTS.md`](./AGENTS.md) — mapa de navegação
2. **Por módulo**: cada pasta tem seu `AGENTS.md` explicando o que contém e como usar
3. **CLAUDE.md**: carregado automaticamente pelo Hermes no início da sessão

👉 **Sempre leia o AGENTS.md** da pasta relevante antes de abrir arquivos.

---

## 📋 Próximos Passos (roadmap resumido)

- [x] Fase 1: Migração google.genai + smoke test
- [x] Fase 2: Migração Tavily + Firecrawl (Playwright removido)
- [ ] Fase 3: Bundle UI + alertas de reposição
- [ ] Fase 4: Gamificação avançada
- [ ] Fase 5: Integração oficial API Shopee
- [ ] Fase 6: Multi-usuário + deploy

---

## 🔑 API Keys Necessárias

| Serviço | Onde conseguir |
|---------|---------------|
| Tavily | https://tavily.com — plano gratuito (1000 créditos/mês) |
| Firecrawl | https://firecrawl.dev — plano gratuito (500 páginas/mês) |
| Gemini | https://aistudio.google.com — gratuito |
| OpenRouter | https://openrouter.ai — vários modelos, pague por uso |
