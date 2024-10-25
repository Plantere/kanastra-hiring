from app.core.database import MongoDBConnection
from datetime import datetime

class DebtsService():
    def __init__(self):
        connection = MongoDBConnection()
        self.db = connection.get_database().debts

    def create_debts(self, debts, task_id):
        debts = [
            {**debt, "taskId": task_id, "sended": False, "createdAt": datetime.now()} for debt in debts
        ]

        return self.db.insert_many(debts)
    
    def find_by_debt_ids(self, debt_ids):
        return self.db.find({"debtId": {"$in": debt_ids}})
    
    def update_debt(self, debt_id = None, task_id = None, update_fields = {}, update_query = {}):
        filter = {}

        if debt_id is not None:
            filter["debtId"] = debt_id

        if task_id is not None:
            filter["taskId"] = task_id


        return self.db.update_one(
            filter,
            {
                "$set": {
                    **update_fields,
                    "updatedAt": datetime.now()
                },
                **update_query
            }
        )