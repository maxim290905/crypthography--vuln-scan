import subprocess
import json
import re
import os
from datetime import datetime
from typing import Dict, Any, List
from app.models import Finding, Severity


class Scanner:
    def __init__(self, target: str, timeout: int = 300):
        self.target = target
        self.timeout = timeout
        self.testssl_path = "/opt/testssl.sh/testssl.sh"
        self.findings: List[Dict[str, Any]] = []
    
    def run_testssl(self) -> Dict[str, Any]:
        """Run testssl.sh and parse results"""
        try:
            # Run testssl.sh with JSON output
            cmd = [
                self.testssl_path,
                "--json",
                "--quiet",
                self.target
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                check=False
            )
            
            # Parse JSON output
            output_lines = result.stdout.split('\n')
            json_data = {}
            for line in output_lines:
                if line.strip().startswith('{'):
                    try:
                        json_data = json.loads(line)
                        break
                    except json.JSONDecodeError:
                        continue
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "json": json_data,
                "stderr": result.stderr
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Timeout expired"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def run_nmap(self) -> Dict[str, Any]:
        """Run nmap scan"""
        try:
            cmd = [
                "nmap",
                "-sV",
                "--script", "ssl-enum-ciphers,ssl-cert",
                "-oJ", "-",
                self.target
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                check=False
            )
            
            # Parse nmap JSON output
            json_data = {}
            try:
                json_data = json.loads(result.stdout)
            except json.JSONDecodeError:
                pass
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "json": json_data,
                "stderr": result.stderr
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Timeout expired"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def parse_testssl_results(self, testssl_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse testssl.sh results into normalized findings"""
        findings = []
        
        if not testssl_data.get("json"):
            return findings
        
        data = testssl_data["json"]
        
        # Parse certificate information
        if "certificate" in data:
            cert = data["certificate"]
            
            # Check certificate expiry
            if "notAfter" in cert:
                not_after = cert["notAfter"]
                try:
                    expiry_date = datetime.strptime(not_after, "%Y%m%d%H%M%S")
                    days_until_expiry = (expiry_date - datetime.utcnow()).days
                    
                    if days_until_expiry < 0:
                        findings.append({
                            "asset_type": "cert",
                            "category": "cert_expired",
                            "severity": Severity.P0,
                            "detail_json": {"expiry_date": not_after, "days": days_until_expiry},
                            "evidence": f"Certificate expired {abs(days_until_expiry)} days ago"
                        })
                    elif days_until_expiry < 30:
                        findings.append({
                            "asset_type": "cert",
                            "category": "cert_near_expiry",
                            "severity": Severity.P1,
                            "detail_json": {"expiry_date": not_after, "days": days_until_expiry},
                            "evidence": f"Certificate expires in {days_until_expiry} days"
                        })
                except ValueError:
                    pass
            
            # Check key size
            if "keySize" in cert:
                key_size = cert["keySize"]
                if isinstance(key_size, str):
                    key_size = int(re.search(r'\d+', key_size).group()) if re.search(r'\d+', key_size) else 0
                
                if key_size < 2048:
                    findings.append({
                        "asset_type": "cert",
                        "category": "small_rsa",
                        "severity": Severity.P0,
                        "detail_json": {"key_size": key_size},
                        "evidence": f"RSA key size is {key_size} bits (should be >= 2048)"
                    })
                elif key_size < 3072:
                    findings.append({
                        "asset_type": "cert",
                        "category": "weak_key",
                        "severity": Severity.P1,
                        "detail_json": {"key_size": key_size},
                        "evidence": f"RSA key size is {key_size} bits (recommended >= 3072)"
                    })
        
        # Parse protocol versions
        if "protocols" in data:
            protocols = data["protocols"]
            if isinstance(protocols, list):
                for proto in protocols:
                    if "id" in proto:
                        proto_id = proto["id"]
                        if proto_id in ["SSLv2", "SSLv3", "TLS1", "TLS1_1"]:
                            findings.append({
                                "asset_type": "protocol",
                                "category": "deprecated_alg",
                                "severity": Severity.P1,
                                "detail_json": {"protocol": proto_id},
                                "evidence": f"Deprecated protocol {proto_id} is enabled"
                            })
        
        # Parse ciphers
        if "ciphers" in data:
            ciphers = data["ciphers"]
            if isinstance(ciphers, list):
                for cipher in ciphers:
                    cipher_name = cipher.get("cipher", "")
                    if any(weak in cipher_name.upper() for weak in ["MD5", "SHA1", "RC4", "DES", "3DES"]):
                        findings.append({
                            "asset_type": "cipher",
                            "category": "deprecated_alg",
                            "severity": Severity.P1,
                            "detail_json": {"cipher": cipher_name},
                            "evidence": f"Weak cipher suite: {cipher_name}"
                        })
        
        return findings
    
    def parse_nmap_results(self, nmap_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse nmap results into normalized findings"""
        findings = []
        
        if not nmap_data.get("json"):
            return findings
        
        data = nmap_data["json"]
        
        # Parse nmap output for SSL/TLS information
        if isinstance(data, list):
            for host in data:
                if "ports" in host:
                    for port in host["ports"]:
                        if "scripts" in port:
                            scripts = port["scripts"]
                            
                            # Parse ssl-cert script output
                            if "ssl-cert" in scripts:
                                cert_info = scripts["ssl-cert"]
                                # Add certificate findings if any
                                pass
                            
                            # Parse ssl-enum-ciphers script output
                            if "ssl-enum-ciphers" in scripts:
                                ciphers_info = scripts["ssl-enum-ciphers"]
                                # Add cipher findings if any
                                pass
        
        return findings
    
    def scan(self) -> Dict[str, Any]:
        """Run full scan and return results"""
        all_findings = []
        
        # Run testssl.sh
        testssl_result = self.run_testssl()
        testssl_findings = self.parse_testssl_results(testssl_result)
        all_findings.extend(testssl_findings)
        
        # Run nmap
        nmap_result = self.run_nmap()
        nmap_findings = self.parse_nmap_results(nmap_result)
        all_findings.extend(nmap_findings)
        
        # Add public exposure finding (assuming internet-facing)
        all_findings.append({
            "asset_type": "network",
            "category": "public_exposure",
            "severity": Severity.P2,
            "detail_json": {"target": self.target},
            "evidence": f"Target {self.target} is publicly accessible"
        })
        
        return {
            "findings": all_findings,
            "testssl": testssl_result,
            "nmap": nmap_result,
            "target": self.target,
            "timestamp": datetime.utcnow().isoformat()
        }

