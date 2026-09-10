"""Ejemplo de integración de Six Hats en entornos Multi-Agente (LangGraph / CrewAI / AutoGen).

Muestra cómo encapsular los Seis Sombreros como un nodo de deliberación forense
en un grafo de agentes o como herramientas especializadas asignadas a agentes de rol.
"""

import asyncio
from typing import TypedDict, Annotated, Sequence
from six_hats.core.orchestrator import SixHatsOrchestrator


class AgentState(TypedDict):
    """Estado compartido en un flujo multi-agente."""
    task: str
    code: str
    approved: bool
    review_summary: str
    patches: list[str]


class SixHatsAgentNode:
    """Nodo de deliberación para grafos de ejecución multi-agente."""

    def __init__(self):
        self.orchestrator = SixHatsOrchestrator()

    async def __call__(self, state: AgentState) -> dict:
        """Ejecuta el ciclo de los 6 Sombreros sobre el estado del código propuesto."""
        print("[Multi-Agent] Nodo Six Hats iniciando análisis del código...")
        result = await self.orchestrator.run_full_cycle(
            code_content=state["code"],
            task_context=state["task"],
            is_diff=False,
        )

        is_approved = result.consensus.verdict == "APPROVE"
        summary = (
            f"Veredicto: {result.consensus.verdict}. "
            f"Arquitectura: {result.consensus.selected_architecture}. "
            f"Sobreingeniería Ponytail: {result.red.bloat_score} %."
        )

        patches = []
        if result.consensus.code_patch:
            patches.append(result.consensus.code_patch)

        return {
            "approved": is_approved,
            "review_summary": summary,
            "patches": patches,
        }


async def main():
    print("=== Pipeline Multi-Agente con Six Hats ===")
    node = SixHatsAgentNode()

    # Estado inicial simulado proveniente de un agente desarrollador
    initial_state: AgentState = {
        "task": "Implementar procesamiento de archivos sin cuellos de botella",
        "code": "def process(path):\n    data = open(path).read()\n    return data\n",
        "approved": False,
        "review_summary": "",
        "patches": [],
    }

    updates = await node(initial_state)
    new_state = {**initial_state, **updates}

    print("\nEstado tras deliberación del nodo Six Hats:")
    print(f"• Aprobado: {new_state['approved']}")
    print(f"• Resumen: {new_state['review_summary']}")
    print(f"• Parches de mitigación generados: {len(new_state['patches'])}")


if __name__ == "__main__":
    asyncio.run(main())
