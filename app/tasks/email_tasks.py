from app.core.celery_app import celery_app
from app.core.logger import Logger
from app.services.email_service import EmailService

@celery_app.task(bind=True)
def send_email_task(self, invoices, task_id):
    email_service = EmailService()
    logger = Logger()

    for invoice, details in invoices:
        try:
            email_service.send_email(details["email"], "Invoice Arrived", "Dear Customer, your invoice has arrived.", invoice, details["debtId"], task_id)
            logger.create_message(f"Email successfully sent to {details['email']} for Debt ID: {details['debtId']}", "INFO", details["debtId"], task_id)
        except Exception as e:
            logger.create_message(f"Failed to send email to {details['email']} for Debt ID: {details['debtId']} - {str(e)}", "ERROR", details["debtId"], task_id)
            raise self.retry(exc=e)
