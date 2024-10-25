import pytest
from app.services.file_service import FileService
from unittest.mock import MagicMock, mock_open

@pytest.fixture
def file_service():
    return FileService()

@pytest.fixture
def mock_csv_file():
    return MagicMock(filename="input.csv")

def test_is_csv_file(file_service):
    assert file_service.is_csv_file("input.csv")
    assert not file_service.is_csv_file("input.txt")

def test_save_file(mocker, file_service, mock_csv_file):
    mocked_open = mocker.patch("app.services.file_service.open", mock_open(), create=True)
    
    result = file_service.save_file(mock_csv_file)
    
    assert result == "/kanastra-file-processor/app/storage/uploads/input.csv"
    mocked_open.assert_called_once_with("/kanastra-file-processor/app/storage/uploads/input.csv", "wb+")
