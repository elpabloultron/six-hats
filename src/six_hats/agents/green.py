from typing import Any, Optional
from six_hats.agents.base import HatAgent
from six_hats.core.models import WhiteHatData, GreenHatProposal, BlackHatFinding, RedHatAssessment
from six_hats.core.patterns import get_divergent_proposals, generate_remediation_proposals
from six_hats.core.llm_client import GeminiHatClient


class GreenHatAgent(HatAgent):
    """Agente Sombrero Verde: Pensamiento lateral, innovación arquitectónica e ideación divergente."""

    def __init__(self, llm_client: Optional[GeminiHatClient] = None):
        super().__init__(
            hat_name="green",
            hat_color="green",
            role="Creatividad e Innovación Arquitectónica Divergente",
            emoji="🟢",
            description="Genera soluciones técnicas no convencionales, inversión de supuestos, patrones GoF, monadas Result y arquitecturas desacopladas.",
        )
        self.llm_client = llm_client

    async def execute(
        self,
        code_content: str = "",
        white_data: Optional[WhiteHatData] = None,
        task_context: str = "",
        **kwargs: Any,
    ) -> list[GreenHatProposal]:
        """Genera alternativas arquitectónicas divergentes e innovadoras."""
        if self.llm_client and self.llm_client.is_available:
            ai_proposals = await self.llm_client.generate_green_proposals(code_content, task_context)
            if ai_proposals:
                return ai_proposals

        complexity = white_data.cyclomatic_complexity if white_data else 1
        return get_divergent_proposals(task_context=task_context, code_complexity=complexity)

    async def execute_remediation(
        self,
        white_data: WhiteHatData,
        critical_findings: list[BlackHatFinding],
        red_assessment: RedHatAssessment,
    ) -> list[GreenHatProposal]:
        """Genera propuestas correctivas inmediatas para el bucle de feedback orquestado por el Sombrero Azul."""
        critical_texts = [f"{f.risk_type}: {f.description}" for f in critical_findings]
        bloat_veto = red_assessment.bloat_score > 35.0
        return generate_remediation_proposals(critical_texts, bloat_veto=bloat_veto)
