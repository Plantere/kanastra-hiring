import pytest
from app.core.celery_app import celery_app
from fastapi.testclient import TestClient
from app.main import app
from app.services.task_service import TaskService
from app.services.debts_service import DebtsService
from app.tasks.csv_tasks import process_csv
from app.core.logger import Logger
from unittest.mock import patch
import time

client = TestClient(app)

def is_celery_busy(celery_inspect):
    return (
        check_non_empty(celery_inspect.scheduled()) or 
        check_non_empty(celery_inspect.active()) or 
        check_non_empty(celery_inspect.reserved())
    )

def wait_for_celery_completion(timeout=10, interval=1):
    start_time = time.time()
    celery_inspect = celery_app.control.inspect()
    
    while is_celery_busy(celery_inspect):
        if time.time() - start_time > timeout:
            return False
        time.sleep(interval)
    return True

def check_non_empty(status_dict):
    if status_dict is None:
        return False
    
    return any(len(tasks) > 0 for tasks in status_dict.values())

@pytest.fixture(scope="module")
def setup_integration_test_environment():
    task_service = TaskService.get_instance()
    debt_service = DebtsService()
    logger = Logger()

    task_service.db.delete_many({})
    debt_service.db.delete_many({})
    logger.clear_all_logs()

    yield

    task_service.db.delete_many({})
    debt_service.db.delete_many({})
    logger.clear_all_logs()

@patch('app.tasks.csv_tasks.process_chunk.delay')
def test_upload_debts_csv_initial(mock_process_chunk_delay, setup_integration_test_environment):
    csv_content = "name,governmentId,email,debtAmount,debtDueDate,debtId\nJohn Doe,123456789,johndoe@example.com,500.0,2024-12-31,abc123\n"
    test_file = {
        "file": ("test.csv", csv_content, "text/csv")
    }

    response = client.post("/api/v1/billing/upload", files=test_file)

    assert response.status_code == 200
    assert response.json()["status"] == "CSV file uploaded successfully for processing"
    assert response.json()["filename"] == "test.csv"
    assert "task_id" in response.json()

    task_id = response.json()["task_id"]
    task_service = TaskService.get_instance()
    task = task_service.db.find_one({"taskId": task_id})

    assert task is not None
    assert task["fileName"] == "test.csv"
    assert task["filePath"] == "/kanastra-file-processor/app/storage/uploads/test.csv"

    file_path = "/kanastra-file-processor/app/storage/uploads/test.csv"
    with open(file_path, "w") as f:
        f.write(csv_content)

    process_csv(file_path, task_id)

    assert wait_for_celery_completion(), "Celery tasks did not complete in the expected time."

    task = task_service.db.find_one({"taskId": task_id})

    assert task is not None
    assert task["fileName"] == "test.csv"
    assert task["filePath"] == task["filePath"]

    debts_service = DebtsService()
    debt = debts_service.db.find_one({"debtId": "abc123"})
    assert debt is not None
    assert debt["name"] == "John Doe"
    assert debt["governmentId"] == "123456789"
    assert debt["email"] == "johndoe@example.com"
    assert debt["debtAmount"] == "500.0"
    assert debt["debtDueDate"] == "2024-12-31"
    assert debt["debtId"] == "abc123"

    logger = Logger()
    assert len(list(logger.get_log_by_message("Email successfully sent to johndoe@example.com for Debt ID: abc123"))) == 1
    assert len(list(logger.get_log_by_message("Invoice generated for John Doe with amount 500.0 due 2024-12-31"))) == 1
    assert len(list(logger.get_log_by_message("Duplicated debt detected:\n  - Name: John Doe\n  - Government ID: 123456789\n  - Email: johndoe@example.com\n  - Debt Amount: 500.0\n  - Debt Due Date: 2024-12-31\n  - Debt ID: abc123\n--------------------------------------"))) == 0

@patch('app.tasks.csv_tasks.process_chunk.delay')
def test_upload_debts_csv_duplicate(mock_process_chunk_delay, setup_integration_test_environment):
    csv_content = "name,governmentId,email,debtAmount,debtDueDate,debtId\nJohn Doe,123456789,johndoe@example.com,500.0,2024-12-31,abc123\n"
    test_file = {
        "file": ("test.csv", csv_content, "text/csv")
    }

    response = client.post("/api/v1/billing/upload", files=test_file)

    assert response.status_code == 200
    assert "task_id" in response.json()

    task_id = response.json()["task_id"]
    task_service = TaskService.get_instance()
    task = task_service.db.find_one({"taskId": task_id})

    assert task is not None
    assert task["fileName"] == "test.csv"

    process_csv("/kanastra-file-processor/app/storage/uploads/test.csv", task_id)

    assert wait_for_celery_completion(), "Celery tasks did not complete in the expected time."

    debts_service = DebtsService()
    debts = debts_service.db.find({"debtId": "abc123"})
    assert len(list(debts)) == 1

    logger = Logger()
    assert len(list(logger.get_log_by_message("Duplicated debt detected:\n  - Name: John Doe\n  - Government ID: 123456789\n  - Email: johndoe@example.com\n  - Debt Amount: 500.0\n  - Debt Due Date: 2024-12-31\n  - Debt ID: abc123\n--------------------------------------"))) == 1