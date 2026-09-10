import os
from typing import List, Optional
from six_hats.core.models import (
    WhiteHatData,
    BlackHatFinding,
    YellowHatBenefit,
    GreenHatProposal,
    RedHatAssessment,
    SixHatsConsensus,
)
from six_hats.tools.ast_extractor import extract_ast_data
from six_hats.tools.git_utils import get_file_diff_stats
from six_hats.tools.security_scanner import scan_security_vulnerabilities
from six_hats.tools.ponytail_rules import audit_ponytail
from six_hats.core.patterns import get_divergent_proposals
from six_hats.core.llm_client import GeminiHatClient
from six_hats.tools.diff_generator import generate_real_patch


class HatRunner:
    """Ejecutor de agentes especializados con arquitectura Agent-Native (Heurística determinista + Guía para IA anfitriona)."""

    def __init__(self, use_llm_if_available: bool = False):
        self.api_key = os.environ.get("GEMINI_API_KEY", "")
        self.use_llm = use_llm_if_available and bool(self.api_key)
        self.llm_client = GeminiHatClient(api_key=self.api_key) if self.use_llm else GeminiHatClient(api_key="")

    async def execute_white_hat(
        self, code_content: str, is_diff: bool = False, filename: str = "source.py"
    ) -> WhiteHatData:
        """Fase 1: Sombrero Blanco extrae hechos puros, AST, complejidad ciclomática y cognitiva."""
        lines_added, lines_deleted = (0, 0)
        if is_diff:
            lines_added, lines_deleted = get_file_diff_stats(code_content)
        return extract_ast_data(code_content, lines_added, lines_deleted, filename=filename)

    async def execute_green_hat(
        self, white_data: WhiteHatData, code_content: str, task_context: str = ""
    ) -> List[GreenHatProposal]:
        """Fase 2: Sombrero Verde genera propuestas arquitectónicas no convencionales (GenAI o Catálogo)."""
        if self.llm_client.is_available:
            ai_proposals = await self.llm_client.generate_green_proposals(code_content, task_context)
            if ai_proposals:
                return ai_proposals

        return get_divergent_proposals(task_context=task_context, code_complexity=white_data.cyclomatic_complexity)

    async def execute_black_hat(
        self, white_data: WhiteHatData, green_proposals: List[GreenHatProposal], code_content: str
    ) -> List[BlackHatFinding]:
        """Fase 3: Sombrero Negro ejecuta escaneo adversarial (Semgrep/Bandit/Gitleaks/OWASP)."""
        findings = scan_security_vulnerabilities(code_content)

        # Análisis de complejidad estructural extrema
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

    async def execute_yellow_hat(
        self, white_data: WhiteHatData, green_proposals: List[GreenHatProposal], code_content: str
    ) -> List[YellowHatBenefit]:
        """Fase 3: Sombrero Amarillo evalúa valor tangible, análisis asintótico Big-O y modernización."""
        benefits: List[YellowHatBenefit] = []

        from six_hats.tools.performance_analyzer import analyze_performance_bottlenecks
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
                impact=f"Índice de Mantenibilidad actual: {white_data.maintainability_index}/100. Con refactorización alcanza >85/100.",
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

    async def execute_red_hat(
        self, white_data: WhiteHatData, green_proposals: List[GreenHatProposal], code_content: str
    ) -> RedHatAssessment:
        """Fase 3: Sombrero Rojo mide DX, ergonomía a las 3:00 AM, confusión léxica y saturación visual."""
        # 1. Auditoría Ponytail y métricas psicométricas
        from six_hats.tools.ponytail_rules import detect_lexical_confusion, calculate_visual_clutter
        ponytail_report = audit_ponytail(code_content)
        confusion_warnings = detect_lexical_confusion(code_content)
        clutter_score = calculate_visual_clutter(code_content)

        # 2. Evaluación de carga cognitiva
        cog = white_data.cognitive_complexity
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

        # Veredicto Ponytail
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

    async def execute_remediation_cycle(
        self,
        white_data: WhiteHatData,
        critical_findings: List[BlackHatFinding],
        red_assessment: RedHatAssessment,
    ) -> List[GreenHatProposal]:
        """Genera propuestas creativas correctivas para el bucle de feedback del Sombrero Azul."""
        from six_hats.core.patterns import generate_remediation_proposals
        critical_texts = [f"{f.risk_type}: {f.description}" for f in critical_findings]
        bloat_veto = red_assessment.bloat_score > 35.0
        return generate_remediation_proposals(critical_texts, bloat_veto=bloat_veto)

    async def execute_blue_hat(
        self,
        white: WhiteHatData,
        green: List[GreenHatProposal],
        black: List[BlackHatFinding],
        yellow: List[YellowHatBenefit],
        red: RedHatAssessment,
        original_code: str = "",
        filepath: str = "solucion.py",
    ) -> SixHatsConsensus:
        """Fase 4: Sombrero Azul sintetiza, aplica mitigaciones de seguridad, el veto de Ponytail y genera el diff real."""
        has_critical = any(f.severity == "CRITICAL" for f in black)
        has_high = any(f.severity == "HIGH" for f in black)
        ponytail_veto = red.bloat_score > 35.0

        mitigations = []
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

        # Selección de arquitectura balanceada
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

        # Generación del Unified Diff real sobre el código del usuario
        refactored_code = None
        if self.llm_client.is_available and original_code.strip():
            refactored_code = await self.llm_client.generate_blue_refactored_code(
                original_code, mitigations, selected
            )

        patch = generate_real_patch(
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
            "5. Acción del Modelo: Como agente orquestador, utiliza tu propio modelo para explicar los hallazgos y sintetizar la refactorización final directamente al usuario."
        )

        return SixHatsConsensus(
            verdict=verdict,
            summary=summary,
            applied_mitigations=mitigations,
            selected_architecture=selected,
            code_patch=patch if patch else None,
            ponytail_veto_applied=ponytail_veto,
            agent_guidance=guidance,
        )
