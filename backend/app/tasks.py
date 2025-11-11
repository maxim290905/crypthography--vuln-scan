import json
import os
from datetime import datetime
from sqlalchemy.orm import Session
from app.celery_app import celery_app
from app.database import SessionLocal
from app.models import Scan, Finding, ScanStatus
from app.scanner import Scanner
from app.pq_score import calculate_pq_score
from app.config import settings


@celery_app.task(bind=True, name="scan_task")
def scan_task(self, scan_id: int):
    """Celery task to perform scan"""
    db: Session = SessionLocal()
    
    try:
        # Get scan record
        scan = db.query(Scan).filter(Scan.id == scan_id).first()
        if not scan:
            raise ValueError(f"Scan {scan_id} not found")
        
        # Update status to running
        scan.status = ScanStatus.RUNNING
        scan.started_at = datetime.utcnow()
        db.commit()
        
        # Run scanner
        scanner = Scanner(target=scan.target, timeout=settings.SCAN_TIMEOUT_SECONDS)
        scan_results = scanner.scan()
        
        # Save raw JSON
        os.makedirs(f"{settings.STORAGE_PATH}/scans", exist_ok=True)
        raw_json_path = f"{settings.STORAGE_PATH}/scans/{scan_id}_raw.json"
        with open(raw_json_path, "w") as f:
            json.dump(scan_results, f, indent=2)
        
        # Create findings
        findings_objects = []
        for finding_data in scan_results["findings"]:
            finding = Finding(
                scan_id=scan_id,
                asset_type=finding_data["asset_type"],
                detail_json=finding_data["detail_json"],
                severity=finding_data["severity"],
                category=finding_data["category"],
                evidence=finding_data.get("evidence")
            )
            findings_objects.append(finding)
            db.add(finding)
        
        db.commit()
        
        # Calculate PQ score
        pq_score, pq_level = calculate_pq_score(findings_objects)
        
        # Update scan with results
        scan.status = ScanStatus.DONE
        scan.finished_at = datetime.utcnow()
        scan.pq_score = pq_score
        scan.raw_json_path = raw_json_path
        
        db.commit()
        
        # Generate PDF report (async, can be done separately)
        # For now, we'll generate it on-demand via API
        
        return {
            "scan_id": scan_id,
            "status": "done",
            "pq_score": pq_score,
            "findings_count": len(findings_objects)
        }
        
    except Exception as e:
        # Update scan status to failed
        if scan:
            scan.status = ScanStatus.FAILED
            scan.error_message = str(e)
            scan.finished_at = datetime.utcnow()
            db.commit()
        
        # Re-raise for Celery retry
        raise self.retry(exc=e, countdown=60, max_retries=1)
    
    finally:
        db.close()

