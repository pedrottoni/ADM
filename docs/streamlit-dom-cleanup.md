# Streamlit DOM Cleanup — Padrões e Regras

Referência para limpar divs desnecessárias em dashboards Streamlit. Aplicável a qualquer projeto Streamlit.

---

## 1. `st.markdown(unsafe_allow_html=True)` vs `st.html()`

| | `st.markdown` | `st.html()` |
|---|---|---|
| **DOM gerado** | `stElementContainer > stMarkdown > stMarkdownContainer > conteúdo` | `stElementContainer > iframe > conteúdo` |
| **Divs extras** | 3 wrappers | 1 iframe |
| **CSS classes** | Funcionam (mesmo DOM) | Não funcionam (iframe isolado) |
| **Ícones Material** | Funcionam | Precisa `<link>` no iframe |
| **Uso recomendado** | Quando precisa de CSS classes do projeto | Quando usa estilos inline |

**Regra:** Se o conteúdo usa apenas estilos inline, prefira `st.html()`.

### Exemplo de conversão

```python
# ANTES (4 wrappers: stElementContainer > stMarkdown > stMarkdownContainer > div)
st.markdown("""
<div class="chart-card-header">
    <span class="chart-card-title">Titulo</span>
</div>
""", unsafe_allow_html=True)

# DEPOIS (1 iframe, estilos inline)
st.html(
    '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@24,400,0,0">'
    '<div style="display:flex;align-items:center;gap:8px">'
    '<span style="color:#94A3B8;font-size:0.85rem;font-weight:500">Titulo</span>'
    '</div>'
)
```

---

## 2. `st.columns(1)[0]` — Wrapper Inútil

```python
# ANTES — cria stHorizontalBlock > stColumn > stVerticalBlock (3 divs extras)
big_card = st.columns(1)[0]
with big_card:
    conteudo()

# DEPOIS — conteudo direto, estilização via CSS
conteudo()
```

**CSS para aplicar estilo de card sem o wrapper:**
```css
/* Stiliza o stHorizontalBlock que contém o conteúdo */
[data-testid="stHorizontalBlock"]:has(.meu-marker) {
  background: #1E293B;
  border: 1px solid #334155;
  border-radius: 12px;
  padding: 1.5rem;
}
```

---

## 3. Hidden Markers — Padrão CSS `:has()`

Para estilizar containers Streamlit sem classes customizadas, use divs ocultos como âncoras CSS:

```python
# Div oculta como âncora
st.markdown(
    '<div class="meu-marker" style="display:none"></div>',
    unsafe_allow_html=True,
)
```

```css
/* Escopo via :has() — só afeta containers que contêm o marker */
[data-testid="stHorizontalBlock"]:has(.meu-marker) {
  /* estilos */
}
```

### Limitações do `:has()`

- Funciona em Chrome 105+, Firefox 121+, Safari 15.4+
- Funciona entre pai-filho em qualquer profundidade
- **Não funciona** entre irmãos (usar `+` ou `~`)
- Evite markers duplicados — cada marker deve ser único na página
- `:has()` em `stHorizontalBlock` para containers com 2+ colunas pode matchar múltiplos — usar marker específico

---

## 4. Streamlit DOM — O que cada widget cria

| Widget | DOM gerado |
|--------|-----------|
| `st.columns([2,1])` | `stHorizontalBlock > stColumn × N` |
| `st.container()` | `stContainer > stVerticalBlock` |
| `st.markdown(html)` | `stElementContainer > stMarkdown > stMarkdownContainer` |
| `st.html()` | `stElementContainer > iframe` |
| `st.selectbox()` | `stElementContainer > stSelectbox > .st-bz` |
| `st.plotly_chart()` | `stElementContainer > stPlotlyChart` |
| `st.expander()` | `stExpander > details > summary` |
| `st.metric()` | `stElementContainer > div[data-testid="stMetric"]` |
| `st.info/success/warning` | `stElementContainer > div[role="alert"]` |

---

## 5. CSS Scoping — Como Estilizar Sem Poluir

### Padrão 1: Marker + `:has()`
```css
[data-testid="stContainer"]:has(.meu-marker) { /* ... */ }
```

### Padrão 2: Posição do child (evitar quando possível)
```css
div[data-testid="column"]:nth-of-type(2) [data-testid="stContainer"] { /* ... */ }
```

### Padrão 3: data-st-key (para widgets com key)
```python
st.selectbox("...", key="meu_key")
```
```css
[data-st-key="meu_key"] { /* ... */ }
```

### Padrão 4: `data-testid` (mais estável que classes Emotion)
```css
[data-testid="stSelectbox"] [data-baseweb="select"] { /* ... */ }
```

**Dica:** `[data-testid]` é mais estável que classes `.st-XXXX` que mudam entre versões do Streamlit.

---

## 6. Popover/Dropdown — Portal Fora do DOM

O dropdown de `st.selectbox` é renderizado num **portal** separado (`[data-baseweb="popover"]`), fora do componente. CSS normal não alcança.

```css
/* Estiliza itens do dropdown (portal) */
[data-baseweb="popover"] * {
  font-size: 0.8rem !important;
}
```

**IMPORTANTE:** Regras globais como `[data-baseweb="popover"] *` afetam TODOS os dropdowns na página. Use com cuidado ou escopo via marker.

---

## 7. Material Symbols em `st.html()`

`st.html()` renderiza em iframe isolado — CSS do projeto não aplica. Para Material Symbols, inclua o `<link>` dentro do iframe:

```python
st.html(
    '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@24,400,0,0">'
    '<span class="material-symbols-rounded" style="font-size:1rem">trending_up</span>'
)
```

---

## 8. st.selectbox — Fonte e Tamanho

Streamlit usa Base Web (Uber) com a classe `.st-bz`. O dropdown é um portal separado.

```css
/* Trigger (fechado) */
[data-testid="stSelectbox"] [data-baseweb="select"] {
  font-size: 0.8rem !important;
}
[data-testid="stSelectbox"] [data-baseweb="select"] > div {
  height: 2rem !important;
  min-height: 2rem !important;
}
[data-testid="stSelectbox"] [data-baseweb="select"] span {
  font-size: 0.8rem !important;
}

/* Dropdown (aberto) — portal separado no body */
[data-baseweb="popover"] * {
  font-size: 0.8rem !important;
}
```

---

## 9. `st.columns([ratio])` — Ratio para Largura Alvo

```python
# Para largura-alvo X% na segunda coluna:
# ratio = [denominator/target - 1, 1]

# Exemplo: 18% na segunda coluna → 1/0.18 - 1 ≈ 4.5
st.columns([4.5, 1])  # segunda coluna ≈ 18%

# Exemplo: 25% na segunda coluna
st.columns([3, 1])     # segunda coluna = 25%
```

---

## 10. Checklist de Limpeza

Antes de considerar uma seção "limpa", verifique:

- [ ] Há `st.columns(1)[0]`? → Remover, aplicar CSS diretamente
- [ ] Há `st.markdown(unsafe_allow_html=True)` com só estilos inline? → Converter para `st.html()`
- [ ] Há markers ocultos que não são usados por CSS? → Remover
- [ ] Há `st.container()` sem CSS associado? → Remover
- [ ] Há classes CSS definidas mas não usadas no HTML/Python? → Remover do CSS
- [ ] O DOM tem mais de 3 níveis de wrappers desnecessários? → Investigar
- [ ] Headers com `st.markdown` usam só estilos inline? → Converter para `st.html()`
- [ ] Selectbox dropdown com fonte errada? → Verificar regras `[data-baseweb="popover"]`
