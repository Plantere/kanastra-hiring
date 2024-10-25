from app.tasks.csv_tasks import process_csv, process_chunk, handle_duplicates
from io import StringIO
from unittest.mock import patch

@patch('app.tasks.csv_tasks.logger')
@patch('app.tasks.csv_tasks.TaskService')
def test_process_csv_creates_and_process_chunks(mock_task_service, mock_logger, mocker):
    csv_content = StringIO(
        'debtId,name,governmentId,email,debtAmount,debtDueDate\n'
        '1,John Doe,123456789,test@example.com,100.0,2024-10-31\n'
    )
    mocker.patch('app.tasks.csv_tasks.open', return_value=csv_content)
    
    mock_task_service_instance = mock_task_service.return_value
    mock_process_chunk = mocker.patch('app.tasks.csv_tasks.process_chunk.delay')

    process_csv("/kanastra-file-processor/app/storage/uploads/file.csv", "test-task-id")
    
    mock_task_service_instance.update_task.assert_called_once_with("test-task-id", update_query={"$inc": {"total": 1, "pending": 1}})

    mock_process_chunk.assert_called_once_with(
        [{'debtId': '1', 'name': 'John Doe', 'governmentId': '123456789', 'email': 'test@example.com', 'debtAmount': '100.0', 'debtDueDate': '2024-10-31'}],
        "test-task-id"
    )

@patch('app.tasks.csv_tasks.logger')
@patch('app.tasks.csv_tasks.DebtsService')
def test_process_chunk_creates_and_handles_duplicates(mock_debts_service, mock_logger, mocker):
    chunk = [
        {'debtId': '1', 'name': 'John Doe', 'governmentId': '123456789', 'email': 'test@example.com', 'debtAmount': '100.0', 'debtDueDate': '2024-10-31'},
        {'debtId': '2', 'name': 'Jane Doe', 'governmentId': '987654321', 'email': 'jane@example.com', 'debtAmount': '200.0', 'debtDueDate': '2024-11-01'}
    ]

    mock_debts_service_instance = mock_debts_service.return_value
    mock_debts_service_instance.find_by_debt_ids.return_value = [{'debtId': '1'}]

    mock_process_sub_chunks = mocker.patch('app.tasks.csv_tasks.process_sub_chunks')
    mock_handle_duplicates = mocker.patch('app.tasks.csv_tasks.handle_duplicates.delay')

    process_chunk(chunk, "test-task-id")

    mock_debts_service_instance.create_debts.assert_called_once_with([{'debtId': '2', 'name': 'Jane Doe', 'governmentId': '987654321', 'email': 'jane@example.com', 'debtAmount': '200.0', 'debtDueDate': '2024-11-01'}], "test-task-id")

    mock_process_sub_chunks.assert_called_once_with([{'debtId': '2', 'name': 'Jane Doe', 'governmentId': '987654321', 'email': 'jane@example.com', 'debtAmount': '200.0', 'debtDueDate': '2024-11-01'}], "test-task-id")

    mock_handle_duplicates.assert_called_once_with([{'debtId': '1', 'name': 'John Doe', 'governmentId': '123456789', 'email': 'test@example.com', 'debtAmount': '100.0', 'debtDueDate': '2024-10-31'}], "test-task-id")

@patch('app.tasks.csv_tasks.logger')
def test_handle_duplicates_logs_duplicates(mock_logger, mocker):
    duplicate_debts = [
        {'debtId': '1', 'name': 'John Doe', 'governmentId': '123456789', 'email': 'test@example.com', 'debtAmount': '100.0', 'debtDueDate': '2024-10-31'}
    ]

    handle_duplicates(duplicate_debts, "test-task-id")

    mock_logger.create_message.assert_called_once_with(
        "Duplicated debt detected:\n"
        "  - Name: John Doe\n"
        "  - Government ID: 123456789\n"
        "  - Email: test@example.com\n"
        "  - Debt Amount: 100.0\n"
        "  - Debt Due Date: 2024-10-31\n"
        "  - Debt ID: 1\n"
        "--------------------------------------", 
        "INFO", 
        "1",
        "test-task-id"
    )
