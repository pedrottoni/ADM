# 🛒 Shopee Growth Quest (ADM)

> Sistema de gestão completo para lojas Shopee, com IA integrada, controle financeiro inteligente e gestão de inventário físico.

---

## 📋 Visão Geral do Projeto

O **Shopee Growth Quest** (também conhecido como **ADM** - Administrador) é um sistema de gestão para e-commerce que opera principalmente com a plataforma Shopee. O projeto foi desenvolvido para automatizar e inteligenciar diversas operações de uma loja virtual de suplementos, desde a criação de anúncios até o controle financeiro e atendimento ao cliente.

### Problema que Resolve

- 📊 **Financeiro**: Dificuldade em calcular lucro real (considerando custos de fornecedores)
- 📦 **Inventário**: Descontrole entre estoque físico (potes) e anúncios virtuais (SKUs)
- ✍️ **Criação de Anúncios**: Processo manual e demorado de escrever descrições
- 💬 **Atendimento**: Respostas genéricas que não passam autoridade

### Solução Proposta

- Integração de custos reais (fornecedor) com vendas (Shopee)
- Sistema de "Kits" que vinculam múltiplos itens físicos a um único anúncio
- IA que gera títulos, descrições e keywords otimizadas para conversão
- Agentes especializados para marketing, atendimento e análise financeira

---

## 🏗️ Arquitetura do Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                     DASHBOARD (Streamlit)                    │
│  Tab 1: Resumo  │  Tab 2: Financeiro  │  Tab 3: Marketing  │
│  Tab 4: Atendimento  │  Tab 5: Produtos  │  Tab 6: Config   │
└──────────────────────────┬──────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
┌───────────────┐  ┌───────────────┐  ┌───────────────┐
│ Finance Agent│  │Product Agent  │  │ Customer Agent│
│   (IA)       │  │    (IA)       │  │     (IA)      │
└───────┬───────┘  └───────┬───────┘  └───────┬───────┘
        │                  │                  │
        ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────┐
│                    CORE SERVICES                            │
│  SalesService  │  LLMClient  │  GamificationEngine          │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                    DATABASE (SQLModel/SQLite)                │
│  Users │ Products │ Inventory │ Transactions │ Missions    │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 Estrutura de Pastas

```
ADM/
├── .env                    # Variáveis de ambiente (API Keys)
├── .qwen/                  # Configurações do agente (opencode)
│   └── settings.json
├── agents/                 # Agentes de IA
│   ├── base_agent.py       # Classe base abstrata
│   ├── finance_agent.py    # Agente financeiro
│   ├── product_agent.py    # Agente de produtos/criação
│   ├── ads_agent.py        # Agente de anúncios/marketing
│   └── customer_agent.py   # Agente de atendimento
├── core/                   # Núcleo do sistema
│   ├── config.py           # Configurações e API Keys
│   ├── llm_client.py       # Cliente unificado de IA (Gemini/OpenRouter/NVIDIA)
│   ├── sales_service.py    # Service de vendas e matching
│   ├── gamification/
│   │   └── engine.py       # Sistema de XP e missões
│   └── database/
│       ├── engine.py       # Conexão SQLite
│       ├── models.py       # Modelos SQLModel
│       └── migrations/    # Scripts de migração
├── dashboard/              # Interface Streamlit
│   ├── main.py           # App principal com todas as tabs
│   └── components/
│       └── settings_view.py  # Página de configurações
├── docs/                  # Documentação
│   └── status_projeto.md  # Estado atual do projeto
└── scratch/               # Área de testes (gitignored)
```

---

## 🛠️ Stack Tecnológico

| Componente | Tecnologia | Versão |
|------------|-----------|--------|
| **Linguagem** | Python | 3.13+ |
| **Web Framework** | Streamlit | Latest |
| **ORM** | SQLModel | Latest |
| **Database** | SQLite | 3 |
| **IA - Texto** | Google Gemini 2.5 Flash | - |
| **IA - Texto Alt** | OpenRouter (GPT/Gemini) | - |
| **IA - Visão** | Gemini 2.5 Flash Vision | - |
| **Ambiente** | python-dotenv | Latest |

---

## 💾 Modelos de Dados

### Diagrama de Entidades

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│     User        │       │    Product      │       │  InventoryItem  │
├─────────────────┤       ├─────────────────┤       ├─────────────────┤
│ id              │       │ id              │       │ id              │
│ username        │       │ title           │       │ name            │
│ level           │       │ description     │       │ supplier_price  │
│ xp              │◄──────│ price           │       │ stock           │
│ joined_at       │       │ supplier_price  │       │ min_stock       │
└─────────────────┘       │ stock           │       └────────┬────────┘
                          │ sku             │                │
                          │ shopee_id       │       ┌────────┴────────┐
                          └────────┬────────┘       │                  │
                          ┌───────┴───────┐       │ ProductComponent │
                          │               │       ├──────────────────┤
