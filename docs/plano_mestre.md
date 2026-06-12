# 📋 Plano Mestre — Shopee Growth Quest (ADM)

> Versão: 1.0 — 12/jun/2026
> Baseado em inspeção completa do projeto em `C:\Proiectum\Loja\ADM`

---

## 🩺 Diagnóstico Inicial (Status Quo)

### Ambiente
| Item | Status | Detalhe |
|------|--------|---------|
| Python 3.11.15 (Hermes venv) | ✅ | Disponível |
| pip instalado no venv | ✅ | `ensurepip` rodado |
| Dependências instaladas | ✅ | 28 pacotes (streamlit 1.58, sqlmodel 0.0.38, etc.) |
| Playwright browser binaries | ❌ | `playwright install` pendente |
| `google.generativeai` deprecated | ⚠️ | Migrar para `google.genai` |
| `.env` com chaves reais | ✅ | GOOGLE_API_KEY, OPENROUTER_API_KEY, NVIDIA_API_KEY |

### Database (SQLite — 295KB)
| Métrica | Valor |
|---------|-------|
| **Produtos (anúncios)** | 39 — todos com título, descrição, preço, estoque |
| **Itens de inventário (potes físicos)** | 13 — com supplier_price, stock, min_stock |
| **ProductComponent (kits)** | 39 registros — todos os 39 produtos linkados a inventário |
| **Transações** | 281 (272 vendas + 9 despesas) |
| **Receita total** | **R$ 10.400,63** |
| **Despesas totais** | R$ 2.378,11 |
| **Lucro líquido** | **R$ 8.022,52** |
| **CompetitorListing** | 0 registros — scraping nunca rodou |
| **Missions** | 0 — gamificação não usada |
| **ProductVariation** | 0 — variações não usadas |
| **Low stock alerts** | 0 — nenhum item abaixo de min_stock |

### Dashboard (`dashboard/main.py`)
| Item | Valor |
|------|-------|
| Linhas | 1.333 (monólito) |
| Funções | 2 (`load_user_data` + `main`) |
| Seções visuais | Resumo, Financeiro, Marketing, Customer, Produtos |
| Concorrência | Em componente separado (`components/competitor_view.py`) |
| Configurações | Em componente separado (`components/settings_view.py`) |
| `print()` statements | 0 (limpo) |
| `st.tab()` | **Não usado** — layout via st.header + st.subheader |

---

## 🏗️ PLANO DE TRABALHO — 9 FRENTES

### 🔴 FASE 1 — Estabilização (fundação)

#### 1.1 Playwright + Browser Binaries
**O que**: Instalar o Chromium do Playwright para scrapers e browser engine funcionarem.
**Por que**: `BrowserEngine` depende do Playwright. Scrapers de marketplace não rodam sem.
**Como**: `python -m playwright install chromium`
**Risco**: Download ~150MB. Pode falhar em rede lenta.

#### 1.2 Migração `google.generativeai` → `google.genai`
**O que**: Substituir o SDK legado pelo novo (`google-genai`).
**Por que**: O pacote antigo não recebe mais atualizações/bugfixes.
**Onde**: `core/llm_client.py` (~194 linhas) — reescrever setup do provider Gemini.
**Risco**: Baixo — API novo SDK é semelhante. Testar com uma chamada de diagnóstico.

#### 1.3 Teste de Fumaça do Dashboard
**O que**: Rodar `streamlit run dashboard/main.py` e verificar se carrega sem erros.
**Por que**: Validar que todo ecossistema (imports, DB, LLM config) funciona.
**Como**: 
```bash
streamlit run dashboard/main.py --server.headless true &
# Verificar se sobe na porta 8501
```

---

### 🔴 FASE 2 — Qualidade e Manutenibilidade

