"""
Offline Map Package API Router
"""

from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.backend.database.connection import get_db
from src.backend.offline.package_service import OfflinePackageService

router = APIRouter(prefix="/offline", tags=["Offline-First Map Support"])


@router.get("/packages")
def list_offline_packages(db: Session = Depends(get_db)):
    packages = OfflinePackageService.list_available_packages(db)
    return {"packages_count": len(packages), "packages": packages}


@router.get("/packages/{package_id}/download")
def download_offline_package(package_id: str, db: Session = Depends(get_db)):
    try:
        payload = OfflinePackageService.generate_package_payload(db, package_id)
        return payload
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
