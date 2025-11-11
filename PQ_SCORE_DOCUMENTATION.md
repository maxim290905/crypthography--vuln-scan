# PQ-Score Algorithm Documentation

## Overview

PQ-Score (Post-Quantum Security Score) is a composite metric that evaluates the cryptographic security posture of scanned assets. The score ranges from 0 to 100, where higher scores indicate higher risk.

## Components and Weights

The PQ-Score is calculated using a weighted sum of five components:

### 1. Deprecated Algorithms (35% weight)
- **Detection**: Presence of deprecated cryptographic algorithms
- **Examples**:
  - RSA keys < 2048 bits
  - MD5 hash algorithm
  - SHA1 hash algorithm
  - SSLv2, SSLv3, TLS 1.0, TLS 1.1 protocols
  - Weak cipher suites (RC4, DES, 3DES)

### 2. Weak Key Sizes (25% weight)
- **Detection**: Cryptographic keys below recommended sizes
- **Examples**:
  - RSA keys < 3072 bits (P1 severity)
  - RSA keys < 2048 bits (P0 severity)
  - Small elliptic curve parameters

### 3. Public Exposure (20% weight)
- **Detection**: Internet-facing services
- **Scoring**: All publicly accessible targets receive a base score

### 4. Certificate Lifecycle Issues (10% weight)
- **Detection**: Certificate expiration and renewal problems
- **Examples**:
  - Expired certificates (P0)
  - Certificates expiring within 30 days (P1)

### 5. Vulnerable Dependencies (10% weight)
- **Detection**: Known vulnerabilities in cryptographic libraries
- **Note**: Currently placeholder for future SBOM integration

## Calculation Formula

```
PQ-Score = round(100 * (
    0.35 * deprecated_alg_score +
    0.25 * weak_key_score +
    0.20 * public_exposure_score +
    0.10 * cert_lifecycle_score +
    0.10 * vulnerable_deps_score
))
```

Each component score is normalized to 0.0-1.0 range.

## Severity Mapping

Findings are categorized by severity:

- **P0 (Critical)**: Immediate action required
  - Expired certificates
  - RSA keys < 2048 bits
  - Critical vulnerabilities

- **P1 (High)**: Address within 1-2 weeks
  - RSA keys < 3072 bits
  - Certificates expiring soon
  - Deprecated protocols

- **P2 (Medium)**: Schedule for next maintenance window
  - Weak cipher suites
  - Public exposure

- **P3 (Low)**: Low priority improvements
  - Minor configuration issues

## Risk Levels

Based on PQ-Score:

| Score Range | Level | Description |
|------------|-------|-------------|
| 0-30 | Low | Minimal risk, good security posture |
| 31-60 | Medium | Some issues present, review recommended |
| 61-85 | High | Significant security concerns, action needed |
| 86-100 | Critical | Critical vulnerabilities, immediate action required |

## Remediation Effort Estimation

Based on PQ-Score and findings count:

- **Low (1-2 days)**: Score < 30
- **Medium (3-5 days)**: Score 30-60
- **High (1-2 weeks)**: Score 61-85
- **Critical (2-4 weeks)**: Score > 85

## Example Calculation

For a target with:
- 1 expired certificate (P0)
- 1 RSA 1024-bit key (P0)
- 1 SSLv3 protocol enabled (P1)
- Publicly accessible

Component scores:
- Deprecated algorithms: 0.8 (high due to multiple issues)
- Weak keys: 1.0 (critical RSA 1024)
- Public exposure: 1.0
- Cert lifecycle: 1.0 (expired cert)
- Vulnerable deps: 0.0 (none detected)

PQ-Score = round(100 * (0.35*0.8 + 0.25*1.0 + 0.20*1.0 + 0.10*1.0 + 0.10*0.0))
         = round(100 * 0.73)
         = 73

**Result**: High risk (73/100)

## Future Enhancements

- Integration with SBOM for dependency analysis
- Machine learning-based risk assessment
- Industry-specific scoring adjustments
- Historical trend analysis
- Compliance mapping (PCI-DSS, HIPAA, etc.)

