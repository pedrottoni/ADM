# ADM Dashdark X — Design System

> Tema ativo no dashboard ADM (Shopee Growth Quest). Inspirado no template Dashdark X — dark navy com acento indigo e sidebar como hub central de navegação.
>
> **Arquivo-fonte:** `dashboard/static/cupertino.css` (~720 linhas). Carregado por `dashboard/app.py` no boot via `st.markdown(<style>...</style>)`.
>
> Se você for alterar tokens ou componentes, edite o CSS. **Não** duplique valores no Python — use sempre `var(--dx-*)`.

---

## 1. Filosofia

**Clean. Data-first. Hub de navegação na sidebar.**

- Sidebar é o ponto de entrada — 7 itens de navegação como radio estilizado
- Cards com bordas sutis (`1px solid var(--dx-card-border)`), sem glassmorphism ou blur pesado
- Paleta dark navy (`#0F172A` base) com contraste limpo entre superfícies
- Acento indigo (`#818CF8`) como única cor primária de ação
- Tipografia compacta (1rem–1.75rem), sem serifadas

---

## 2. Paleta de Cores (tokens CSS `:root`)

### Superfícies

| Token | Hex | Uso |
|-------|-----|-----|
| `--dx-bg-primary` | `#0F172A` | Fundo principal do app |
| `--dx-bg-secondary` | `#1E293B` | Cards, expanders, inputs |
| `--dx-bg-tertiary` | `#334155` | Toggle off, hover ativo |
| `--dx-sidebar-bg` | `#0B0F1D` | Sidebar (mais escuro que a main) |
| `--dx-card-bg` | `#1E293B` | Cards de KPI/chart (atrás de `--dx-bg-secondary`) |
| `--dx-card-border` | `rgba(51, 65, 85, 0.6)` | Borda sutil dos cards |
| `--dx-separator` | `#334155` | Divisores, bordas de input/sidebar |

### Acentos (status & ação)

| Token | Hex | Uso |
|-------|-----|-----|
| `--dx-indigo` | `#818CF8` | **Primary** — botões, links, active nav, focus ring |
| `--dx-indigo-hover` | `#6366F1` | Hover de botão primary |
| `--dx-indigo-glow` | `rgba(129, 140, 248, 0.25)` | Box-shadow em hover/focus |
| `--dx-blue` | `#3B82F6` | Info alerts, accent secundário |
| `--dx-green` | `#22C55E` | Success, delta positivo |
| `--dx-orange` | `#F59E0B` | Warning alerts |
| `--dx-red` | `#EF4444` | Error, delta negativo |

### Texto

| Token | Hex | Uso |
|-------|-----|-----|
| `--dx-text-primary` | `#F8FAFC` | Títulos, valores de métrica |
| `--dx-text-secondary` | `#94A3B8` | Body text, labels de nav |
| `--dx-text-tertiary` | `#64748B` | Captions, subtitles, sidebar hints |

### Raio & nav

| Token | Valor | Uso |
|-------|-------|-----|
| `--dx-radius-s` | `8px` | Botões, inputs, alerts, badges |
| `--dx-radius-m` | `12px` | Cards, expanders, dataframes |
| `--dx-nav-active-bg` | `#1E293B` | Background do item de nav ativo |
| `--dx-nav-hover-bg` | `rgba(148, 163, 184, 0.08)` | Background do item de nav em hover |
| `--dx-nav-active-border` | `3px solid var(--dx-indigo)` | Borda esquerda do item de nav ativo |

---

## 3. Tipografia

| Nível | Peso | Tamanho | Tracking |
|-------|------|---------|----------|
| `h1` | 700 | `1.75rem` | `-0.02em` |
| `h2` | 700 | `1.5rem` | `-0.02em` |
| `h3`–`h6` | 700 | inherits | `-0.02em` |
| Valor de métrica | 700 | `1.75rem` | `-0.02em` |
| Body | 400 | inherits | normal |
| Caption / `.stCaption` | normal | `0.8rem` | normal |
| `.page-subtitle` | normal | `0.9rem` | normal |

**Font stack** (do `.streamlit/config.toml`): `"Segoe UI Variable", "Segoe UI", -apple-system, BlinkMacSystemFont, sans-serif`.

---

## 4. Cantos (Border Radius)

| Token | Valor | Uso |
|-------|-------|-----|
| `--dx-radius-s` | `8px` | Botões, inputs, alerts, badges (pill) |
| `--dx-radius-m` | `12px` | Cards de métrica, expanders, dataframes, chart-card |

---

## 5. Sidebar — Hub de Navegação

A sidebar é o coração do design system. Tem fundo `--dx-sidebar-bg`, borda direita 1px em `--dx-separator`, largura `260–300px`.

### Estrutura interna (de cima pra baixo)

