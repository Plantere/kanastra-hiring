import pytest
from unittest.mock import patch, MagicMock
from app.services.debts_service import DebtsService
from datetime import datetime

@pytest.fixture
def mock_db():
    with patch('app.services.debts_service.MongoDBConnection') as MockMongoConnection:
        mock_connection_instance = MockMongoConnection.return_value
        mock_db = MagicMock()
        mock_connection_instance.get_database.return_value.debts = mock_db
        yield mock_db

@pytest.fixture
def debts_service():
    return DebtsService()

def test_create_debts(mock_db, debts_service):
    sample_debts = [
        {"debtId": "123", "name": "John Doe", "amount": 100, "sended": False},
        {"debtId": "456", "name": "Jane Doe", "amount": 200, "sended": False}
    ]

    mock_insert_result = MagicMock()
    mock_db.insert_many.return_value = mock_insert_result

    task_id = "task_test_id"
    
    fixed_datetime = datetime(2024, 10, 25, 1, 41, 31, 499910)
    
    with patch('app.services.debts_service.datetime') as mock_datetime:
        mock_datetime.now.return_value = fixed_datetime
        
        result = debts_service.create_debts(sample_debts, task_id)

        expected_debts = [
            {**debt, "createdAt": fixed_datetime} for debt in sample_debts
        ]

        assert result == mock_insert_result

def test_find_by_debt_ids(mock_db, debts_service):
    sample_debt_ids = ["123", "456"]

    mock_cursor = MagicMock()
    mock_db.find.return_value = mock_cursor

    result = debts_service.find_by_debt_ids(sample_debt_ids)
    
    mock_db.find.assert_called_once_with({"debtId": {"$in": sample_debt_ids}})
    assert result == mock_cursor

def test_update_debt(mock_db, debts_service):
    mock_update_result = MagicMock()
    mock_db.update_one.return_value = mock_update_result

    debt_id = "123"
    task_id = None
    update_fields = {"status": "paid"}
    update_query = {"$inc": {"amountPaid": 100}}

    result = debts_service.update_debt(debt_id=debt_id, update_fields=update_fields, update_query=update_query)

    mock_db.update_one.assert_called_once_with(
        {"debtId": debt_id},
        {
            "$set": {
                **update_fields,
                "updatedAt": mock_db.update_one.call_args[0][1]["$set"]["updatedAt"]
            },
            **update_query
        }
    )

    assert result == mock_update_result