┌─────────────────┐       │               │       │ product_id       │
│  Transaction    │       │ ProductComponent◄────│ inventory_item_id│
├─────────────────┤       │               │       │ quantity         │
│ id              │       └───────────────┘       └─────────────────┘
│ date            │
│ type (IN/OUT)   │       ┌──────────────────────────────────┐
│ category        │       │       ProductVariation          │
│ amount          │       ├──────────────────────────────────┤
│ product_id ◄────│       │ id              (SKU Shopee)     │
│ quantity        │       │ name            (Ex: "Kit 3x")   │
│ user_id ◄───────┘       │ price, supplier_price, stock    │
└─────────────────┘       │ product_id                       │
                          └──────────────────────────────────┘

┌─────────────────┐
│     Mission     │
├─────────────────┤
│ id              │
│ title           │
│ description     │
│ xp_reward       │
│ is_completed    │
│ user_id ◄───────┘
└─────────────────┘
```

### Descrição dos Modelos

| Modelo | Descrição |
|--------|-----------|
| **User** | Usuário administrador com sistema de gamificação (XP/Level) |
| **Product** | Anúncio virtual na Shopee (SKU Virtual). Preço de venda na plataforma. |
| **InventoryItem** | Pote físico real (ex: "Pote Melatonina 60 caps"). Custo do fornecedor. |
| **ProductComponent** | Tabela de ligação que define quantos itens físicos formam um produto virtual |
| **ProductVariation** | Variações de um produto (ex: "Kit 1x", "Kit 3x", "Sabor Morango") |
| **Transaction** | Cada venda ou despesa. Vinculada a `product_id` para cálculo de lucro em tempo real |
| **Mission** | Missões do sistema de gamificação para engajar o usuário |

---

## 🔑 Principais Funcionalidades

### 1. 💰 Financeiro Inteligente

- **Upload de CSV (Shopee)**: A IA interpreta relatórios de vendas, identifica produtos e sugere importação
- **Gestão de Custos**: Cálculo automático de COGS (Custo por Mercadoria Vendida) baseado nos potes físicos
- **KPIs em Tempo Real**: Faturamento, Margem e Lucro Líquido atualizados dinamicamente
- **Editor de Histórico**: Tabela editável para corrigir ou deletar transações passadas
- **Análise Profunda**: Geração de relatório estratégico via IA com recomendações de ação

### 2. 📦 Gestão de Produtos (IA Factory)

- **Visão Computacional**: Extração de detalhes (nome, peso, benefícios) a partir da foto do rótulo
- **Geração de Copy**: Criação de títulos e descrições otimizados para conversão e SEO
- **Busca Web**: Pesquisa automática na internet por informações complementares
- **Bundle Maker**: Sistema de criação de anúncios que consomem estoque de múltiplos itens físicos

### 3. 📢 Central de Marketing

- **Análise de Campanha**: Calcula ROAS e CTR, fornece sugestões estratégicas via IA
- **Gerador de Prompts de Imagem**: Cria prompts para Midjourney/DALL-E a partir de produtos

### 4. 🤝 Atendimento ao Cliente

- **Gerador de Respostas**: Gera respostas empáticas e personalizadas para clientes
- **Análise de Sentimento**: Analisa avaliações para identificar pontos fortes e reclamações

### 5. 🎮 Sistema de Gamificação

- Sistema de XP e Level
- Missões diárias para engajamento
- Conquistas e badges

---

## 🚀 Como Executar o Projeto

### Pré-requisitos

```bash
# Python 3.13+
python --version
```

### Instalação

```bash
# Clone o repositório
cd ADM

# Crie um ambiente virtual (opcional mas recomendado)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Instale as dependências
pip install streamlit sqlmodel pandas google-generativeai openai python-dotenv
```

### Configuração das API Keys

Edite o arquivo `.env` com suas chaves de API:

```env
# Google Gemini (OBRIGATÓRIO)
GOOGLE_API_KEY=AIzaSy...

# OpenRouter (Alternativo)
OPENROUTER_API_KEY=sk-or-v1-...

# NVIDIA (Alternativo)
NVIDIA_API_KEY=nvapi-...
```

### Executando o Dashboard

```bash
streamlit run dashboard/main.py
```

O aplicativo estará disponível em: `http://localhost:8501`

---

## 📖 Guia de Uso

### Fluxo Principal: Cadastro de Produtos

1. **Adicione itens físicos**: Vá na aba "Meus Anúncios" → "Estoque de Potes (Físico)" → "Novo Item Físico"
2. **Crie o anúncio virtual**: Use a "Fábrica de Produtos" com texto ou imagem (Vision)
3. **Vincule os componentes**: Configure a composição do kit (quantos potes formam o produto)
4. **Defina preço e estoque**: Configure o preço de venda na Shopee