1. **Brand block** — `.sidebar-brand` (emoji + nome "ADM") + `.sidebar-subtitle` ("Shopee Growth Quest")
2. **User profile** — `.user-profile` com avatar gradient indigo→blue, `.user-name`, `.user-level`
3. **XP bar** — `st.progress()` estilizada (altura 4px, pill, indigo fill)
4. **Achievements** — `.achievement-badge` (pill com fundo indigo-12% e texto indigo)
5. **Section header** — `### Navegação` (uppercase, 0.7rem, text-tertiary)
6. **Nav radio** — `st.radio("nav", label_visibility="collapsed")` estilizado como lista de nav-items
7. **LLM toggle** — `st.toggle("🤖 IA Ativa", ...)`
8. **Footer** — `.sidebar-footer` + `.sidebar-cta` (badge "ADM v1.0")

### Estilo do nav radio (3 estados)

| Estado | Background | Texto | Borda esquerda |
|--------|-----------|-------|---------------|
| Inativo | transparent | `--dx-text-secondary`, weight 400 | 3px transparent |
| Hover | `--dx-nav-hover-bg` | `--dx-text-primary` | 3px transparent |
| **Ativo** | `--dx-nav-active-bg` | `--dx-text-primary`, weight 500 | **3px solid `--dx-indigo`** |

O círculo nativo do `st.radio` é escondido com `label[data-baseweb="radio"] > div:first-child { display: none }`. O texto fica no `span` interno.

### Seletores críticos (sidebar)

```css
section[data-testid="stSidebar"]                  /* container raiz */
section[data-testid="stSidebar"] > div            /* padding interno: 1.25rem 1rem */
label[data-baseweb="radio"]                       /* cada item de nav */
label[data-baseweb="radio"]:has(input:checked)    /* item ativo */
section[data-testid="stSidebar"] hr               /* divider na sidebar */
section[data-testid="stSidebar"] .stProgress      /* XP bar */
section[data-testid="stSidebar"] label[data-baseweb="toggle"] /* IA Ativa toggle */
```

---

## 6. Containers & Layout

### Colunas

- `gap: 1rem` entre colunas (`div[data-testid="column"]`)
- Em layouts de **2 colunas** (`2/3 + 1/3` ou `1/2 + 1/2`), use `gap="medium"` no `st.columns(...)` pra dar respiro

### Containers (chart-card, sub-block)

**CRÍTICO: NÃO use `<div>` open/close entre `st.markdown` / `st.plotly_chart`** — quebra ancoragem do DOM. Use o **pattern de marker CSS**:

```python
with st.container():
    st.markdown('<div class="chart-card-marker" style="display:none"></div>', unsafe_allow_html=True)
    st.markdown('<div class="chart-card-header">...</div>', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True)
```

```css
/* Seletor: container INTERNO (stVerticalBlock aninhado), não a coluna inteira */
.stVerticalBlock > .stElementContainer > .stVerticalBlock:has(.chart-card-marker) {
    background: var(--dx-card-bg);
    border: 1px solid var(--dx-separator);
    border-radius: var(--dx-radius-m);
    padding: 1.5rem;
}
```

**Marker classes disponíveis** (uma por contexto):

| Marker | Uso | Cor de fill |
|--------|-----|-------------|
| `.chart-card-marker` | Card genérico de chart | `--dx-card-bg` |
| `.sub-block` | Bloco alinhado em row de sub-blocos | `--dx-card-bg` |
| `.evolution-card-marker` | Card principal de evolução (full-width left) | `--dx-card-bg` |
| `.scrollable-chart-marker` | Marker para chart com scroll-x + full-bleed | transparent |

Para charts em **cards múltiplos**, **cada `st.container()` precisa de seu próprio marker** — eles não compartilham estilo via classe herdada.

### Separadores entre sub-blocos (linha 1px)

São renderizados via `::before` / `::after` posicionados absolutamente (não use `st.markdown("<hr>...")`):

| Onde | Como |
|------|------|
| Vertical entre colunas (ev ↔ dir) | `div[data-testid="column"]:nth-of-type(2)::before` (left: -0.5rem, 1px wide) |
| Horizontal entre sub-blocos empilhados | `div[data-testid="column"]:nth-of-type(2) [data-testid="stContainer"]:nth-of-type(1)::after` (bottom: -0.5rem) |

---

## 7. Componentes

### Metric Cards (KPIs)

**Streamlit 1.56 renderiza `st.metric()` via React + Emotion CSS-in-JS — sem `data-testid`.**

**Solução atual:** componente custom em `dashboard/components/metric_card.py` que usa `st.html()` (não-iframe, bypassa Emotion). O componente recebe `label`, `value`, `delta`, e **detecta** automaticamente `:material/` icon no delta pra setar seta ▲/▼ e cor.

