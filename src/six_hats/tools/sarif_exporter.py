"""Exportador oficial a formato SARIF v2.1.0 (Static Analysis Results Interchange Format).

Permite integrar los hallazgos del Sombrero Negro y Ponytail directamente en GitHub
Code Scanning, GitLab SAST y dashboards de seguridad CI/CD.
"""

import json
from typing import List, Dict, Any
from six_hats.core.models import SixHatsReviewResult


SEVERITY_TO_SARIF_LEVEL = {
    "CRITICAL": "error",
    "HIGH": "error",
    "MEDIUM": "warning",
    "LOW": "note",
}


def build_sarif_report(result: SixHatsReviewResult, filepath: str = "code.py") -> Dict[str, Any]:
    """Construye el documento SARIF v2.1.0 a partir del resultado de la revisión de Six Hats."""
    rules: List[Dict[str, Any]] = []
    sarif_results: List[Dict[str, Any]] = []
    seen_rule_ids = set()

    # 1. Mapeo de hallazgos del Sombrero Negro
    for idx, finding in enumerate(result.black):
        rule_id = finding.cwe_owasp_id or f"SH-BLACK-{idx + 1:03d}"
        if rule_id not in seen_rule_ids:
            seen_rule_ids.add(rule_id)
            rules.append({
                "id": rule_id,
                "name": finding.risk_type.replace(" ", "_"),
                "shortDescription": {"text": finding.risk_type},
                "fullDescription": {"text": finding.description},
                "defaultConfiguration": {"level": SEVERITY_TO_SARIF_LEVEL.get(finding.severity, "warning")},
            })

        sarif_results.append({
            "ruleId": rule_id,
            "level": SEVERITY_TO_SARIF_LEVEL.get(finding.severity, "warning"),
            "message": {"text": f"{finding.description} (Ubicación: {finding.location})"},
            "locations": [
                {
                    "physicalLocation": {
                        "artifactLocation": {"uri": filepath},
                        "region": {"startLine": 1},
                    }
                }
            ],
        })

    # 2. Mapeo de violaciones de la Escalera de la Pereza de Ponytail
    for idx, violation_txt in enumerate(result.red.ladder_violations):
        rule_id = f"PONYTAIL-{idx + 1:03d}"
        if rule_id not in seen_rule_ids:
            seen_rule_ids.add(rule_id)
            rules.append({
                "id": rule_id,
                "name": "Ponytail_Overengineering_Violation",
                "shortDescription": {"text": "Violación a la Escalera de la Pereza (Anti-Sobreingeniería)"},
                "fullDescription": {"text": violation_txt},
                "defaultConfiguration": {"level": "note"},
            })

        sarif_results.append({
            "ruleId": rule_id,
            "level": "note",
            "message": {"text": violation_txt},
            "locations": [
                {
                    "physicalLocation": {
                        "artifactLocation": {"uri": filepath},
                        "region": {"startLine": 1},
                    }
                }
            ],
        })

    sarif_doc = {
        "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "six-hats",
                        "version": "0.1.0",
                        "informationUri": "https://github.com/pablo/six-hats",
                        "rules": rules,
                    }
                },
                "results": sarif_results,
            }
        ],
    }

    return sarif_doc


def export_to_sarif_file(result: SixHatsReviewResult, output_path: str, filepath: str = "code.py") -> None:
    """Escribe el reporte SARIF v2.1.0 en el archivo destino."""
    sarif_data = build_sarif_report(result, filepath=filepath)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(sarif_data, f, indent=2, ensure_ascii=False)
