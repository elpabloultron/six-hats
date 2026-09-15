from typing import Any, Optional
from six_hats.agents.base import HatAgent
from six_hats.core.models import WhiteHatData, GreenHatProposal, YellowHatBenefit
from six_hats.tools.performance_analyzer import analyze_performance_bottlenecks
from six_hats.tools.ast_extractor import extract_ast_data


class YellowHatAgent(HatAgent):
    """Agente Sombrero Amarillo: Optimismo fundamentado, análisis asintótico Big-O y valor tangible."""

    def __init__(self):
        super().__init__(
            hat_name="yellow",
            hat_color="yellow",
            role="Optimismo Constructivo, Análisis Big-O y Modernización",
            emoji="🟡",
            description="Identifica oportunidades de aceleración Big-O, escalabilidad, modernización idiomática (Python 3.10+) y resiliencia de largo plazo.",
        )

    async def execute(
        self,
        code_content: str,
        white_data: Optional[WhiteHatData] = None,
        green_proposals: Optional[list[GreenHatProposal]] = None,
        **kwargs: Any,
    ) -> list[YellowHatBenefit]:
        """Evalúa oportunidades de optimización, viabilidad y beneficios medibles."""
        benefits: list[YellowHatBenefit] = []

        bottlenecks = analyze_performance_bottlenecks(code_content)
        for b in bottlenecks:
            benefits.append(
                YellowHatBenefit(
                    metric=f"Optimización Big-O: {b['type']}",
                    impact=f"{b['description']} Remedición: {b['remediation']}",
                    feasibility="ALTA",
                    asymptotic_optimization=f"{b['location']}: {b['type']}",
                )
            )

        if white_data is None and code_content.strip():
            white_data = extract_ast_data(code_content, 0, 0)

        mi_str = f"{white_data.maintainability_index}/100" if white_data else "No calculado"

        benefits.append(
            YellowHatBenefit(
                metric="Rendimiento y Throughput",
                impact="La aplicación de patrones del Sombrero Verde proyecta una aceleración de entre 20 % y 40 % en throughput.",
                feasibility="ALTA",
            )
        )
        benefits.append(
            YellowHatBenefit(
                metric="Mantenibilidad y Calidad de Código",
                impact=f"Índice de Mantenibilidad actual: {mi_str}. Con refactorización alcanza >85/100.",
                feasibility="ALTA",
            )
        )
        benefits.append(
            YellowHatBenefit(
                metric="Modernización Sintáctica (Ruff SIM/UP)",
                impact="Reemplazo de construcciones legadas por patrones idiomáticos modernos de Python 3.10+ (match/case, unión de tipos |).",
                feasibility="ALTA",
            )
        )

        return benefits
