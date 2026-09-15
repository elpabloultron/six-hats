from typing import Any, Optional
from six_hats.agents.base import HatAgent
from six_hats.core.models import WhiteHatData, GreenHatProposal, RedHatAssessment
from six_hats.tools.ponytail_rules import (
    audit_ponytail,
    detect_lexical_confusion,
    calculate_visual_clutter,
)
from six_hats.tools.ast_extractor import extract_ast_data


class RedHatAgent(HatAgent):
    """Agente Sombrero Rojo: Intuición, ergonomía de API, legibilidad nocturna a las 3:00 AM y antipatrones Ponytail."""

    def __init__(self):
        super().__init__(
            hat_name="red",
            hat_color="red",
            role="Experiencia de Desarrollo (DX), Ergonomía 3:00 AM y Filtro Ponytail",
            emoji="🔴",
            description="Mide fatiga mental, confusión léxica (RapidFuzz), saturación visual y veta la sobreingeniería según la Escalera de la Pereza.",
        )

    async def execute(
        self,
        code_content: str,
        white_data: Optional[WhiteHatData] = None,
        green_proposals: Optional[list[GreenHatProposal]] = None,
        **kwargs: Any,
    ) -> RedHatAssessment:
        """Evalúa la fricción psicométrica y la ergonomía subjetiva del código."""
        ponytail_report = audit_ponytail(code_content)
        confusion_warnings = detect_lexical_confusion(code_content)
        clutter_score = calculate_visual_clutter(code_content)

        if white_data is None and code_content.strip():
            white_data = extract_ast_data(code_content, 0, 0)

        cog = white_data.cognitive_complexity if white_data else 0
        if cog > 15:
            score = "Alta (Fatiga Mental Severa)"
            feeling = "Produce rechazo visual inmediato; demasiados saltos conceptuales y anidamientos innecesarios."
            ergo = "Pésima ergonomía a las 3:00 AM. Alto riesgo de introducir bugs al parchar bajo presión."
        elif cog > 7:
            score = "Media (Aceptable)"
            feeling = "Legible pero con fricción evitable. Se beneficiaría de simplificación de nombres y early returns."
            ergo = "Operable, aunque requiere concentración activa para no perder el hilo."
        else:
            score = "Baja (Fluida y Elegante)"
            feeling = "Intuitivo y placentero de leer. El diseño respeta el principio de menor sorpresa."
            ergo = "Excelente ergonomía de API. Depurable con total claridad a las 3:00 AM."

        if ponytail_report.bloat_score > 40.0:
            ponytail_verdict = f"RECHAZO PONYTAIL: Sobreingeniería Crítica ({ponytail_report.bloat_score} %)"
        elif ponytail_report.bloat_score > 20.0:
            ponytail_verdict = f"ADVERTENCIA PONYTAIL: Complejidad Accidental Detectada ({ponytail_report.bloat_score} %)"
        else:
            ponytail_verdict = f"APROBADO PONYTAIL: Código Conciso y Pragmático ({ponytail_report.bloat_score} %)"

        ladder_violations_txt = [
            f"[{v.severity}] Peldaño {v.rung} ({v.name}): {v.lazy_recommendation}"
            for v in ponytail_report.violations[:5]
        ]

        lines_reducible_pct = 0.0
        if ponytail_report.lines_analyzed > 0:
            lines_reducible_pct = round(
                (ponytail_report.estimated_lines_reducible / ponytail_report.lines_analyzed) * 100.0, 1
            )

        return RedHatAssessment(
            cognitive_load_score=score,
            gut_feeling=feeling,
            ergonomics=ergo,
            bloat_score=ponytail_report.bloat_score,
            ladder_violations=ladder_violations_txt,
            lines_reducible_pct=lines_reducible_pct,
            ponytail_verdict=ponytail_verdict,
            lexical_confusion_warnings=confusion_warnings,
            visual_clutter_score=clutter_score,
        )
