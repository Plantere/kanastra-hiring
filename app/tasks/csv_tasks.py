from app.core.celery_app import celery_app 
from itertools import islice
from app.services.task_service import TaskService
from app.tasks.invoice_tasks import generate_invoice_task
from copy import deepcopy
from app.core.logger import Logger
from app.services.debts_service import DebtsService
import csv

logger = Logger()

sub_chunk_size = 500

def split_into_chunks(data, chunk_size):
    return [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]


@celery_app.task(bind=True)
def process_csv(self, file_location, task_id):
    task_service = TaskService()

    try:
        with open(file_location, mode="r", encoding="utf-8") as f:
            content = csv.DictReader(f)

            while True:
                chunk = list(islice(content, 10000))
                if not chunk:
                    break
                
                total_rows = len(chunk)
                task_service.update_task(task_id, update_query = {"$inc": {"total": total_rows, "pending": total_rows}})

                process_chunk.delay(chunk, task_id)
    except Exception as e:
        raise e

@celery_app.task(bind=True)
def process_chunk(self, chunk, task_id):
    debt_ids = [row['debtId'] for row in chunk]

    debts_service = DebtsService()

    existing_debts = {debt['debtId'] for debt in debts_service.find_by_debt_ids(debt_ids)}

    new_entries = [row for row in chunk if row['debtId'] not in existing_debts]

    if new_entries:
        debts_service.create_debts(deepcopy(new_entries), task_id)
        process_sub_chunks(new_entries, task_id)

    duplicate_entries = [row for row in chunk if row['debtId'] in existing_debts]

    if duplicate_entries:
        handle_duplicates.delay(duplicate_entries, task_id)


def process_sub_chunks(data, task_id):
    chunks = split_into_chunks(data, sub_chunk_size)

    for sub_chunk in chunks:
        generate_invoice_task.delay(sub_chunk, task_id)


@celery_app.task(bind=True)
def handle_duplicates(self, duplicate_debts, task_id):
    task_service = TaskService()

    for item in duplicate_debts:
        logger.create_message(
           f"Duplicated debt detected:\n"
            f"  - Name: {item['name']}\n"
            f"  - Government ID: {item['governmentId']}\n"
            f"  - Email: {item['email']}\n"
            f"  - Debt Amount: {item['debtAmount']}\n"
            f"  - Debt Due Date: {item['debtDueDate']}\n"
            f"  - Debt ID: {item['debtId']}\n"
            f"--------------------------------------", "INFO", item['debtId'], task_id
        )

        task_service.update_task(task_id, update_query = {"$inc": {"duplicated": 1}})