**Hover** é global no CSS (não-inline):
```css
.metric-card:hover {
    border-color: var(--dx-indigo) !important;
    box-shadow: 0 0 0 1px var(--dx-indigo-glow), 0 2px 8px rgba(0, 0, 0, 0.3) !important;
}
```

**Regra dura pro delta** (Pedro, business profile): **só gráfico, nunca texto**.
- Permitido: `▲/▼`, `:material/` icon, números, `%`
- Removido: `"Margem"`, `"Saudável"`, `"Atenção"`, `"Crítico"`, `"Excelente"`, `"Prejuízo"`

Exemplos válidos:
```python
metric_card("Margem", "23.4%", delta=":material/check_circle: 25.0%")      # verde ▲
metric_card("ROI", "1.8x", delta=":material/cancel: -5.0%")           # vermelho ▼
metric_card("Vendas", "R$ 10.4K", delta="▲ 12.3%")    # verde ▲ semântica
```

### Chart Cards

Container com `background: #1E293B`, `border: 1px solid #334155`, `border-radius: 12px`, `padding: 1.5rem`.

**Header** (`flex-wrap: wrap`, gap 0.75rem):
```html
<div class="chart-card-header">
  <div class="chart-card-header-left">
    <span class="chart-card-title">📈 Evolução Financeira</span>
    <div class="chart-card-value-row">
      <span class="chart-card-value">R$ 10.502,63</span>
      <span class="chart-card-delta">▲ 23.4%</span>
    </div>
  </div>
</div>
```

**Legend** (HTML custom, não Plotly legend):
```html
<div class="chart-card-legend">
  <span class="chart-card-legend-item">
    <span class="chart-card-legend-dot" style="background:#818CF8"></span> Receitas
  </span>
</div>
```

