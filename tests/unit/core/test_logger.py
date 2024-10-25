import pytest
from unittest.mock import patch, MagicMock
from app.core.logger import Logger
from datetime import datetime, timezone

@pytest.fixture
def mock_db():
    with patch('app.core.logger.MongoDBConnection') as MockMongoConnection:
        mock_connection_instance = MockMongoConnection.return_value
        mock_db = MagicMock()
        mock_connection_instance.get_database.return_value.logs = mock_db
        yield mock_db

def test_create_message(mock_db):
    logger = Logger()

    sample_message = "Test log message"
    sample_type = "INFO"
    sample_info = "test_id"

    logger.create_message(sample_message, sample_type, sample_info)

    expected_log_entry = {
        "message": sample_message,
        "type": sample_type,
        "timestamp": datetime.now(timezone.utc),
        "additional_information": sample_info
    }
    
    assert mock_db.insert_one.call_count == 1
    actual_call_args = mock_db.insert_one.call_args[0][0]
    
    assert actual_call_args["message"] == expected_log_entry["message"]
    assert actual_call_args["type"] == expected_log_entry["type"]
    assert actual_call_args["additional_information"] == expected_log_entry["additional_information"]
    assert isinstance(actual_call_args["timestamp"], datetime)

def test_get_log_by_message(mock_db):
    logger = Logger()
    
    sample_message = "Test log message"
    
    logger.get_log_by_message(sample_message)
    mock_db.find.assert_called_once_with({"message": sample_message})

def test_clear_all_logs(mock_db):
    logger = Logger()
    
    logger.clear_all_logs()
    mock_db.delete_many.assert_called_once_with({})
