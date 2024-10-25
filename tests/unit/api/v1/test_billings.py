import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from app.main import app
from app.services.task_service import TaskService
from app.services.file_service import FileService

client = TestClient(app)

@pytest.fixture
def client_with_overrides(mocker):
    mock_file_service = MagicMock()
    mock_file_service.is_csv_file.return_value = True
    mock_file_service.save_file.return_value = "/kanastra-file-processor/app/storage/uploads/uploaded.csv"

    mock_task_service = MagicMock()
    mock_task_service.create_task.return_value = "test-task-id"

    app.dependency_overrides[FileService.get_instance] = lambda: mock_file_service
    app.dependency_overrides[TaskService.get_instance] = lambda: mock_task_service

    mock_process_csv = mocker.patch('app.tasks.csv_tasks.process_csv.delay')

    yield client, mock_process_csv, mock_task_service, mock_file_service

    app.dependency_overrides = {}

def test_upload_debts_csv_success(client_with_overrides):
    client, mock_process_csv_delay, mock_task_service, mock_file_service = client_with_overrides

    response = client.post("api/v1/billing/upload", files={
        "file": ("test.csv", "debtId,name,email,debtAmount,debtDueDate\n1,John Doe,john@example.com,100.0,2024-10-31\n", "text/csv")
    })

    assert response.status_code == 200
    assert response.json() == {
        "status": "CSV file uploaded successfully for processing",
        "filename": "test.csv",
        "task_id": "test-task-id"
    }

    mock_process_csv_delay.assert_called_once_with("/kanastra-file-processor/app/storage/uploads/uploaded.csv", "test-task-id")
    mock_file_service.is_csv_file.assert_called_once_with("test.csv")
    mock_file_service.save_file.assert_called_once()
    mock_task_service.create_task.assert_called_once_with("test.csv", "/kanastra-file-processor/app/storage/uploads/uploaded.csv")

def test_upload_debts_not_csv(client_with_overrides):
    client, mock_process_csv, mock_task_service, mock_file_service = client_with_overrides

    mock_file_service.is_csv_file.return_value = False

    non_csv_content = "This is not a CSV Content"
    test_file = {
        "file": ("test.txt", non_csv_content, "text/plain")
    }

    response = client.post("/api/v1/billing/upload", files=test_file)

    assert response.status_code == 400
    assert response.json() == {
        "detail": "The uploaded file is not in CSV format. Please upload a file with the .csv extension."
    }

    mock_process_csv.assert_not_called()