# Tab render functions for ADM dashboard
"""Each tab's render(user, agents) function is exported here."""

from .resumo import render as render_resumo
from .financeiro import render as render_financeiro
from .marketing import render as render_marketing
from .atendimento import render as render_atendimento
from .anuncios import render as render_anuncios
from .concorrencia import render as render_concorrencia
from .configuracoes import render as render_configuracoes

TAB_RENDERERS = {
    "resumo": render_resumo,
    "financeiro": render_financeiro,
    "marketing": render_marketing,
    "atendimento": render_atendimento,
    "anuncios": render_anuncios,
    "concorrencia": render_concorrencia,
    "configuracoes": render_configuracoes,
}
