import pytest
from app.scanner import Scanner
from app.models import Severity


def test_scanner_initialization():
    """Test scanner initialization"""
    scanner = Scanner(target="example.com", timeout=60)
    assert scanner.target == "example.com"
    assert scanner.timeout == 60


def test_parse_findings():
    """Test parsing findings from testssl results"""
    scanner = Scanner(target="example.com")
    
    # Mock testssl result
    testssl_data = {
        "json": {
            "certificate": {
                "notAfter": "20240101000000",
                "keySize": 1024
            },
            "protocols": [
                {"id": "SSLv2"},
                {"id": "TLS1_2"}
            ],
            "ciphers": [
                {"cipher": "TLS_RSA_WITH_MD5"},
                {"cipher": "TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384"}
            ]
        }
    }
    
    findings = scanner.parse_testssl_results(testssl_data)
    
    # Should find weak key size
    weak_key_findings = [f for f in findings if f["category"] == "small_rsa"]
    assert len(weak_key_findings) > 0
    
    # Should find deprecated protocol
    deprecated_findings = [f for f in findings if f["category"] == "deprecated_alg"]
    assert len(deprecated_findings) > 0


def test_pq_score_calculation():
    """Test PQ score calculation"""
    from app.pq_score import calculate_pq_score
    from app.models import Finding
    
    # Create mock findings
    findings = [
        Finding(
            asset_type="cert",
            category="small_rsa",
            detail_json={"key_size": 1024},
            severity=Severity.P0,
            evidence="Weak key"
        ),
        Finding(
            asset_type="protocol",
            category="deprecated_alg",
            detail_json={"protocol": "SSLv2"},
            severity=Severity.P1,
            evidence="Deprecated protocol"
        )
    ]
    
    score, level = calculate_pq_score(findings)
    
    assert isinstance(score, float)
    assert score >= 0 and score <= 100
    assert level in ["Low", "Medium", "High", "Critical"]


