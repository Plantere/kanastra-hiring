from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from app.tasks.csv_tasks import process_csv

from app.services.task_service import TaskService
from app.services.file_service import FileService

from app.interfaces.services.file_service_interface import IFileService
from app.interfaces.services.task_service_interface import ITaskService

router = APIRouter()

@router.post("/billing/upload")
async def upload_debts(
    file: UploadFile = File(...),
    file_service: IFileService = Depends(FileService.get_instance), 
    task_service: ITaskService = Depends(TaskService.get_instance)
):
    
    filename = file.filename
    
    if not file_service.is_csv_file(filename):
        raise HTTPException(status_code=400, detail="The uploaded file is not in CSV format. Please upload a file with the .csv extension.")

    filepath = file_service.save_file(file)

    task_id = task_service.create_task(filename, filepath)

    process_csv.delay(filepath, task_id)

    return {
        "status": "CSV file uploaded successfully for processing", 
        "filename": filename, 
        "task_id": task_id
    }

