import time
import asyncio
from typing import Any, Optional
from six_hats.core.models import SixHatsReviewResult
from six_hats.core.runner import HatRunner


class SixHatsOrchestrator:
    """Orquestador del Grafo Dialéctico Cíclico con Trazabilidad (LangGraph & OpenTelemetry style)."""

    def __init__(self, runner: Optional[HatRunner] = None):
        self.runner = runner or HatRunner()

    async def run_full_cycle(
        self, code_content: str, is_diff: bool = False, task_context: str = "", filepath: str = "source.py"
    ) -> SixHatsReviewResult:
        """Ejecuta la deliberación completa en el grafo con bucles de reversión y telemetría estructurada."""
        trace: list[dict[str, Any]] = []
        loop_count = 0

        # Span 1: Sombrero Blanco (Evidencia y Métricas)
        t0 = time.perf_counter()
        white_data = await self.runner.execute_white_hat(code_content, is_diff=is_diff, filename=filepath)
        trace.append({
            "span_name": "white_hat_ast_telemetry",
            "hat": "white",
            "duration_ms": round((time.perf_counter() - t0) * 1000, 2),
            "status": "COMPLETED",
            "summary": f"McCabe {white_data.cyclomatic_complexity}, Sonar {white_data.cognitive_complexity}, {len(white_data.dependencies)} deps",
        })

        # Span 2: Sombrero Verde (Ideación Divergente)
        t0 = time.perf_counter()
        green_proposals = await self.runner.execute_green_hat(white_data, code_content, task_context)
        trace.append({
            "span_name": "green_hat_divergent_ideation",
            "hat": "green",
            "duration_ms": round((time.perf_counter() - t0) * 1000, 2),
            "status": "COMPLETED",
            "summary": f"{len(green_proposals)} alternativas arquitectónicas concebidas",
        })

        # Span 3: Crítica Concurrente (Negro, Amarillo y Rojo en paralelo)
        t0 = time.perf_counter()
        black_task = self.runner.execute_black_hat(white_data, green_proposals, code_content)
        yellow_task = self.runner.execute_yellow_hat(white_data, green_proposals, code_content)
        red_task = self.runner.execute_red_hat(white_data, green_proposals, code_content)

        black_findings, yellow_benefits, red_assessment = await asyncio.gather(
            black_task, yellow_task, red_task
        )
        trace.append({
            "span_name": "concurrent_critique_phase",
            "hat": "black_yellow_red",
            "duration_ms": round((time.perf_counter() - t0) * 1000, 2),
            "status": "COMPLETED",
            "summary": f"{len(black_findings)} riesgos, {len(yellow_benefits)} beneficios, bloat {red_assessment.bloat_score} %",
        })

        # Evaluación de Condición de Bucle de Feedback (LangGraph Feedback Loop)
        critical_risks = [f for f in black_findings if f.severity == "CRITICAL"]
        has_severe_bloat = red_assessment.bloat_score > 35.0

        if (critical_risks or has_severe_bloat) and loop_count < 1:
            loop_count += 1
            t0 = time.perf_counter()
            reason = "Vulnerabilidad CRITICAL detectada" if critical_risks else "Veto Ponytail por sobreingeniería severa"
            
            # Retroalimentación correctiva al Sombrero Verde
            remediated_proposals = await self.runner.execute_remediation_cycle(
                white_data, critical_risks, red_assessment
            )
            # Reemplazar o anteponer las propuestas adaptadas
            green_proposals = remediated_proposals

            trace.append({
                "span_name": "cyclic_feedback_loopback",
                "hat": "blue_to_green_loopback",
                "duration_ms": round((time.perf_counter() - t0) * 1000, 2),
                "status": "LOOPBACK_EXECUTED",
                "reason": reason,
                "summary": f"Bucle de reversión activado: {len(remediated_proposals)} propuestas de remediación generadas.",
            })

        # Span 4: Síntesis y Veredicto (Sombrero Azul)
        t0 = time.perf_counter()
        consensus = await self.runner.execute_blue_hat(
            white=white_data,
            green=green_proposals,
            black=black_findings,
            yellow=yellow_benefits,
            red=red_assessment,
            original_code=code_content,
            filepath=filepath,
        )
        trace.append({
            "span_name": "blue_hat_consensus_synthesis",
            "hat": "blue",
            "duration_ms": round((time.perf_counter() - t0) * 1000, 2),
            "status": "COMPLETED",
            "summary": f"Veredicto {consensus.verdict}, arquitectura «{consensus.selected_architecture}»",
        })

        return SixHatsReviewResult(
            white=white_data,
            green=green_proposals,
            black=black_findings,
            yellow=yellow_benefits,
            red=red_assessment,
            consensus=consensus,
            deliberation_trace=trace,
            feedback_loop_count=loop_count,
        )

    async def run_critics(self, code_content: str, is_diff: bool = False) -> dict[str, Any]:
        """Evaluación rápida: Sombrero Blanco (Hechos), Negro (Riesgos) y Amarillo (Valor)."""
        white_data = await self.runner.execute_white_hat(code_content, is_diff=is_diff)
        
        # Generar propuestas base para contextualizar la crítica
        green_proposals = await self.runner.execute_green_hat(white_data, code_content)
        
        black_task = self.runner.execute_black_hat(white_data, green_proposals, code_content)
        yellow_task = self.runner.execute_yellow_hat(white_data, green_proposals, code_content)
        
        black_findings, yellow_benefits = await asyncio.gather(black_task, yellow_task)

        return {
            "white": white_data.model_dump(),
            "black": [b.model_dump() for b in black_findings],
            "yellow": [y.model_dump() for y in yellow_benefits],
        }

    async def run_debate(self, architecture_proposal: str) -> dict[str, Any]:
        """Ejecuta una confrontación dialéctica estricta (debate) entre dos sombreros opuestos."""
        white_data = await self.runner.execute_white_hat(architecture_proposal, is_diff=False)
        proposals = await self.runner.execute_green_hat(white_data, architecture_proposal, "Debate dialéctico formal")
        
        black_findings = await self.runner.execute_black_hat(white_data, proposals, architecture_proposal)
        yellow_benefits = await self.runner.execute_yellow_hat(white_data, proposals, architecture_proposal)
        
        black_list = [
            {"risk": f.risk_type, "severity": f.severity, "desc": f.description, "description": f.description}
            for f in black_findings
        ]
        green_list = [
            {"name": p.name, "paradigm": p.paradigm, "tradeoff": p.tradeoff}
            for p in proposals
        ]
        yellow_list = [
            {"benefit": b.metric, "impact": b.impact, "feasibility": b.feasibility}
            for b in yellow_benefits
        ]

        return {
            "proposal": architecture_proposal,
            "black_critique": black_list,
            "black_hat_critique": black_list,
            "green_counterproposals": green_list,
            "yellow_hat_defense": yellow_list,
            "blue_resolution": {
                "verdict": "APROBADO_CON_CONDICIONES" if black_findings else "APROBADO",
                "summary": "Debate concluido equilibrando resiliencia frente a riesgos con valor técnico de modernización.",
                "selected_architecture": proposals[0].name if proposals else "Arquitectura Modular Pragmática",
                "consensus": (
                    "Debate concluido. El Sombrero Azul dictamina equilibrar la robustez ante los riesgos "
                    "señalados por el Sombrero Negro con las alternativas del Sombrero Verde y los beneficios del Sombrero Amarillo."
                ),
            },
            "synthesis": (
                "Debate concluido. El Sombrero Azul dictamina equilibrar la robustez ante los riesgos "
                "señalados por el Sombrero Negro con los beneficios de rendimiento aportados por el Sombrero Amarillo."
            ),
        }

    async def run_ponytail_audit(self, code_content: str, max_acceptable_bloat: float = 25.0) -> dict[str, Any]:
        """Ejecuta una auditoría estricta contra la Escalera de la Pereza de Ponytail."""
        from six_hats.tools.ponytail_rules import audit_ponytail
        report = audit_ponytail(code_content, max_acceptable_bloat=max_acceptable_bloat)
        return report.model_dump()

    async def run_agent(
        self,
        hat_name: str,
        code_content: str,
        is_diff: bool = False,
        task_context: str = "",
        filepath: str = "source.py",
    ) -> Any:
        """Ejecuta un agente individual por nombre de sombrero con su contexto necesario."""
        normalized = hat_name.strip().lower()
        es_to_en = {
            "blanco": "white",
            "rojo": "red",
            "negro": "black",
            "amarillo": "yellow",
            "verde": "green",
            "azul": "blue",
        }
        hat = es_to_en.get(normalized, normalized)

        if hat == "white":
            return await self.runner.execute_white_hat(code_content, is_diff=is_diff, filename=filepath)
        elif hat == "green":
            white_data = await self.runner.execute_white_hat(code_content, is_diff=is_diff, filename=filepath)
            return await self.runner.execute_green_hat(white_data, code_content, task_context)
        elif hat == "black":
            white_data = await self.runner.execute_white_hat(code_content, is_diff=is_diff, filename=filepath)
            green_proposals = await self.runner.execute_green_hat(white_data, code_content, task_context)
            return await self.runner.execute_black_hat(white_data, green_proposals, code_content)
        elif hat == "yellow":
            white_data = await self.runner.execute_white_hat(code_content, is_diff=is_diff, filename=filepath)
            green_proposals = await self.runner.execute_green_hat(white_data, code_content, task_context)
            return await self.runner.execute_yellow_hat(white_data, green_proposals, code_content)
        elif hat == "red":
            white_data = await self.runner.execute_white_hat(code_content, is_diff=is_diff, filename=filepath)
            green_proposals = await self.runner.execute_green_hat(white_data, code_content, task_context)
            return await self.runner.execute_red_hat(white_data, green_proposals, code_content)
        elif hat == "blue":
            return await self.run_full_cycle(code_content, is_diff=is_diff, task_context=task_context, filepath=filepath)
        else:
            raise ValueError(f"Sombrero no reconocido: «{hat_name}». Opciones válidas: white, red, black, yellow, green, blue.")

