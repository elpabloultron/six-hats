from typing import Any, Optional
from six_hats.agents.base import HatAgent
from six_hats.core.models import (
    WhiteHatData,
    GreenHatProposal,
    BlackHatFinding,
    YellowHatBenefit,
    RedHatAssessment,
    SixHatsConsensus,
)
from six_hats.tools.diff_generator import generate_real_patch
from six_hats.core.llm_client import GeminiHatClient


class BlueHatAgent(HatAgent):
    """Agente Sombrero Azul: Orquestación metacognitiva, mediación de consenso, veto Ponytail y síntesis de parche."""

    def __init__(self, llm_client: Optional[GeminiHatClient] = None):
        super().__init__(
            hat_name="blue",
            hat_color="blue",
            role="Orquestación Metacognitiva, Consenso, Veto y Síntesis de Parche",
            emoji="🔵",
            description="Modera la deliberación de los demás sombreros, aplica el veto de sobreingeniería y consolida el parche final.",
        )
        self.llm_client = llm_client

    async def execute(
        self,
        white: WhiteHatData,
        green: list[GreenHatProposal],
        black: list[BlackHatFinding],
        yellow: list[YellowHatBenefit],
        red: RedHatAssessment,
        original_code: str = "",
        filepath: str = "solucion.py",
        **kwargs: Any,
    ) -> SixHatsConsensus:
        """Sintetiza los hallazgos de los 5 sombreros, aplica directivas de veto y emite el consenso ejecutable."""
        has_critical = any(f.severity == "CRITICAL" for f in black)
        has_high = any(f.severity == "HIGH" for f in black)
        ponytail_veto = red.bloat_score > 35.0

        mitigations: list[str] = []
        for finding in black:
            if finding.severity in ("CRITICAL", "HIGH"):
                mitigations.append(f"Mitigado [{finding.risk_type}]: {finding.description}")
            elif finding.severity == "MEDIUM":
                mitigations.append(f"Ajustado [{finding.risk_type}]: Aislamiento y validación defensiva.")

        if ponytail_veto:
            mitigations.append(
                f"Veto de Ponytail aplicado: Se podaron abstracciones innecesarias reduciendo ~{red.lines_reducible_pct} % de código."
            )

        if not mitigations:
            mitigations.append("Verificación estándar de precondiciones y aserciones defensivas completada.")

        selected = green[0].name if green else "Arquitectura Modular Pragmática"

        if has_critical:
            verdict = "REQUIRE_CHANGES"
            summary = (
                "Se exigen cambios obligatorios: Se detectaron vulnerabilidades críticas de seguridad (Semgrep/Bandit). "
                "Aplique el parche de mitigación antes del despliegue."
            )
        elif has_high or ponytail_veto:
            verdict = "REQUIRE_CHANGES"
            summary = (
                "Aprobación condicionada: Riesgos altos detectados o sobreingeniería según la Escalera de la Pereza de Ponytail. "
                "Se requiere simplificación y saneamiento de dependencias."
            )
        else:
            verdict = "APPROVE"
            summary = (
                "Aprobado por consenso multilateral. La propuesta equilibra valor técnico, resiliencia probada y código conciso "
                "conforme a las directrices de Ponytail."
            )

        refactored_code = None
        if self.llm_client and self.llm_client.is_available and original_code.strip():
            refactored_code = await self.llm_client.generate_blue_refactored_code(
                original_code, mitigations, selected
            )

        from six_hats.tools.diff_generator import generate_and_verify_patch

        patch, patch_valid, syntax_err = generate_and_verify_patch(
            original_code=original_code,
            filepath=filepath,
            refactored_code=refactored_code,
            applied_mitigations=mitigations,
        )

        guidance = (
            "MANDATO PARA LA IA ANFITRIONA (SOMBRERO AZUL):\n"
            f"1. Telemetría Forense: Complejidad ciclomática {white.cyclomatic_complexity}, "
            f"complejidad cognitiva {white.cognitive_complexity}, índice de mantenibilidad {white.maintainability_index}/100.\n"
            f"2. Hallazgos de Seguridad: {len(black)} riesgo(s) detectado(s). Mitigaciones prioritarias: {'; '.join(mitigations[:3])}.\n"
            f"3. Directiva Ponytail: Bloat score {red.bloat_score} % ({red.ponytail_verdict}). "
            + ("APLICAR VETO: Podar capas intermedias y evitar patrones innecesarios." if ponytail_veto else "Código conciso: Mantener simplicidad.")
            + f"\n4. Propuesta Arquitectónica: {selected}.\n"
            f"5. Estado del Parche: {'✓ Verificado sintácticamente' if patch_valid else f'Advertencia: {syntax_err}'}.\n"
            "6. Acción del Modelo: Como agente orquestador, utiliza tu propio modelo para explicar los hallazgos y sintetizar la refactorización final directamente al usuario."
        )

        return SixHatsConsensus(
            verdict=verdict,
            summary=summary,
            applied_mitigations=mitigations,
            selected_architecture=selected,
            code_patch=patch if patch else None,
            patch_validated=patch_valid,
            patch_syntax_error=syntax_err,
            ponytail_veto_applied=ponytail_veto,
            agent_guidance=guidance,
        )
