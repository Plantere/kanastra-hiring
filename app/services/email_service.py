from app.core.logger import Logger
from app.services.task_service import TaskService
from app.services.debts_service import DebtsService

class EmailService():
    def __init__(self):
        self.task_service = TaskService()
        self.debts_service = DebtsService()
        self.logger = Logger()

    def send_email(self, recipient_email, subject, body, invoice, debt_id, task_id):
        email_content = f"""
            To: {recipient_email}
            Subject: {subject}

            {body}

            Attached Invoice Code:
            {invoice}
        """

        self.task_service.update_task(task_id, update_query = {"$inc": {"sended": 1, "pending": -1}})
        self.logger.create_message(email_content, "INFO", debt_id, task_id)
        self.debts_service.update_debt(debt_id=debt_id, task_id=task_id, update_fields = {"sended": True})
