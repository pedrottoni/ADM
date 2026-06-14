# Estado Atual do Projeto: ADM (Shopee Growth Quest)

Este documento unifica o conhecimento de todas as sessões de desenvolvimento anteriores, servindo como a "Verdade Única" para o projeto.

---

## Arquitetura e Modelagem

O sistema foi migrado para uma arquitetura baseada em **Componentes de Inventário**, permitindo a gestão de kits e combos de forma precisa.

### Principais Modelos (`core/database/models.py`):
- **`Product`**: Representa o anúncio na Shopee (SKU Virtual). Possui preço de venda e estoque sincronizado com a plataforma.
- **`InventoryItem`**: Representa o pote físico (ex: "Pote Melatonina"). Contém o custo real do fornecedor.
- **`ProductComponent`**: Tabela de ligação que define quantos `InventoryItem` compõem um `Product`.
- **`Transaction`**: Registra cada venda ou despesa. Agora vinculado a `product_id` e `quantity` para cálculo de lucro em tempo real.

---

## Funcionalidades Implementadas

### 1. Financeiro Inteligente
- **Upload de CSV (Shopee)**: IA interpreta os relatórios de vendas, identifica os produtos e sugere a importação.
- **Gestão de Custos**: Cálculo automático de COGS (Custo por Mercadoria Vendida) baseado nos potes físicos.
- **KPIs**: Faturamento, Margem e Lucro Líquido atualizados dinamicamente.
- **Editor de Histórico**: Tabela editável para corrigir ou deletar transações passadas.

### 2. Gestão de Produtos (IA Factory)
- **Visão Computacional**: Extração de detalhes (nome, peso, benefícios) a partir da foto do rótulo.
- **Geração de Copy**: Criação de títulos e descrições otimizados para conversão e SEO, com busca ativa na internet por informações complementares.
- **Bundle Maker**: Sistema de criação de anúncios que consomem estoque de múltiplos itens físicos.

### 3. Agentes de Apoio
- **Ads Master**: Análise de métricas de anúncios (ROAS, CTR) e sugestão de palavras-chave.
- **Customer Hero**: Gerador de respostas empáticas para clientes e analisador de sentimento de avaliações.

---

## Backlog (O que ainda resta fazer)

### Alta Prioridade
- [ ] **Interface de Composição (Bundle UI)**: Melhorar a forma de definir componentes de um produto manualmente via Dashboard (Tab 5).
- [ ] **Alertas de Reposição**: Implementar lógica que avisa quando o estoque de um `InventoryItem` está baixo com base no ritmo de vendas de todos os anúncios vinculados.

### Futuro / Opcional
- [ ] **Gerador de Prompts de Imagem**: Criar sugestões para ferramentas como Midjourney a partir da descrição dos produtos.
- [ ] **Dashboard de Cohort/LTV**: Análises mais avançadas de retenção de clientes.
- [ ] **Integração API Shopee (Nativo)**: Substituir o upload manual de CSV pela conexão direta via API (requer credenciais de desenvolvedor Shopee).

---

## Histórico de Conversas (Consolidação)
As informações deste arquivo foram extraídas e unificadas dos seguintes IDs de conversa no diretório `brain`:
- `9ba55366`: Integração Vendas/Estoque.
- `129499f9`: Inventário e Kits (Revolução de Potes).
- `09c7faeb`: IA Product Factory / Vision.
- `c7075ea0`: Estrutura Financeira e Gastos Manuais.
- `b37ddb49`: Setup Base e Gamification.

---

## Changelog

### 2026-06-14 — Emoji → Material Icons + AGENTS.md overhaul

**Migração de emojis para Material Symbols:**
- Todos os emojis Unicode substituídos por `:material/` icons ou `<span class="material-symbols-rounded">` em contextos HTML
- `metric_card.py`: Adicionada função `_material_to_html()` para converter `:material/xxx:` em HTML real dentro de `st.html()`
- `app.py`: Sidebar (rocket, person, emoji_events) usa Material Symbols via CSS
- `cupertino.css`: Adicionado import do Google Material Symbols Rounded font
- `competitor_service.py`: Marketplace labels e badges migrados
- `llm_client.py`: Warning/error strings migrados
- Console print emojis mantidos (decisão do usuário)
- LLM prompt emojis em `product_agent.py` mantidos (instruções para IA)

**AGENTS.md reescrito em inglês:**
- Root `AGENTS.md` — compacto, high-signal, com technical quirks
- `CLAUDE.md` — atualizado e alinhado
- 12 sub-module AGENTS.md — todos traduzidos para inglês
- Bug do `settings_view.py` documentado
- `MARKETPLACE_LABELS` duplicado documentado

**Arquivos modificados:** 34 arquivos (.py, .md, .css, .bat)
