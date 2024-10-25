import pytest
from unittest.mock import patch, MagicMock
from app.tasks.invoice_tasks import generate_invoice_task

@patch('app.tasks.invoice_tasks.send_email_task')
@patch('app.tasks.invoice_tasks.InvoiceService')

def test_generate_invoice_task_success(mock_invoice_service_class, mock_send_email_task):
    mock_invoice_service_instance = mock_invoice_service_class.return_value

    debt_details = [
        {"debtId": "1", "debtAmount": 100.0, "debtDueDate": "2024-10-31", "name": "John Doe"},
        {"debtId": "2", "debtAmount": 200.0, "debtDueDate": "2024-11-01", "name": "Jane Doe"}
    ]

    mock_invoice_service_instance.generate_invoice.side_effect = [
        "invoice_1",
        "invoice_2"
    ]

    task_id = "task_test_id"

    generate_invoice_task(debt_details, task_id)

    mock_invoice_service_instance.generate_invoice.assert_any_call("1", 100.0, "2024-10-31", "John Doe", task_id)
    mock_invoice_service_instance.generate_invoice.assert_any_call("2", 200.0, "2024-11-01", "Jane Doe", task_id)

    expected_invoices = [
        ["invoice_1", debt_details[0]],
        ["invoice_2", debt_details[1]]
    ]

    mock_send_email_task.delay.assert_called_once_with(expected_invoices, task_id)

@patch('app.tasks.invoice_tasks.send_email_task')
@patch('app.tasks.invoice_tasks.InvoiceService')
def test_generate_invoice_task_failure(mock_invoice_service_class, mock_send_email_task, mocker):
    mock_invoice_service_instance = mock_invoice_service_class.return_value

    exception_instance = Exception("Simulated Failure")
    mock_invoice_service_instance.generate_invoice.side_effect = exception_instance

    debt_details = [
        {"debtId": "1", "debtAmount": 100.0, "debtDueDate": "2024-10-31", "name": "John Doe"}
    ]
    
    exception_error = Exception("Simulated Failure")
    mock_invoice_service_instance.generate_invoice.side_effect = exception_error

    task_id = "task_test_id"

    with pytest.raises(Exception) as exc_info:
        generate_invoice_task(debt_details, task_id)
        assert exc_info == exception_error

    mock_invoice_service_instance.generate_invoice.assert_called_once_with("1", 100.0, "2024-10-31", "John Doe", task_id)

    mock_send_email_task.delay.assert_not_called()