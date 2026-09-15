import os
from typing import Optional
from six_hats.core.models import (
    WhiteHatData,
    BlackHatFinding,
    YellowHatBenefit,
    GreenHatProposal,
    RedHatAssessment,
    SixHatsConsensus,
)
from six_hats.core.llm_client import GeminiHatClient
from six_hats.agents.white import WhiteHatAgent
from six_hats.agents.green import GreenHatAgent
from six_hats.agents.black import BlackHatAgent
from six_hats.agents.yellow import YellowHatAgent
from six_hats.agents.red import RedHatAgent
from six_hats.agents.blue import BlueHatAgent


class HatRunner:
    """Ejecutor orquestador que coordina los agentes especializados de cada sombrero."""

    def __init__(
        self,
        use_llm_if_available: bool = False,
        white_agent: Optional[WhiteHatAgent] = None,
        green_agent: Optional[GreenHatAgent] = None,
        black_agent: Optional[BlackHatAgent] = None,
        yellow_agent: Optional[YellowHatAgent] = None,
        red_agent: Optional[RedHatAgent] = None,
        blue_agent: Optional[BlueHatAgent] = None,
    ):
        self.api_key = os.environ.get("GEMINI_API_KEY", "")
        self.use_llm = use_llm_if_available and bool(self.api_key)
        self.llm_client = GeminiHatClient(api_key=self.api_key) if self.use_llm else GeminiHatClient(api_key="")

        # Inyección o instanciación de los 6 agentes especializados
        self.white_agent = white_agent or WhiteHatAgent()
        self.green_agent = green_agent or GreenHatAgent(llm_client=self.llm_client if self.use_llm else None)
        self.black_agent = black_agent or BlackHatAgent()
        self.yellow_agent = yellow_agent or YellowHatAgent()
        self.red_agent = red_agent or RedHatAgent()
        self.blue_agent = blue_agent or BlueHatAgent(llm_client=self.llm_client if self.use_llm else None)

    async def execute_white_hat(
        self, code_content: str, is_diff: bool = False, filename: str = "source.py"
    ) -> WhiteHatData:
        """Fase 1: Sombrero Blanco extrae hechos puros, AST, complejidad ciclomática y cognitiva."""
        return await self.white_agent.execute(code_content=code_content, is_diff=is_diff, filename=filename)

    async def execute_green_hat(
        self, white_data: WhiteHatData, code_content: str, task_context: str = ""
    ) -> list[GreenHatProposal]:
        """Fase 2: Sombrero Verde genera propuestas arquitectónicas no convencionales (GenAI o Catálogo)."""
        return await self.green_agent.execute(
            code_content=code_content, white_data=white_data, task_context=task_context
        )

    async def execute_black_hat(
        self, white_data: WhiteHatData, green_proposals: list[GreenHatProposal], code_content: str
    ) -> list[BlackHatFinding]:
        """Fase 3: Sombrero Negro ejecuta escaneo adversarial (Semgrep/Bandit/Gitleaks/OWASP)."""
        return await self.black_agent.execute(
            code_content=code_content, white_data=white_data, green_proposals=green_proposals
        )

    async def execute_yellow_hat(
        self, white_data: WhiteHatData, green_proposals: list[GreenHatProposal], code_content: str
    ) -> list[YellowHatBenefit]:
        """Fase 3: Sombrero Amarillo evalúa valor tangible, análisis asintótico Big-O y modernización."""
        return await self.yellow_agent.execute(
            code_content=code_content, white_data=white_data, green_proposals=green_proposals
        )

    async def execute_red_hat(
        self, white_data: WhiteHatData, green_proposals: list[GreenHatProposal], code_content: str
    ) -> RedHatAssessment:
        """Fase 3: Sombrero Rojo mide DX, ergonomía a las 3:00 AM, confusión léxica y saturación visual."""
        return await self.red_agent.execute(
            code_content=code_content, white_data=white_data, green_proposals=green_proposals
        )

    async def execute_remediation_cycle(
        self,
        white_data: WhiteHatData,
        critical_findings: list[BlackHatFinding],
        red_assessment: RedHatAssessment,
    ) -> list[GreenHatProposal]:
        """Genera propuestas creativas correctivas para el bucle de feedback del Sombrero Azul."""
        return await self.green_agent.execute_remediation(
            white_data=white_data,
            critical_findings=critical_findings,
            red_assessment=red_assessment,
        )

    async def execute_blue_hat(
        self,
        white: WhiteHatData,
        green: list[GreenHatProposal],
        black: list[BlackHatFinding],
        yellow: list[YellowHatBenefit],
        red: RedHatAssessment,
        original_code: str = "",
        filepath: str = "solucion.py",
    ) -> SixHatsConsensus:
        """Fase 4: Sombrero Azul sintetiza, aplica mitigaciones de seguridad, el veto de Ponytail y genera el diff real."""
        return await self.blue_agent.execute(
            white=white,
            green=green,
            black=black,
            yellow=yellow,
            red=red,
            original_code=original_code,
            filepath=filepath,
        )
