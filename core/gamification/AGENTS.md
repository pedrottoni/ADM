# 🎮 Gamification — Engine de Progressão

## Visão Geral
Sistema de gamificação: XP, níveis e missões para engajar o uso do dashboard.

## Arquivos

| Arquivo | Propósito |
|---------|-----------|
| `engine.py` | `GamificationEngine`: `calculate_level(xp)`, `xp_for_next_level(current_level)`, `add_xp(user, amount, session)` (faz level up automático). **NÃO tem `complete_mission()` nem `check_level_up()` expostos** — esses nomes na doc antiga estavam errados. |

## Regras de Level (FÓRMULA REAL — doc antigo estava errado)

⚠️ **Cuidado:** a fórmula é **quadrática**, não linear. Doc antigo dizia `user.level * 100` — errado.

```python
# Em core/gamification/engine.py — o que está VIVO no código:

@staticmethod
def calculate_level(xp: int) -> int:
    # Level = floor(sqrt(XP / 100)) + 1
    return math.floor(math.sqrt(xp / 100)) + 1

@staticmethod
def xp_for_next_level(current_level: int) -> int:
    # XP necessário pro próximo nível: current_level^2 * 100
    return (current_level ** 2) * 100
```

Tabela de referência:

| XP acumulado | Level |
|------|------|
| 0 | 1 |
| 100 | 2 |
| 400 | 3 |
| 900 | 4 |
| 1600 | 5 |
| n² × 100 | n+1 |

XP necesario para subir do `level N` para `N+1`: `(N² × 100) + ((N+1)² × 100) - (N² × 100)` simplificando: `(N+1)² × 100 - N² × 100 = (2N+1) × 100`.

## Como Usar
```python
from core.gamification.engine import GamificationEngine

# API existente:
#   GamificationEngine.calculate_level(xp)  -> int
#   GamificationEngine.xp_for_next_level(current_level) -> int
#   GamificationEngine.add_xp(user, amount, session) -> User  (faz level up automático se aplicável)
# ⚠️ NÃO há método complete_mission() — vem direto via SQLModel (Mission.is_completed=True + add_xp)

level = GamificationEngine.calculate_level(user.xp)
next_xp = GamificationEngine.xp_for_next_level(level)
GamificationEngine.add_xp(user, 50, session)   # +50 XP, checa level up automático
```

## Dependências
- `core/database/models.py` — User, Mission
- chamado por `agents/` e pelo dashboard
