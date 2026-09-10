"""Ejemplo de integración de Six Hats con modelos Nous Hermes 2/3 (ChatML Tool Calling).

Este script demuestra cómo conectar un modelo Hermes alojado localmente
(Ollama, vLLM o LM Studio) con el motor analítico de Six Hats.
"""

import json
import asyncio
from pathlib import Path
from six_hats.core.orchestrator import SixHatsOrchestrator

# Inicializar motor analítico local
orchestrator = SixHatsOrchestrator()


async def execute_tool_call(tool_name: str, arguments: dict) -> str:
    """Despachador local que atiende las llamadas <tool_call> emitidas por Hermes."""
    if tool_name == "six_hats_review":
        res = await orchestrator.run_full_cycle(
            code_content=arguments.get("code_diff", ""),
            is_diff=arguments.get("is_diff", False),
            task_context=arguments.get("task_context", ""),
        )
        return json.dumps(res.model_dump(), indent=2, ensure_ascii=False)
    elif tool_name == "six_hats_debate":
        res = await orchestrator.run_debate(arguments.get("architecture_proposal", ""))
        return json.dumps(res, indent=2, ensure_ascii=False)
    elif tool_name == "six_hats_quick_check":
        res = await orchestrator.run_critics(arguments.get("code_diff", ""))
        return json.dumps(res, indent=2, ensure_ascii=False)
    elif tool_name == "six_hats_ponytail_audit":
        res = await orchestrator.run_ponytail_audit(
            code_content=arguments.get("code", ""),
            max_acceptable_bloat=arguments.get("threshold", 25.0),
        )
        return json.dumps(res, indent=2, ensure_ascii=False)
    else:
        return json.dumps({"error": f"Herramienta '{tool_name}' desconocida."})


async def main():
    system_prompt_path = Path(__file__).parent / "system_prompt.txt"
    system_prompt = system_prompt_path.read_text(encoding="utf-8")

    print("=== Configuración de Agente Hermes con Six Hats ===")
    print(f"System prompt cargado ({len(system_prompt)} caracteres).")

    # Simulación de llamada emitida por Hermes:
    simulated_call = {
        "name": "six_hats_ponytail_audit",
        "arguments": {
            "code": "class DataFetcher:\n    def fetch(self, x):\n        return x\n",
            "threshold": 20.0,
        },
    }

    print(f"\nProcesando llamada de herramienta: {simulated_call['name']}...")
    result_str = await execute_tool_call(simulated_call["name"], simulated_call["arguments"])
    result = json.loads(result_str)

    print("\nResultado procesado por Six Hats:")
    print(f"• Bloat Score: {result.get('bloat_score')} %")
    print(f"• Estado de Aceptabilidad: {result.get('is_acceptable')}")
    print(f"• Violaciones identificadas: {len(result.get('violations', []))}")


if __name__ == "__main__":
    asyncio.run(main())
