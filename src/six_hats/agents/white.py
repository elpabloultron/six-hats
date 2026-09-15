from typing import Any
from six_hats.agents.base import HatAgent
from six_hats.core.models import WhiteHatData
from six_hats.tools.ast_extractor import extract_ast_data
from six_hats.tools.git_utils import get_file_diff_stats


class WhiteHatAgent(HatAgent):
    """Agente Sombrero Blanco: Objetividad, evidencia cuantitativa y telemetría de código."""

    def __init__(self):
        super().__init__(
            hat_name="white",
            hat_color="white",
            role="Evidencia Objetiva y Telemetría Estática",
            emoji="⚪",
            description="Extrae hechos empíricos puros, AST, complejidad ciclomática de McCabe, cognitiva de SonarSource, dependencias y churn de Git.",
        )

    async def execute(
        self, code_content: str, is_diff: bool = False, filename: str = "source.py", **kwargs: Any
    ) -> WhiteHatData:
        """Extrae telemetría estática, hechos cuantitativos y métricas de complejidad objetivas."""
        lines_added, lines_deleted = (0, 0)
        if is_diff:
            lines_added, lines_deleted = get_file_diff_stats(code_content)
        return extract_ast_data(code_content, lines_added, lines_deleted, filename=filename)
