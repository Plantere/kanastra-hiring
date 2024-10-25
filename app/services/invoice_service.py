from app.core.logger import Logger
from app.services.task_service import TaskService
import uuid

class InvoiceService():
    def __init__(self):
        self.logger = Logger()
        self.task_service = TaskService()

    def generate_invoice(self, debt_id, amount, due_date, debtor, task_id):
        random_uuid = str(uuid.uuid4())

        self.task_service.update_task(task_id, update_query = {"$inc": {"invoice_generated": 1}})
        self.logger.create_message(f"Invoice generated for {debtor} with amount {amount} due {due_date}", "INFO", debt_id, task_id)
        
        return f"{debt_id}_{random_uuid}_{amount}"