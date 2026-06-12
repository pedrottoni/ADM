# 🎮 Gamification — Engine de Progressão

## Visão Geral
Sistema de gamificação: XP, níveis e missões para engajar o uso do dashboard.

## Arquivos

| Arquivo | Propósito |
|---------|-----------|
| `engine.py` | `GamificationEngine`: add_xp(), check_level_up(), complete_mission() |

## Modelos
- `User.level`, `User.xp` — progressão do usuário
- `Mission` — tarefas com `xp_reward`, `is_completed`

## Regras de Level
- XP por nível: `user.level * 100`
- Level up quando `xp >= next_level_xp`

## Como Usar
```python
from core.gamification.engine import GamificationEngine
engine = GamificationEngine()
engine.add_xp(session, user, 50)  # +50 XP, checa level up automático
```

## Dependências
- `core/database/models.py` — User, Mission
- chamado por `agents/` e pelo dashboard
