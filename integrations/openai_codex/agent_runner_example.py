"""Ejemplo de integración de Six Hats con OpenAI API / Codex / Function Calling.

Este script demuestra cómo usar las definiciones de herramientas de Six Hats
con cualquier cliente compatible con OpenAI (incluyendo OpenAI, LiteLLM, vLLM, Azure OpenAI).
"""

import json
import asyncio
from pathlib import Path
from six_hats.core.orchestrator import SixHatsOrchestrator

orchestrator = SixHatsOrchestrator()


async def handle_tool_call(name: str, arguments: dict) -> dict:
    """Enruta y ejecuta la función invocada por el modelo de OpenAI."""
    if name == "six_hats_review":
        res = await orchestrator.run_full_cycle(
            code_content=arguments.get("code_diff", ""),
            is_diff=arguments.get("is_diff", False),
            task_context=arguments.get("task_context", ""),
        )
        return res.model_dump()
    elif name == "six_hats_debate":
        return await orchestrator.run_debate(arguments.get("architecture_proposal", ""))
    elif name == "six_hats_quick_check":
        return await orchestrator.run_critics(arguments.get("code_diff", ""))
    elif name == "six_hats_ponytail_audit":
        return await orchestrator.run_ponytail_audit(
            code_content=arguments.get("code", ""),
            max_acceptable_bloat=arguments.get("threshold", 25.0),
        )
    return {"error": f"Herramienta '{name}' no soportada"}


async def main():
    tools_file = Path(__file__).parent / "tools.json"
    tools = json.loads(tools_file.read_text(encoding="utf-8"))

    print("=== OpenAI Codex / Function Calling con Six Hats ===")
    print(f"Cargadas {len(tools)} herramientas:")
    for t in tools:
        fn = t["function"]
        print(f" - {fn['name']}: {fn['description'].splitlines()[0]}")

    # Ejemplo de invocación de six_hats_quick_check
    sample_code = """
    def login(user, password):
        if user == "admin" and password == "secret":
            return True
        return False
    """
    print("\nEjecutando six_hats_quick_check sobre función de login...")
    result = await handle_tool_call("six_hats_quick_check", {"code_diff": sample_code})

    print("\nResumen del chequeo rápido:")
    print(f"• Complejidad Ciclomática: {result['white'].get('cyclomatic_complexity')}")
    print(f"• Hallazgos del Sombrero Negro: {len(result.get('black', []))}")
    print(f"• Beneficios del Sombrero Amarillo: {len(result.get('yellow', []))}")


if __name__ == "__main__":
    asyncio.run(main())
