import json
from unittest.mock import patch

import pandas as pd

from src.main import main


@patch("src.main.read_excel_file")
@patch("src.main.main_page")
@patch("src.main.simple_search")
@patch("src.main.spending_by_category")
def test_main_runs(mock_report, mock_search, mock_main_page, mock_read):
    """Проверяет, что main.py запускается без ошибок"""
    mock_read.return_value = pd.DataFrame(
        {
            "Дата операции": ["31.12.2021 16:44:00"],
            "Сумма операции": [-160],
            "Категория": ["Супермаркеты"],
            "Описание": ["Колхоз"],
        }
    )
    mock_main_page.return_value = json.dumps(
        {"greeting": "Добрый день", "cards": [], "top_transactions": [], "currency_rates": [], "stock_prices": []}
    )
    mock_search.return_value = json.dumps([])
    mock_report.return_value = pd.DataFrame()

    try:
        main()
    except Exception as e:
        assert False, f"main() вызвал ошибку: {e}"
    else:
        assert True
