import time
import asyncio
from typing import Dict, Any, Optional, List
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
        trace: List[Dict[str, Any]] = []
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

    async def run_critics(self, code_content: str, is_diff: bool = False) -> Dict[str, Any]:
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

    async def run_debate(self, architecture_proposal: str) -> Dict[str, Any]:
        """Debate dialéctico entre Sombrero Negro (Auditoría de riesgos) y Verde (Innovación)."""
        # Creación de contexto fáctico mínimo
        white_dummy = await self.runner.execute_white_hat(architecture_proposal)
        
        # Sombrero Verde defiende o expande la propuesta
        green_proposals = await self.runner.execute_green_hat(white_dummy, architecture_proposal)
        
        # Sombrero Negro ataca la propuesta identificando riesgos
        black_findings = await self.runner.execute_black_hat(white_dummy, green_proposals, architecture_proposal)
        
        # Sombrero Azul modera y emite síntesis
        red_assessment = await self.runner.execute_red_hat(white_dummy, green_proposals, architecture_proposal)
        yellow_benefits = await self.runner.execute_yellow_hat(white_dummy, green_proposals, architecture_proposal)
        
        consensus = await self.runner.execute_blue_hat(
            white=white_dummy,
            green=green_proposals,
            black=black_findings,
            yellow=yellow_benefits,
            red=red_assessment,
        )

        return {
            "proposal": architecture_proposal,
            "green_counterproposals": [p.model_dump() for p in green_proposals],
            "black_critique": [f.model_dump() for f in black_findings],
            "blue_resolution": consensus.model_dump(),
        }

    async def run_ponytail_audit(self, code_content: str, max_acceptable_bloat: float = 25.0) -> Dict[str, Any]:
        """Ejecuta una auditoría focalizada en la Escalera de la Pereza de Ponytail para detectar sobreingeniería."""
        from six_hats.tools.ponytail_rules import audit_ponytail

        report = audit_ponytail(code_content, max_acceptable_bloat=max_acceptable_bloat)
        return report.model_dump()

