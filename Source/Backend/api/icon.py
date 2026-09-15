from fastapi import APIRouter
from fastapi.responses import FileResponse

router = APIRouter()

@router.get("/favicon.ico")
def getIcon():
    return FileResponse("Backend/static/favicon.ico")