import time
from abc import ABC, abstractmethod
from typing import Any


class HatAgent(ABC):
    """Clase base abstracta para agentes especializados en la metodología de Seis Sombreros."""

    hat_name: str
    hat_color: str
    role: str
    emoji: str
    description: str

    def __init__(self, hat_name: str, hat_color: str, role: str, emoji: str, description: str):
        self.hat_name = hat_name
        self.hat_color = hat_color
        self.role = role
        self.emoji = emoji
        self.description = description

    @abstractmethod
    async def execute(self, *args: Any, **kwargs: Any) -> Any:
        """Ejecuta el análisis o la acción correspondiente a la perspectiva del sombrero."""
        pass

    async def run_with_telemetry(self, span_name: str, *args: Any, **kwargs: Any) -> tuple[Any, dict[str, Any]]:
        """Ejecuta el agente registrando métricas de duración y telemetría de ejecución estructurada."""
        t0 = time.perf_counter()
        result = await self.execute(*args, **kwargs)
        duration_ms = round((time.perf_counter() - t0) * 1000, 2)
        telemetry = {
            "span_name": span_name,
            "hat": self.hat_name,
            "duration_ms": duration_ms,
            "status": "COMPLETED",
        }
        return result, telemetry

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.emoji} ({self.hat_name.capitalize()})>"
