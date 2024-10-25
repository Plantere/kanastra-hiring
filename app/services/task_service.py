from app.core.database import MongoDBConnection
from datetime import datetime
from app.interfaces.services.task_service_interface import ITaskService
import uuid

class TaskService(ITaskService):
    def __init__(self):
        connection = MongoDBConnection()
        self.db = connection.get_database().tasks

    def create_task(self, filename, file_path):
        task_id = str(uuid.uuid4())

        self.db.insert_one({
            "taskId": task_id,
            "total": 0,
            "invoice_generated": 0,
            "pending": 0,
            "sended": 0,
            "duplicated": 0,
            "fileName": filename,
            "filePath": file_path,
            "createdAt": datetime.now(),
            "updatedAt": datetime.now(),
        })

        return task_id
    
    def update_task(self, task_id, update_fields = {}, update_query = {}):
        self.db.update_one(
            {"taskId": task_id},
            {
                "$set": {
                    **update_fields,
                    "updatedAt": datetime.now()
                },
                **update_query
            }
        )

    @classmethod
    def get_instance(cls) -> ITaskService:
        return cls()