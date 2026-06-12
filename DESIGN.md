# 🍎 Cupertino Dark — Design System

> Tema inspirado no [Cupertino Obsidian Theme](https://community.obsidian.md/themes/cupertino) por Alexis C (sevenaxis) — Best Theme of Obsidian Gems of the Year 2024.
> Adaptado para Streamlit dashboard do ADM (Shopee Growth Quest).

---

## 1. Filosofia

**Fresh. Familiar. Focused.** — Clean typography, refined spacing, iOS-native-inspired components. O tema deve ser **completo no momento da instalação**, sem necessidade de ajustes. Prioriza fluxo e sensação nativa sobre customização.

- "Great tools should just work. No rabbit holes. No endless tweaking."
- "Every option is an invitation to procrastinate."
- **Menos customização, menos ruído visual.**

---

## 2. Paleta de Cores

### Cores de Superfície (iOS Dark Mode)

| Token | Hex | Uso |
|-------|-----|-----|
| `--bg-primary` | `#1C1C1E` | Fundo principal da app |
| `--bg-secondary` | `#2C2C2E` | Sidebar, containers, expanders |
| `--bg-tertiary` | `#3A3A3C` | Inputs, selects, tabelas header, tab bar bg |
| `--glass-bg` | `rgba(44,44,46,0.75)` | Cards métrica com blur |
| `--glass-border` | `rgba(255,255,255,0.08)` | Borda sutil dos cards glass |
| `--separator` | `rgba(84,84,86,0.65)` | Linhas divisórias, bordas finas |
| `--fill` | `rgba(120,120,128,0.2)` | Progress bar bg, toggle off |

### Cores de Texto

| Token | Hex | Uso |
|-------|-----|-----|
| `--text-primary` | `#FFFFFF` | Títulos, valores de métricas |
| `--text-secondary` | `#EBEBF5` | Parágrafos, labels |
| `--text-tertiary` | `#8E8E93` | Captions, métricas label, placeholders |
| `--text-quaternary` | `#636366` | Desabilitado / metadados |

### Cores de Acento (iOS System Colors)

| Token | Hex | Uso |
|-------|-----|-----|
| `--blue` | `#007AFF` | Primary buttons, tabs ativo, links, progress |
| `--green` | `#34C759` | Sucesso, toggle ativo, delta positivo |
| `--orange` | `#FF9500` | Warning, alertas |
| `--red` | `#FF3B30` | Erro, delta negativo, perigo |
| `--purple` | `#AF52DE` | Acento secundário |

---

## 3. Tipografia

| Nível | Peso | Tamanho | Tracking |
|-------|------|---------|----------|
| Título h1 | 800 | `2rem` | `-0.03em` |
| Título h2–h6 | 700 | — | `-0.02em` |
| Valor de métrica | 700 | `1.75rem` | `-0.02em` |
| Corpo | 400 | `0.9rem` | normal |
| Label / Caption | 500 | `0.8rem` | normal |
| Badge (sidebar) | 600 | `0.75rem` | `+0.05em` uppercase |

**Font stack:** `"Segoe UI Variable", "Segoe UI", -apple-system, BlinkMacSystemFont, sans-serif` — usa a fonte nativa de cada plataforma (SF Pro no macOS/iOS).

---

## 4. Cantos (Border Radius)

| Token | Valor | Uso |
|-------|-------|-----|
| `--radius-s` | `8px` | Botões, inputs, selects, alertas, tabs |
| `--radius-m` | `12px` | Cards de métrica, expanders, sidebar métrica |
| `--radius-l` | `20px` | (reservado para modais futuros) |

---

## 5. Glassmorphism

Efeito de vidro fosco aplicado em cards de métrica e sidebar:

```
background: rgba(44, 44, 46, 0.75);
backdrop-filter: blur(20px);
-webkit-backdrop-filter: blur(20px);
border: 0.5px solid rgba(255, 255, 255, 0.08);
```

---

## 6. Componentes

### Tabs (iOS Segmented Control)
- Background: `#3A3A3C` com `border-radius: 8px` e `padding: 3px`
- Tab inativa: transparente, texto `#EBEBF5`
- Tab ativa: `#007AFF` sólido, texto branco, `box-shadow`
- Transição: `0.2s cubic-bezier(0.32, 0.72, 0, 1)`

### Botões (iOS Style)
- **Primary:** fundo `#007AFF`, texto branco, `border-radius: 8px`, shadow sutil
  - Hover: `#0056CC` com glow azul, sobe 1px
  - Active: volta ao lugar, `#004999`
- **Secondary:** fundo `#3A3A3C`, texto `#007AFF`, borda 0.5px separator

### Cards de Métrica
- Vidro fosco (glassmorphism)
- Label: `#8E8E93`, 0.8rem, 500 weight
- Valor: branco, 1.75rem, 700 weight
- Hover: bg mais claro, borda mais visível

### Toggle (iOS Switch)
- Off: `#3A3A3C` (fill)
- On: `#34C759` (green)
- Thumb: branco com shadow

### Inputs / Textareas
- Fundo: `#3A3A3C`, borda 0.5px separator
- Focus: borda `#007AFF` + ring azul 3px com 20% opacidade
- Placeholder: `#8E8E93`

### Alertas
- **Info:** borda esquerda azul (#007AFF), fundo rgba azul 12%
- **Success:** borda esquerda verde (#34C759), fundo rgba verde 12%
- **Warning:** borda esquerda laranja (#FF9500), fundo rgba laranja 12%
- **Error:** borda esquerda vermelha (#FF3B30), fundo rgba vermelho 12%

### Progress Bar
- Altura: 4px
- Border-radius: 100px (pill)
- Fundo: fill, Preenchimento: `#007AFF`
- Transição: `0.4s cubic-bezier(0.32, 0.72, 0, 1)`

### DataFrames / Tabelas
- Border-radius: 12px, borda 0.5px separator
- Header: `#3A3A3C`, texto `#EBEBF5`, peso 600
- Body: `#2C2C2E`, texto branco
- Hover row: `#3A3A3C`

---

## 7. Sombras

```css
/* Botões */
box-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);

/* Botão primary hover */
box-shadow: 0 2px 8px rgba(0, 122, 255, 0.4);

/* Toggle thumb */
box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
```

---

## 8. Regras de Layout

- **Sidebar:** largura padrão Streamlit, `border-right: 0.5px solid separator`
- **Métricas:** 4 colunas no topo (KPI row), padding interno 16px 20px
- **Divisores:** 0.5px, cor separator, margem 1.5rem vertical
- **Expansores:** container arredondado 12px, padding 16px

---

## 9. Animações

```css
transition: all 0.2s cubic-bezier(0.32, 0.72, 0, 1);
```

Curva customizada `(0.32, 0.72, 0, 1)` — aceleração rápida, desaceleração natural (iOS-style spring).

Aplicada em: tabs, botões, cards de métrica, inputs focus, progress bar.

---

## 10. Anti-padrões (Don'ts)

- ❌ **Não use cores aleatórias** — toda cor deve vir da paleta acima
- ❌ **Não misture estilos de card** — glassmorphism é o único padrão
- ❌ **Não remova o backdrop-filter** sem substituto — é a assinatura visual
- ❌ **Não use bordas escuras** (`#000` ou `#111`) — use separator (`rgba(84,84,86,0.65)`)
- ❌ **Não use fontes serifadas ou não-sistema** — a proposta é "native feel"
- ❌ **Não ignore contraste** — texto primário é branco puro, secundário é `#EBEBF5` (passa WCAG AA em bg escuro)

---

## 11. Implementação

| Arquivo | O quê |
|---------|-------|
| `.streamlit/config.toml` | Base theme (dark, primaryColor, bg, font) |
| `dashboard/static/cupertino.css` | Todos os tokens e estilos CSS |
| `dashboard/app.py` | Load do CSS com `open(encoding="utf-8")` |

---

## 12. Inspiração & Créditos

- **Cupertino Obsidian Theme** — [github.com/aaaaalexis/obsidian-cupertino](https://github.com/aaaaalexis/obsidian-cupertino) by Alexis C (sevenaxis)
- **Apple Human Interface Guidelines** — [developer.apple.com/design](https://developer.apple.com/design/human-interface-guidelines)
- **iOS System Colors** — paleta de cores nativa Apple
