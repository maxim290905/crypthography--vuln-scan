from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models import ScanStatus, Severity, UserRole


# Auth schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str
    role: UserRole = UserRole.USER


class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    role: UserRole
    
    model_config = {"from_attributes": True}


# Project schemas
class ProjectCreate(BaseModel):
    name: str


class ProjectResponse(BaseModel):
    id: int
    name: str
    owner_id: int
    created_at: datetime
    
    model_config = {"from_attributes": True}


# Scan schemas
class ScanCreate(BaseModel):
    target: str
    project_id: int
    scan_type: str = "tls_network"
    notes: Optional[str] = None


class ScanResponse(BaseModel):
    id: int
    project_id: int
    target: str
    scan_type: str
    status: ScanStatus
    pq_score: Optional[float] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    
    model_config = {"from_attributes": True}


class ScanStatusResponse(BaseModel):
    id: int
    target: str
    status: ScanStatus
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    error_message: Optional[str] = None


class FindingResponse(BaseModel):
    id: int
    asset_type: str
    detail_json: Dict[str, Any]
    severity: Severity
    category: str
    evidence: Optional[str] = None


class ScanResultResponse(BaseModel):
    scan: ScanResponse
    findings: List[FindingResponse]
    pq_score: Optional[float] = None
    pq_level: Optional[str] = None  # Low, Medium, High, Critical
    summary: Dict[str, Any]


# Asset schemas
class AssetResponse(BaseModel):
    target: str
    scan_id: int
    pq_score: Optional[float] = None
    status: ScanStatus
    last_scan: datetime
    findings_count: int

