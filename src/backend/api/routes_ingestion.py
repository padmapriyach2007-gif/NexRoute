"""
Data Ingestion API Router
"""

from typing import Any, Dict, List
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.backend.database.connection import get_db
from src.backend.auth.security import require_role
from src.backend.ingestion.data_ingestion import DataIngestionEngine

router = APIRouter(prefix="/ingestion", tags=["Data Ingestion & Digital Twin"])


class IngestPOIDatasetRequest(BaseModel):
    provider_name: str = "OPEN_STREET_MAP"
    records: List[Dict[str, Any]]


@router.post("/poi-dataset")
def ingest_poi_dataset(
    req: IngestPOIDatasetRequest,
    db: Session = Depends(get_db)
):
    job = DataIngestionEngine.ingest_poi_dataset(
        db, req.records, provider_name=req.provider_name
    )
    return {
        "job_id": job.id,
        "status": job.status,
        "records_ingested": job.records_ingested,
        "records_updated": job.records_updated,
        "records_failed": job.records_failed
    }
