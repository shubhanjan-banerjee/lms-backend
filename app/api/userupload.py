from fastapi import APIRouter, UploadFile, File, Depends
from fastapi.responses import JSONResponse
import logging
import tempfile
import shutil
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.developer_processing import process_employees_excel_and_insert

router = APIRouter(prefix="/admin/userupload", tags=["admin-userupload"])

@router.post("/")
def upload_users(file: UploadFile = File(...), db: Session = Depends(get_db)):
    logger = logging.getLogger("uvicorn.error")
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name
        summary = process_employees_excel_and_insert(tmp_path, db)
        if isinstance(summary, dict) and summary.get("error"):
            logger.error(f"Excel processing error: {summary['error']}")
            return JSONResponse(status_code=400, content={"error": summary["error"]})
        return {"summary": summary}
    except Exception as e:
        logger.exception(f"File upload failed: {str(e)}")
        return JSONResponse(status_code=500, content={"error": str(e)})
