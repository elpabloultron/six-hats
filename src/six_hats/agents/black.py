from typing import Any, Optional
from six_hats.agents.base import HatAgent
from six_hats.core.models import WhiteHatData, GreenHatProposal, BlackHatFinding
from six_hats.tools.security_scanner import scan_security_vulnerabilities
from six_hats.tools.ast_extractor import extract_ast_data


class BlackHatAgent(HatAgent):
    """Agente Sombrero Negro: Juicio crítico, auditoría adversarial de seguridad, fallos y riesgos."""

    def __init__(self):
        super().__init__(
            hat_name="black",
            hat_color="black",
            role="Auditoría Adversarial, CWE/OWASP e Invariantes",
            emoji="⚫",
            description="Identifica vulnerabilidades de seguridad (CWE/OWASP), puntos únicos de fallo, complejidad extrema y genera hipótesis de rotura.",
        )

    async def execute(
        self,
        code_content: str,
        white_data: Optional[WhiteHatData] = None,
        green_proposals: Optional[list[GreenHatProposal]] = None,
        **kwargs: Any,
    ) -> list[BlackHatFinding]:
        """Ejecuta un escaneo adversarial completo buscando fallos y vulnerabilidades de seguridad."""
        findings = scan_security_vulnerabilities(code_content)

        # Si no se suministran datos del Sombrero Blanco, se extraen para enriquecer el juicio
        if white_data is None and code_content.strip():
            white_data = extract_ast_data(code_content, 0, 0)

        if white_data:
            if white_data.cyclomatic_complexity > 12:
                findings.append(
                    BlackHatFinding(
                        severity="HIGH",
                        risk_type="Complejidad Ciclomática Excesiva (CWE-398)",
                        location=f"Complejidad McCabe: {white_data.cyclomatic_complexity}",
                        description="Flujo de ejecución con demasiadas ramificaciones anidadas, elevando la superficie de regresiones.",
                        cwe_owasp_id="CWE-398",
                        remediation="Modularizar en funciones puras independientes con responsabilidad única.",
                    )
                )

            if white_data.cognitive_complexity > 15:
                findings.append(
                    BlackHatFinding(
                        severity="MEDIUM",
                        risk_type="Riesgo de Error Humano por Carga Cognitiva Severa",
                        location=f"Complejidad Cognitiva SonarSource: {white_data.cognitive_complexity}",
                        description="El código exige retener demasiados contextos lógicos simultáneos, propiciando fallos en guardias.",
                        cwe_owasp_id="CWE-710",
                        remediation="Aplanar estructuras if anidadas aplicando cláusulas de guarda (early returns).",
                    )
                )

        return findings
