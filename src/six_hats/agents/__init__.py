from typing import Any, Type
from six_hats.agents.base import HatAgent
from six_hats.agents.white import WhiteHatAgent
from six_hats.agents.red import RedHatAgent
from six_hats.agents.black import BlackHatAgent
from six_hats.agents.yellow import YellowHatAgent
from six_hats.agents.green import GreenHatAgent
from six_hats.agents.blue import BlueHatAgent

HAT_AGENTS_REGISTRY: dict[str, Type[HatAgent]] = {
    "white": WhiteHatAgent,
    "red": RedHatAgent,
    "black": BlackHatAgent,
    "yellow": YellowHatAgent,
    "green": GreenHatAgent,
    "blue": BlueHatAgent,
}


def get_agent(hat_name: str, **kwargs: Any) -> HatAgent:
    """Devuelve una instancia del agente especializado según el color del sombrero."""
    normalized = hat_name.strip().lower()
    # Soporte para nombres en español
    es_to_en = {
        "blanco": "white",
        "rojo": "red",
        "negro": "black",
        "amarillo": "yellow",
        "verde": "green",
        "azul": "blue",
    }
    key = es_to_en.get(normalized, normalized)

    if key not in HAT_AGENTS_REGISTRY:
        valid_keys = ", ".join(list(HAT_AGENTS_REGISTRY.keys()))
        raise ValueError(f"Sombrero no reconocido: «{hat_name}». Opciones válidas: {valid_keys}")

    agent_cls = HAT_AGENTS_REGISTRY[key]
    return agent_cls(**kwargs)


__all__ = [
    "HatAgent",
    "WhiteHatAgent",
    "RedHatAgent",
    "BlackHatAgent",
    "YellowHatAgent",
    "GreenHatAgent",
    "BlueHatAgent",
    "HAT_AGENTS_REGISTRY",
    "get_agent",
]
