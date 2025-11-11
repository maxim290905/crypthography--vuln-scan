from typing import List, Dict, Any
from app.models import Finding, Severity


def calculate_pq_score(findings: List[Finding]) -> tuple[float, str]:
    """
    Calculate PQ-score based on findings.
    Returns: (score, level) where level is "Low", "Medium", "High", or "Critical"
    """
    if not findings:
        return 0.0, "Low"
    
    # Component weights
    WEIGHTS = {
        "deprecated_alg": 0.35,
        "weak_key": 0.25,
        "public_exposure": 0.20,
        "cert_lifecycle": 0.10,
        "vulnerable_deps": 0.10,
    }
    
    # Initialize component scores
    component_scores = {key: 0.0 for key in WEIGHTS.keys()}
    
    # Count findings by category
    category_counts = {}
    for finding in findings:
        category = finding.category
        if category not in category_counts:
            category_counts[category] = 0
        category_counts[category] += 1
        
        # Map severity to score contribution
        severity_score = {
            Severity.P0: 1.0,
            Severity.P1: 0.75,
            Severity.P2: 0.5,
            Severity.P3: 0.25,
        }.get(finding.severity, 0.0)
        
        # Add to appropriate component
        if category in ["deprecated_alg", "weak_cipher", "md5", "sha1"]:
            component_scores["deprecated_alg"] = min(1.0, component_scores["deprecated_alg"] + severity_score * 0.1)
        elif category in ["weak_key", "small_rsa", "weak_ec_curve"]:
            component_scores["weak_key"] = min(1.0, component_scores["weak_key"] + severity_score * 0.1)
        elif category == "public_exposure":
            component_scores["public_exposure"] = min(1.0, component_scores["public_exposure"] + severity_score)
        elif category in ["cert_expiry", "cert_expired", "cert_near_expiry"]:
            component_scores["cert_lifecycle"] = min(1.0, component_scores["cert_lifecycle"] + severity_score * 0.2)
        elif category == "vulnerable_deps":
            component_scores["vulnerable_deps"] = min(1.0, component_scores["vulnerable_deps"] + severity_score)
    
    # Calculate weighted sum
    total_score = sum(component_scores[comp] * weight for comp, weight in WEIGHTS.items())
    pq_score = round(total_score * 100)
    
    # Determine level
    if pq_score <= 30:
        level = "Low"
    elif pq_score <= 60:
        level = "Medium"
    elif pq_score <= 85:
        level = "High"
    else:
        level = "Critical"
    
    return float(pq_score), level


def get_top_findings(findings: List[Finding], limit: int = 3) -> List[Dict[str, Any]]:
    """Get top N findings by severity"""
    severity_order = {Severity.P0: 0, Severity.P1: 1, Severity.P2: 2, Severity.P3: 3}
    sorted_findings = sorted(findings, key=lambda f: severity_order.get(f.severity, 99))
    return [
        {
            "severity": f.severity.value,
            "category": f.category,
            "asset_type": f.asset_type,
            "evidence": f.evidence,
        }
        for f in sorted_findings[:limit]
    ]


def estimate_effort(pq_score: float, findings_count: int) -> str:
    """Estimate remediation effort in person-days"""
    if pq_score < 30:
        return "Low (1-2 days)"
    elif pq_score < 60:
        return "Medium (3-5 days)"
    elif pq_score < 85:
        return "High (1-2 weeks)"
    else:
        return "Critical (2-4 weeks)"