#### 2.1 Infraestrutura de Testes
**O que**: Criar estrutura mínima de testes (pytest).
**Por que**: Zero testes — qualquer mudança é feita no escuro.
**O que testar primeiro**:
- `SalesService.match_product()` — lógica de fuzzy match
- `finance_agent.py` — CRUD de transações
- `core/database/models.py` — validação de schemas
- `core/config.py` — leitura/escrita de `.env`

#### 2.2 Refatorar Dashboard Monolítico
**O que**: Quebrar `dashboard/main.py` (1.333 linhas) em módulos por seção.
**Por que**: Arquivo único dificulta manutenção, debugging e paralelismo de desenvolvimento.
**Como**:
```
dashboard/
├── main.py              # Entry point + layout shell
├── pages/
│   ├── resumo.py        # KPIs, top vendas, alertas
│   ├── financeiro.py    # Tesouraria, transações, upload CSV
│   ├── marketing.py     # Análise de campanhas, prompts
│   ├── atendimento.py   # Customer Hero
│   ├── produtos.py      # Gestão de anúncios, kits, estoque
├── components/
│   ├── competitor_view.py   # ✅ já existe
│   └── settings_view.py     # ✅ já existe
```
**Risco**: Streamlit não tem suporte nativo a múltiplos arquivos numa single-page app. Solução: usar funções importadas ou `st.Page`/`st.navigation` (novo no Streamlit 1.36+).

#### 2.3 Corrigir Gotchas Conhecidos
- `LLM_ENABLED` é string `"true"` no `.env` (não booleano) — documentar e validar
- `CompetitorListing` tabela = `competitorlisting` (lowercase, sem separador) — documentar
- Product usa `title` (não `name`) — consistência no código
- `browser_session/` é gitignored — cookies não persistem entre clones

---

### 🟡 FASE 3 — Features Pendentes (Alta Prioridade)

#### 3.1 Bundle UI — Interface de Composição de Kits
**O que**: Interface visual no Dashboard (seção Produtos) para:
- Listar todos os `InventoryItem` disponíveis
- Arrastar/quantificar componentes de um `Product`
- Visualizar árvore de componentes (Product → InventoryItems com quantidades)
**Por que**: Hoje a composição de kits é via código/dados brutos. O vendedor precisa montar kits manualmente.
**Onde**: Tab "📦 Gestão de Anúncios" — nova subseção ou modal.
**SQL**: `INSERT INTO productcomponent (product_id, inventory_item_id, quantity) VALUES (?, ?, ?)`
**UX**: Streamlit `data_editor` + selectbox + botão "Vincular"

#### 3.2 Alertas de Reposição Inteligentes
**O que**: Sistema que alerta quando `InventoryItem.stock` está baixo, baseado em:
- `min_stock` atual (estático)
- **Ritmo de vendas**: quantas unidades de cada InventoryItem foram vendidas nos últimos 7/30 dias (via ProductComponent → Transaction)
- Projeção: "Se continuar nesse ritmo, estoque acaba em X dias"
**Por que**: Sem vendas ainda, mas a lógica precisa estar pronta para quando começar a vender.
**Onde**: Dashboard tab "📦 Gestão de Anúncios" + notificação no "🏠 Resumo"

---

### 🟢 FASE 4 — Features Pendentes (Média Prioridade)

#### 4.1 Gerador de Prompts de Imagem
**O que**: A partir da descrição do produto, gerar prompt otimizado para Midjourney / DALL-E.
**Onde**: Tab "📢 Central de Marketing" (já tem subseção "Gerador de Prompts" — verificar se já implementado).
**Depende**: LLM ativo (provider configurado no .env).

#### 4.2 Dashboard de Cohort / LTV
**O que**: Análise de retenção de clientes ao longo do tempo.
**Depende**: Dados de vendas com identificação de cliente (hoje não tem — precisa de modelagem nova ou campo `customer_name` em Transaction).
**Complexidade**: Média. Requer nova coluna/model ou extração dos CSVs da Shopee.

