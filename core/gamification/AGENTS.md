# Gamification — Progression Engine

## Overview
Gamification system: XP, levels, and missions to drive dashboard engagement.

## Files

| File | Purpose |
|------|---------|
| `engine.py` | `GamificationEngine`: `calculate_level(xp)`, `xp_for_next_level(current_level)`, `add_xp(user, amount, session)` (auto level-up). **No `complete_mission()` or `check_level_up()` methods** — those names in old docs were wrong. |

## Level Formula (REAL — old docs had it wrong)

**WARNING:** The formula is **quadratic**, not linear. Old docs said `user.level * 100` — wrong.

```python
# In core/gamification/engine.py — what's LIVE in code:

@staticmethod
def calculate_level(xp: int) -> int:
    # Level = floor(sqrt(XP / 100)) + 1
    return math.floor(math.sqrt(xp / 100)) + 1

@staticmethod
def xp_for_next_level(current_level: int) -> int:
    # XP needed for next level: current_level^2 * 100
    return (current_level ** 2) * 100
```

Reference table:

| XP accumulated | Level |
|---------------|-------|
| 0 | 1 |
| 100 | 2 |
| 400 | 3 |
| 900 | 4 |
| 1600 | 5 |
| n² × 100 | n+1 |

XP to level up from `level N` to `N+1`: `(2N+1) × 100`

## How to Use
```python
from core.gamification.engine import GamificationEngine

# API:
#   GamificationEngine.calculate_level(xp)  -> int
#   GamificationEngine.xp_for_next_level(current_level) -> int
#   GamificationEngine.add_xp(user, amount, session) -> User  (auto level-up)
# No complete_mission() — use SQLModel directly (Mission.is_completed=True + add_xp)

level = GamificationEngine.calculate_level(user.xp)
next_xp = GamificationEngine.xp_for_next_level(level)
GamificationEngine.add_xp(user, 50, session)   # +50 XP, auto level-up if applicable
```

## Dependencies
- `core/database/models.py` — User, Mission
- Called by `agents/` and dashboard