### Fluxo Principal: Registro de Vendas

1. **Upload de CSV**: Na aba "Financeiro" → "Importar Dados", submeta o relatório da Shopee
2. **Review da IA**: A IA mostra as transações identificadas para você revisar
3. **Confirmação**: Ao confirmar, as vendas são registradas E o estoque físico é abatido automaticamente

---

## ⚠️ Observações Importantes

### Diferença entre Product e InventoryItem

- **Product (SKU Virtual)**: O anúncio que aparece na Shopee. Tem preço de venda e estoque virtual.
- **InventoryItem (Pote Físico)**: O produto real que você tem no armazém. Tem custo do fornecedor.

### Como funciona o sistema de Kits

Quando você cria um "Kit 3x Potes de Melatonina":
1. Cria um `Product` chamado "Melatonina - 3x"
2. Cria um `ProductComponent` vinculando 3x do `InventoryItem` "Pote Melatonina 60 caps"
3. Ao vender 1 unidade, o sistema automaticamente abata 3 do estoque físico

### Alertas de Reposição

O sistema já possui lógica para alertar quando o estoque de um `InventoryItem` está abaixo do `min_stock`. Esses alertas aparecem na aba "Resumo".

---

## 📋 Backlog de Funcionalidades

### Alta Prioridade (TODO)
- [ ] **Interface de Composição (Bundle UI)**: Melhorar a forma de definir componentes de um produto manualmente via Dashboard
- [ ] **Alertas de Reposição Avançados**: Implementar lógica que projeta quando o estoque vai acabar baseado no ritmo de vendas
- [ ] **Testar e validar**: Testar as alterações recentes no dashboard (filtro de datas, métricas)

### Futuro / Opcional
- [ ] **Gerador de Prompts de Imagem**: Criar sugestões para ferramentas como Midjourney
- [ ] **Dashboard de Cohort/LTV**: Análises mais avançadas de retenção de clientes
- [ ] **Integração API Shopee (Nativo)**: Substituir o upload manual de CSV pela conexão direta via API

---

## 🛠️ Alterações Recentes (Abril 2026)

### ✅ Concluído
- [x] **Criação do README.md**: Documentação completa do projeto
- [x] **Correção de Bug no Product Agent**: Função `generate_mass_upload_csv` estava retornando DataFrame vazio (faltava `return df_export.to_csv()`)
- [x] **Dashboard - Aba "Meus Anúncios"**:
  - Removido métricas "Receita Real", "Lucro Real", "Margem Total" da aba "Desempenho de Vendas"
  - Renomeado aba "Estoque de Potes (Físicos)" → "Estoque de Potes"
  - Adicionado filtro de período com seletor de calendário (date picker)
  - Período padrão: dia 15 do mês anterior até dia 14 do mês atual (ciclo de pagamento do fornecedor)
  - Métricas adicionadas: Potes Vendidos (Período), COGS (Período), Potes Vendidos (Total), COGS (Total)
  - Adicionada coluna "Potes Vendidos (Mês)" na tabela de inventário
- [x] **Correção de Bug de Tipo**: TypeError `'<=' not supported between 'datetime.date' and 'datetime.datetime'` - conversão de tipos para comparação correta de datas

---

## 🔧 Comandos Úteis

```bash
# Executar o dashboard
streamlit run dashboard/main.py

# Executar em modo debug
streamlit run dashboard/main.py --server.runOnSave false

# Resetar banco de dados (se necessário)
# Vá em: Aba Financeiro → Zona de Perigo → "Zerar Vendas/Histórico"
```

---

## 📊 Histórico do Projeto

Este documento foi consolidado a partir de múltiplas sessões de desenvolvimento:

| Sessão | Tópico Principal |
|--------|-----------------|
| `session_atual` | Dashboard: Filtros de data, métricas de potes, correções de bugs |
| `9ba55366` | Integração Vendas/Estoque |
| `129499f9` | Inventário e Kits (Revolução de Potes) |
| `09c7faeb` | IA Product Factory / Vision |
| `c7075ea0` | Estrutura Financeira e Gastos Manuais |
| `b37ddb49` | Setup Base e Gamification |

---

## 📄 Licença

Este projeto é de uso pessoal/desenvolvimento. As APIs (Google, OpenRouter, NVIDIA) requerem chaves próprias.

---

## 🆘 Troubleshooting

### "GOOGLE_API_KEY not found"
- Verifique se o arquivo `.env` existe na raiz do projeto
- As chaves estão no formato correto (sem aspas extras)

### Stock não abate ao registrar venda
- Verifique se o produto tem componentes vinculados
- O sistema só abate estoque físico se houver `ProductComponent`

### IA não responde
- Verifique a aba "Configurações" → "Teste de Conexão"
- Tente mudar o provider de IA (Gemini/OpenRouter/NVIDIA)

---

*Criado automaticamente em Abril/2026*