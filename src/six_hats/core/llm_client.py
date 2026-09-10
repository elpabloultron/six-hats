"""Cliente LLM oficial para Google Gemini utilizando google-genai.

Permite enriquecer dinámicamente las propuestas del Sombrero Verde y la síntesis
de código del Sombrero Azul, con fallback automático y silencioso si no hay API key.
"""

import os
import json
import logging
from typing import List, Optional, Dict, Any
from six_hats.core.models import GreenHatProposal
from six_hats.core.prompts import GREEN_HAT_PROMPT, BLUE_HAT_PROMPT

logger = logging.getLogger("six_hats.llm_client")


class GeminiHatClient:
    """Adaptador de inferencia para los Seis Sombreros con el SDK google-genai."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-2.5-flash"):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY", "")
        self.model = model
        self._client = None

        if self.api_key:
            try:
                from google import genai
                self._client = genai.Client(api_key=self.api_key)
            except Exception as e:
                logger.debug(f"No se pudo inicializar google-genai: {e}")
                self._client = None

    @property
    def is_available(self) -> bool:
        """Indica si el cliente cuenta con API key válida y SDK cargado."""
        return self._client is not None

    async def generate_green_proposals(self, code_content: str, task_context: str = "") -> Optional[List[GreenHatProposal]]:
        """Genera 3 alternativas arquitectónicas divergentes adaptadas al código analizado."""
        if not self.is_available:
            return None

        prompt = (
            f"Analiza este código y el contexto: '{task_context}'.\n\n"
            f"Código fuente:\n```\n{code_content[:4000]}\n```\n\n"
            "Responde ÚNICAMENTE con un JSON con formato: {\"proposals\": [{\"name\": \"...\", \"paradigm\": \"...\", \"description\": \"...\", \"tradeoff\": \"...\"}]}"
        )

        try:
            from google.genai import types
            config = types.GenerateContentConfig(
                system_instruction=GREEN_HAT_PROMPT,
                temperature=0.85,
                response_mime_type="application/json",
            )
            response = self._client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=config,
            )
            data = json.loads(response.text)
            proposals = [GreenHatProposal(**p) for p in data.get("proposals", [])]
            return proposals if len(proposals) >= 3 else None
        except Exception as e:
            logger.debug(f"Fallo al invocar Sombrero Verde con GenAI: {e}")
            return None

    async def generate_blue_refactored_code(
        self, original_code: str, applied_mitigations: List[str], selected_architecture: str
    ) -> Optional[str]:
        """Sintetiza la versión refactorizada completa del código original aplicando mitigaciones y minimalismo."""
        if not self.is_available:
            return None

        mitigations_str = "\n".join(f"- {m}" for m in applied_mitigations)
        prompt = (
            f"Refactoriza el siguiente código para aplicar las mitigaciones de seguridad y arquitectura:\n"
            f"Arquitectura elegida: {selected_architecture}\n"
            f"Mitigaciones requeridas:\n{mitigations_str}\n\n"
            f"Código original:\n```\n{original_code[:4000]}\n```\n\n"
            "Devuelve ÚNICAMENTE el código refactorizado completo sin explicaciones en texto ni comentarios introductorios."
        )

        try:
            from google.genai import types
            config = types.GenerateContentConfig(
                system_instruction=BLUE_HAT_PROMPT,
                temperature=0.2,
            )
            response = self._client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=config,
            )
            return response.text.strip()
        except Exception as e:
            logger.debug(f"Fallo al invocar Sombrero Azul con GenAI: {e}")
            return None