Classes: `.chart-card-title` (#94A3B8 / 0.85rem / 500), `.chart-card-value` (#F8FAFC / 1.75rem / 700), `.chart-card-delta` (pill green, border-radius 100px, #166534 bg + #86efac texto).

### Botões

```css
.stButton > button {
    border-radius: var(--dx-radius-s);
    font-weight: 500;
    padding: 8px 20px;
}
```

| Variant | Seletor | Background hover |
|---------|---------|------------------|
| Primary | `button[kind="primary"]` | `--dx-indigo-hover` + glow + `translateY(-1px)` |
| Secondary | `button[kind="secondary"]` | `--dx-nav-hover-bg`, border → `--dx-text-tertiary` |
| Default (sem kind) | `.stButton > button:has(div:has(p:first-child)):not([kind="secondary"])` | indigo |

### Inputs / Textareas / Select

- Background: `--dx-bg-secondary`
- Border: 1px `--dx-separator`
- Border-radius: `--dx-radius-s`
- Focus: border → `--dx-indigo` + glow `--dx-indigo-glow` 3px
- Placeholder: `--dx-text-tertiary`

### Toggle (estilo iOS)

- Off: `--dx-bg-tertiary`
- On: `--dx-indigo`
- Thumb: branco com `box-shadow: 0 1px 3px rgba(0,0,0,0.3)`

### Expanders

- Background: `--dx-bg-secondary`
- Border: 1px `--dx-separator`, radius `--dx-radius-m`
- Padding interno: 12px 16px

### Alerts (Info/Success/Warning/Error)

Padrão: **borda esquerda 3px colorida** + fundo 10% da cor:

| Tipo | Borda esquerda | Fundo bg |
|------|---------------|----------|
| `st.info` | `--dx-blue` | `rgba(59, 130, 246, 0.1)` |
| `st.success` | `--dx-green` | `rgba(34, 197, 94, 0.1)` |
| `st.warning` | `--dx-orange` | `rgba(245, 158, 11, 0.1)` |
| `st.error` | `--dx-red` | `rgba(239, 68, 68, 0.1)` |

Border-radius `--dx-radius-s`, padding `12px 16px`, font-size `0.9rem`.

### DataFrames

- Container: `--dx-radius-m`, 1px separator border, `overflow: hidden`
- Header: `--dx-bg-secondary` bg, `--dx-text-secondary` text, weight 600, separator bottom
- Body: `--dx-bg-primary` bg, `--dx-text-primary` text
- Row hover: `--dx-bg-secondary`

### Progress Bar

- Altura: `6px` (sidebar usa `4px`)
- Border-radius: `100px` (pill)
- Background: `rgba(148, 163, 184, 0.15)`, fill: `--dx-indigo`
- Transição: `width 0.4s cubic-bezier(0.32, 0.72, 0, 1)`

### Dividers (`<hr>`)

- 1px height, background `--dx-separator`, margin `1.5rem 0`

### Code blocks (`<code>`)

- Background `--dx-bg-secondary`, cor `--dx-indigo`, padding `2px 6px`, radius `4px`

---

## 8. Animações & Transições

| Onde | Efeito |
|------|--------|
| Nav radio (hover/active) | `all 0.15s ease` |
| Botões (hover/active) | `all 0.15s ease` |
| Inputs (focus border) | `border-color 0.15s ease` |
| Toggle | `background 0.2s ease` |
| Progress bar | `width 0.4s cubic-bezier(0.32, 0.72, 0, 1)` |
| Sidebar CTA link | `all 0.15s ease` |

**Não há spring/iOS-bouncy** no design atual — o Dashdark X é mais sóbrio/funcional que o Cupertino.

---

## 9. Regras de Layout

| Onde | Regra |
|------|-------|
| Página | `layout="wide"` (em `st.set_page_config`) |
| Sidebar | `initial_sidebar_state="expanded"`, sempre visível |
| Sidebar width | `260–300px` (forçado via `min-width`/`max-width`) |
| Página principal | Padding interno via CSS, conteúdo justificado pelo `st.columns` |
| KPI row | 4 métricas no topo de cada tab |
| Dashboard layout | Padrão `2/3 + 1/3` (`st.columns([2, 1], gap="medium")`) |
| Chart cards | Altura mínima `480px` quando dentro de `.scrollable-chart-marker` |

---

## 10. Anti-padrões (Don'ts)

- **No:** Não duplique valores de cor — sempre `var(--dx-*)`, nunca hex inline
- **No:** Não use `st.metric()` — vai renderizar com Emotion cache e quebrar a estilização
- **No:** Não use `st.html(fig.to_html())` para Plotly — `st.html()` não executa `<script>`, chart fica em branco
- **No:** Não use `<div>` open + `st.plotly_chart()` + `</div>` em mais de um `st.markdown` — quebra ancoragem do DOM
- **No:** Não invente marker classes sem atualizar o CSS correspondente — markers órfãos não fazem nada
- **No:** Não use `data-testid` em metric — não existe no Streamlit 1.56
- **No:** Não misture accent colors em uma mesma área — só `--dx-indigo` como primária
- **No:** Não coloque texto no `delta` da metric_card — só :material/ icon + seta + número + %
- **No:** Não use `:has()` fora dos contextos documentados — funciona, mas vira débito técnico

---

## 11. Implementação

| Arquivo | Conteúdo |
|---------|----------|
| `.streamlit/config.toml` | Base theme Streamlit (paletteDark + font) |
| `dashboard/static/cupertino.css` | **~720 linhas CSS** — todos os tokens `:root` + componentes. **Source of truth visual.** |
| `dashboard/app.py` | Lê CSS via `Path(__file__).resolve().parent / "static" / "cupertino.css"` e injeta com `st.markdown(f"<style>{...}</style>")` |
| `dashboard/components/metric_card.py` | Componente `st.html()` para KPI cards |
| `dashboard/components/chart_card_header.py` | (se existir) Helper Python pra renderizar header |

### Padrão de carregamento

```python
# In dashboard/app.py — BEFORE any st.* call other than set_page_config
from pathlib import Path as _Path
_CSS_PATH = _Path(__file__).resolve().parent / "static" / "cupertino.css"
_CSS_CONTENT = _CSS_PATH.read_text(encoding="utf-8")
st.markdown(f"<style>{_CSS_CONTENT}</style>", unsafe_allow_html=True)
```

**Winux note:** sempre use `encoding="utf-8"`. Sem isso, caracteres Unicode (emojis, `►`, etc.) quebram em `cp1252`.

---

## 12. Workflow de Mudança Visual

Quando você for alterar o design system:

1. **Leia este DESIGN.md** para entender qual token/componente está envolvido
2. **Edite `cupertino.css`** — tokens ficam todos no `:root` no topo (linhas ~7–31), componentes ficam nas seções comentadas abaixo
3. **Se criar novo marker class** (ex: `.my-card-marker`), adicione a regra CSS logo abaixo das existentes (`Marker Pattern` section ~linha 352+)
4. **Se criar novo componente reutilizável** (ex: `components/my_card.py`), importe local (dentro da função) — convenção de projeto
5. **Atualize este DESIGN.md** — adicione a seção/componente novo aqui
6. **Commit em pares** — código + doc no mesmo fluxo; nunca commitar sem atualizar este arquivo

> 📌 Regra de ouro: se você teve que fazer uma改革 visual (cores, layout, marker pattern), e este DESIGN.md não menciona — **você esqueceu de documentar**. Volte e documente antes do commit.

---

## 13. Inspiração & Créditos

- **Dashdark X dashboard template** — base para a paleta dark navy / indigo
- **Tons sobre Tailwind palette** (`slate-900`, `slate-800`, `indigo-400`, `indigo-500`) — valores coerentes com Tailwind v3 padrão
