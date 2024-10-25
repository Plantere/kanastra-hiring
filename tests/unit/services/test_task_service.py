import pytest
from unittest.mock import MagicMock
from datetime import datetime
from app.services.task_service import TaskService

@pytest.fixture
def mock_db():
    return MagicMock()

@pytest.fixture
def mock_datetime():
    current_time = datetime.now()
    mock_datetime = MagicMock(wraps=datetime)
    mock_datetime.now.return_value = current_time
    return mock_datetime, current_time

@pytest.fixture
def task_service(mock_db, monkeypatch, mock_datetime):
    def mock_db_init(self):
        self.db = mock_db
    
    monkeypatch.setattr('app.services.task_service.TaskService.__init__', mock_db_init)
    monkeypatch.setattr('app.services.task_service.datetime', mock_datetime[0])
    
    return TaskService()

def test_create_task_inserts_correct_data(task_service, mock_db, mock_datetime):
    filename = "example.txt"
    file_path = "/files/example.txt"
    
    _, current_time = mock_datetime

    task_id = task_service.create_task(filename, file_path)

    assert mock_db.insert_one.call_count == 1
    
    insert_data = mock_db.insert_one.call_args[0][0]
    
    assert insert_data["fileName"] == filename
    assert insert_data["filePath"] == file_path
    assert insert_data["taskId"] == task_id
    assert insert_data["createdAt"] == current_time
    assert insert_data["updatedAt"] == current_time

def test_update_task_updates_correct_data(task_service, mock_db, mock_datetime):
    task_id = "test-task-id"
    update_fields = {
        "total": 10
    }
    
    _, current_time = mock_datetime

    task_service.update_task(task_id, update_fields)

    assert mock_db.update_one.call_count == 1
    
    filter_query, update_query = mock_db.update_one.call_args[0]
    
    assert filter_query == {"taskId": task_id}
    assert update_query["$set"]["total"] == 10
    assert update_query["$set"]["updatedAt"] == current_time
