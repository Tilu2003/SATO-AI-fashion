# ============================================================================
# FILE: validation_module.py
# PURPOSE: Pattern quality validation and scoring
# ============================================================================

from typing import Dict, Any


def run_3d_validation(pattern_data: Dict[str, Any], measurements: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validates a generated pattern against user measurements.
    Scores pattern quality based on confidence and measurement coverage.
    """
    issues = []
    score = 100

    # Penalise low AI confidence
    confidence = pattern_data.get("translation_confidence", pattern_data.get("confidence_score", 0.85))
    if confidence < 0.5:
        score -= 20
        issues.append("Low translation confidence — review AI output carefully.")
    elif confidence < 0.75:
        score -= 10
        issues.append("Moderate confidence — double-check key measurements.")

    # Penalise unsupported features
    unsupported = pattern_data.get("unsupported_features", [])
    if unsupported:
        penalty = min(len(unsupported) * 5, 20)
        score -= penalty
        issues.append(f"{len(unsupported)} feature(s) require manual adjustment.")

    # Basic measurement sanity checks
    chest = measurements.get("chestCircumference", measurements.get("chest", 0))
    waist = measurements.get("waistCircumference", measurements.get("waist", 0))
    hips  = measurements.get("hipCircumference",  measurements.get("hips",  0))

    if chest and waist and chest < waist:
        score -= 5
        issues.append("Warning: waist measurement is larger than chest — please verify.")

    if chest and hips and hips < chest * 0.8:
        score -= 5
        issues.append("Warning: hip measurement seems unusually small relative to chest.")

    score = max(score, 0)

    return {
        "status": "SUCCESS" if score >= 60 else "NEEDS_REVIEW",
        "score": score,
        "issues": issues,
    }
