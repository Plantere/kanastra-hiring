import pytest
from app.tasks.email_tasks import send_email_task
from unittest.mock import patch

@patch('app.tasks.email_tasks.Logger')
@patch('app.tasks.email_tasks.EmailService')
def test_send_email_task_success(mock_email_service, mock_logger, mocker):
    mock_email_service_instance = mock_email_service.return_value
    mock_logger_instance = mock_logger.return_value

    invoices = [
        ("invoice_code_123", {"email": "test@example.com", "debtId": "debt123"})
    ]

    task_id="test-task-id"

    send_email_task(invoices, task_id)

    mock_email_service_instance.send_email.assert_called_once_with(
        "test@example.com",
        "Invoice Arrived",
        "Dear Customer, your invoice has arrived.",
        "invoice_code_123",
        "debt123",
        "test-task-id"
    )

    mock_logger_instance.create_message.assert_called_once_with(
        "Email successfully sent to test@example.com for Debt ID: debt123",
        "INFO",
        "debt123",
        "test-task-id"
    )

@patch('app.tasks.email_tasks.Logger')
@patch('app.tasks.email_tasks.EmailService')
@patch('app.tasks.email_tasks.send_email_task.retry')
def test_send_email_task_failure_and_retry(mock_retry, mock_email_service, mock_logger):
    mock_email_service_instance = mock_email_service.return_value
    mock_logger_instance = mock_logger.return_value

    exception_instance = Exception("Simulated Failure")
    mock_email_service_instance.send_email.side_effect = exception_instance
    

    invoices = [
        ("invoice_code_123", {"email": "test@example.com", "debtId": "debt123"})
    ]
    
    task_id="test-task-id"
    with pytest.raises(Exception) as exc_info:
        send_email_task(invoices, task_id)

        assert exc_info == exception_instance

    mock_email_service_instance.send_email.assert_called_once_with(
        "test@example.com",
        "Invoice Arrived",
        "Dear Customer, your invoice has arrived.",
        "invoice_code_123",
        "debt123",
        task_id
    )

    mock_logger_instance.create_message.assert_called_once_with(
        "Failed to send email to test@example.com for Debt ID: debt123 - Simulated Failure",
        "ERROR",
        "debt123",
        task_id
    )

    mock_retry.assert_called_once_with(exc=exception_instance)
