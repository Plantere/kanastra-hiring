from app.core.database import MongoDBConnection
from datetime import datetime, timedelta, timezone

class Logger:
    def __init__(self):
        connection = MongoDBConnection()
        self.db = connection.get_database().logs

    def create_message(self, message, log_type, additional_information, task_id=None):
        log_entry = {
            "message": message,
            "type": log_type,
            "timestamp": datetime.now(timezone.utc),
            "additional_information": additional_information,
            "task_id": task_id
        }

        self.db.insert_one(log_entry)

    def get_log_by_message(self, message):
        return self.db.find({"message": message})

    def clear_all_logs(self):
        self.db.delete_many({})
