import pytest
from unittest.mock import MagicMock
from app.services.email_service import EmailService

@pytest.fixture
def mock_logger():
    return MagicMock()

@pytest.fixture
def email_service(mock_logger, monkeypatch):
    def mock_init(self):
        self.logger = mock_logger
        self.task_service = mock_logger
        self.debts_service = mock_logger
    
    monkeypatch.setattr('app.services.email_service.EmailService.__init__', mock_init)
    
    return EmailService()

def test_send_email_creates_log_entry(email_service, mock_logger):
    recipient_email = "test@example.com"
    subject = "Test Subject"
    body = "This is a test email body."
    invoice = "12345"
    debt_id = "6789"
    task_id = "task-test-id"
    
    email_service.send_email(recipient_email, subject, body, invoice, debt_id, task_id)
    
    assert mock_logger.create_message.call_count == 1
    
    expected_content = f"""
            To: {recipient_email}
            Subject: {subject}

            {body}

            Attached Invoice Code:
            {invoice}
        """
    
    mock_logger.create_message.assert_called_with(expected_content, "INFO", debt_id, task_id)
