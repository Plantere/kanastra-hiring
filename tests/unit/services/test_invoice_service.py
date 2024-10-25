import pytest
from unittest.mock import MagicMock
from app.services.invoice_service import InvoiceService

@pytest.fixture
def mock_logger():
    return MagicMock()

@pytest.fixture
def invoice_service(mock_logger, monkeypatch):
    def mock_init(self):
        self.logger = mock_logger
        self.task_service = mock_logger
    
    monkeypatch.setattr('app.services.invoice_service.InvoiceService.__init__', mock_init)
    
    return InvoiceService()

def test_generate_invoice_creates_log_and_returns_invoice_id(invoice_service, mock_logger):
    debt_id = "123456"
    amount = 150.75
    due_date = "2024-10-31"
    debtor = "John Doe"
    task_id = "task-test-id"
    
    invoice_id = invoice_service.generate_invoice(debt_id, amount, due_date, debtor, task_id)
    
    assert mock_logger.create_message.call_count == 1
    
    mock_logger.create_message.assert_called_with(
        f"Invoice generated for {debtor} with amount {amount} due {due_date}", 
        "INFO", 
        debt_id,
        task_id
    )
    
    parts = invoice_id.split('_')
    assert parts[0] == debt_id
    assert len(parts) == 3
    assert float(parts[2]) == amount
