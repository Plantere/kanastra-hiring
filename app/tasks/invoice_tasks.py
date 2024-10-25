from app.core.celery_app import celery_app
from app.services.invoice_service import InvoiceService
from app.tasks.email_tasks import send_email_task

@celery_app.task(bind=True)
def generate_invoice_task(self, debt_details, task_id):
    invoices = []
    
    invoice_service = InvoiceService()

    for row in debt_details:
        try:
            invoice = invoice_service.generate_invoice(row['debtId'], row['debtAmount'], row['debtDueDate'], row['name'], task_id)
            invoices.append([invoice, row])
        except Exception as e:
            raise self.retry(exc=Exception(f"Failed to generate invoice for debt ID {row['debtId']}: {str(e)}"))

    try:
        send_email_task.delay(invoices, task_id)
    except Exception as e:
        raise self.retry(exc=e)