#### 4.3 Dashboard de Concorrência (🔍 Tab)
**O que**: Tab de Concorrência está em componente separado (`competitor_view.py`), mas **não aparece na navegação principal**. Integrar no layout principal.
**Por que**: Usuário não consegue acessar facilmente.

---

### 🔵 FASE 5 — Integração Shopee Nativa

#### 5.1 API Shopee Open Platform
**O que**: Conectar via API REST da Shopee (open.shopee.com) para:
- Importar vendas automaticamente (substituir upload CSV manual)
- Sincronizar estoque (Product.stock → Shopee)
- Obter métricas de anúncio reais
**Depende**: Credenciais de desenvolvedor Shopee (OAuth 2.0 com refresh token).
**Tempo estimado**: 2-4 dias de desenvolvimento.
**Valor**: Automatiza o processo mais manual do sistema hoje.

---

## 📊 Estimativa de Esforço

| Fase | Frente | Esforço | Impacto | Dependências |
|------|--------|---------|---------|-------------|
| 1.1 | Playwright install | 15min | 🟢 Alto | Nenhuma |
| 1.2 | Migração google.genai | 2h | 🟢 Alto | Nenhuma |
| 1.3 | Teste de fumaça | 30min | 🟡 Médio | 1.1, 1.2 |
| 2.1 | Infra de testes | 4h | 🟡 Médio | Nenhuma |
| 2.2 | Refactor dashboard | 8h | 🟢 Alto | 2.1 (segurança) |
| 2.3 | Gotchas | 1h | 🟡 Médio | Nenhuma |
| 3.1 | Bundle UI | 6h | 🟢 Alto | Nenhuma |
| 3.2 | Alertas reposição | 4h | 🟡 Médio | 3.1 (parcial) |
| 4.1 | Prompts imagem | 2h | 🟢 Baixo | LLM configurado |
| 4.2 | Cohort/LTV | 6h | 🔵 Baixo | Modelagem customer |
| 4.3 | Tab concorrência | 1h | 🟡 Médio | Nenhuma |
| 5.1 | API Shopee | 16h+ | 🟢 Alto | Chaves Shopee dev |

---

## 🚀 Recomendação de Ordem de Execução

```
Semana 1:  1.1 → 1.2 → 1.3 → 2.3   (estabilização + gotchas)
Semana 2:  2.1 → 2.2                (qualidade + manutenibilidade)
Semana 3:  3.1 → 3.2                (features alta prioridade)
Semana 4:  4.1 → 4.3 → 4.2          (features média prioridade)
Futuro:    5.1                        (integração Shopee nativa)
```

---

## 🛑 Riscos Identificados

1. **Python 3.11 + pandas 3.0**: pandas 3.0 tem breaking changes. Testar funções de data que usam `date` em transações.
2. **Plotly 6.8**: API pode ter mudado. Verificar gráficos existentes no dashboard.
3. **Streamlit 1.58**: Muito recente. Verificar se components compatíveis com versões mais estáveis (1.30-1.36).
4. **Sem backup do DB**: `database.db` tem dados reais de 281 transações. Fazer backup antes de qualquer migração.
5. **google.generativeai → google.genai**: API diferente. Precisa de teste com chamada real.
6. **`transaction` é palavra reservada SQL**: Tabela precisa ser sempre referenciada com aspas `"transaction"`.
7. **Produtos duplicados**: Os 39 produtos têm títulos muito similares com variações de quantidade (- 1x, - 2x, - 3x). Verificar se o fuzzy match (threshold 55%) consegue distinguir corretamente.

---

## 📌 Próximo Passo Imediato

**Qual frente você quer atacar primeiro?**

1. 🔴 **Playwright install** — desbloquear scrapers
2. 🔴 **Migração google.genai** — resolver deprecation warning
3. 🟡 **Refactor do dashboard** — quebrar o monólito
4. 🟡 **Bundle UI** — interface de composição de kits
5. 🔵 **Outro** — você escolhe

> _Este plano é vivo. Atualize conforme avançamos._
