from fastapi import APIRouter, File, UploadFile 
from app.controller.upload_controller import uploadFile
from app.models.ticket_model import Ticket_model

upload_route = APIRouter(
    prefix="/upload",
    tags= ["Upload file"]
)

@upload_route.post("/upload")
async def upload_file(fileName:str,file:UploadFile = File(...)):
    return await uploadFile(file,fileName)