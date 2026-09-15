from typing import List, Dict, Optional, Literal, Any
from pydantic import BaseModel, Field


class WhiteHatData(BaseModel):
    symbols_affected: List[str] = Field(default_factory=list, description="Funciones, clases o métodos afectados")
    cyclomatic_complexity: int = Field(default=1, description="Complejidad ciclomática calculada (McCabe)")
    cognitive_complexity: int = Field(default=0, description="Complejidad cognitiva calculada (SonarSource)")
    maintainability_index: float = Field(default=100.0, description="Índice de Mantenibilidad (0 a 100)")
    lines_added: int = Field(default=0, description="Líneas de código añadidas")
    lines_deleted: int = Field(default=0, description="Líneas de código eliminadas")
    test_coverage_pct: float = Field(default=0.0, description="Porcentaje de cobertura de tests estimado o medido")
    dependencies: List[str] = Field(default_factory=list, description="Módulos o bibliotecas importadas")
    git_churn_score: Optional[str] = Field(None, description="Frecuencia histórica de modificaciones y autores en Git (pydriller)")
    historical_risk: Optional[str] = Field(None, description="Clasificación de riesgo de hotspot histórico (LOW, MEDIUM, HIGH_HOTSPOT)")
    coverage_summary: Optional[str] = Field(None, description="Resumen de cobertura real de tests si está disponible")


class BlackHatFinding(BaseModel):
    severity: Literal["CRITICAL", "HIGH", "MEDIUM", "LOW"] = Field(description="Nivel de gravedad del riesgo")
    risk_type: str = Field(description="Tipo de riesgo (concurrencia, seguridad, fuga de recursos, etc.)")
    location: str = Field(description="Ubicación o contexto del hallazgo en el código")
    description: str = Field(description="Explicación detallada del fallo potencial o vulnerabilidad")
    cwe_owasp_id: Optional[str] = Field(None, description="Identificador CWE u OWASP asociado")
    remediation: Optional[str] = Field(None, description="Recomendación de remediación técnica")
    property_invariants: List[str] = Field(
        default_factory=list,
        description="Casos límite e invariantes de prueba por propiedades basados en Hypothesis (fuzzing conceptual)",
    )


class YellowHatBenefit(BaseModel):
    metric: str = Field(description="Métrica impactada (latencia, rendimiento, reusabilidad)")
    impact: str = Field(description="Magnitud y justificación del beneficio positivo")
    feasibility: Literal["ALTA", "MEDIA", "BAJA"] = Field(description="Factibilidad técnica de implementación")
    asymptotic_optimization: Optional[str] = Field(
        default=None,
        description="Detección de trampas asintóticas Big-O optimizables (ej. O(n²) a O(n))",
    )


class GreenHatProposal(BaseModel):
    name: str = Field(description="Nombre identificativo de la alternativa arquitectónica")
    paradigm: str = Field(description="Paradigma o patrón (ej. Reactivo, Funcional, Zero-Alloc)")
    description: str = Field(description="Descripción de la propuesta disruptiva")
    tradeoff: str = Field(description="Compromiso o costo asociado a esta alternativa")


class RedHatAssessment(BaseModel):
    cognitive_load_score: str = Field(description="Nivel de carga cognitiva estimada (Baja, Media, Alta)")
    gut_feeling: str = Field(description="Impresión intuitiva visceral sobre el diseño")
    ergonomics: str = Field(description="Evaluación de legibilidad y facilidad de depuración a las 3:00 AM")
    bloat_score: float = Field(default=0.0, description="Índice Ponytail de sobreingeniería (0 a 100 %)")
    ladder_violations: List[str] = Field(default_factory=list, description="Violaciones detectadas a la Escalera de la Pereza")
    lines_reducible_pct: float = Field(default=0.0, description="Porcentaje estimado de líneas superfluas")
    ponytail_verdict: str = Field(default="APROBADO (Código Conciso)", description="Veredicto de sobreingeniería")
    lexical_confusion_warnings: List[str] = Field(
        default_factory=list,
        description="Variables con nombres engañosamente similares en el mismo ámbito (distancia Levenshtein ≤ 2)",
    )
    visual_clutter_score: float = Field(
        default=0.0,
        description="Índice de saturación visual por ruido, densidad y anidamiento continuo (0 a 100 %)",
    )


class SixHatsConsensus(BaseModel):
    verdict: Literal["APPROVE", "REJECT", "REQUIRE_CHANGES"] = Field(description="Decisión final del Sombrero Azul")
    summary: str = Field(description="Síntesis ejecutiva de la deliberación")
    applied_mitigations: List[str] = Field(default_factory=list, description="Mitigaciones a los riesgos del Sombrero Negro")
    selected_architecture: str = Field(description="Arquitectura o alternativa seleccionada")
    code_patch: Optional[str] = Field(None, description="Unified diff con la solución final")
    patch_validated: bool = Field(default=False, description="Indica si el parche fue verificado sintácticamente con éxito")
    patch_syntax_error: Optional[str] = Field(default=None, description="Error sintáctico detectado al validar el parche si ocurrió")
    ponytail_veto_applied: bool = Field(default=False, description="Indica si se aplicó veto de simplicidad de Ponytail")
    agent_guidance: Optional[str] = Field(
        default=None,
        description="Mandato y directrices cognitivas para que la IA anfitriona proceda con la solución final",
    )


class SixHatsReviewResult(BaseModel):
    white: WhiteHatData
    green: List[GreenHatProposal] = Field(default_factory=list)
    black: List[BlackHatFinding] = Field(default_factory=list)
    yellow: List[YellowHatBenefit] = Field(default_factory=list)
    red: RedHatAssessment
    consensus: SixHatsConsensus
    deliberation_trace: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Trazas estructuradas de ejecución del grafo (Spans) con marcas de tiempo y transiciones",
    )
    feedback_loop_count: int = Field(
        default=0,
        description="Número de bucles de retroalimentación dialéctica ejecutados ante riesgos críticos",
    )
