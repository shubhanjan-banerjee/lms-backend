from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
import logging
import tempfile
import shutil
from app.services.developer_processing import process_developers_excel

router = APIRouter(prefix="/admin/userupload", tags=["admin-userupload"])

@router.post("/")
def upload_users(file: UploadFile = File(...)):
    logger = logging.getLogger("uvicorn.error")
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name
        users = process_developers_excel(tmp_path)
        if isinstance(users, list) and users and isinstance(users[0], dict) and users[0].get("error"):
            logger.error(f"Excel processing error: {users[0]['error']}")
            return JSONResponse(status_code=400, content={"error": users[0]["error"]})
        return users
    except Exception as e:
        logger.exception(f"File upload failed: {str(e)}")
        return JSONResponse(status_code=500, content={"error": str(e)})
