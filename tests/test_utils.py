from unittest.mock import MagicMock, patch

import pandas as pd

from src.utils import filter_by_date, get_currency_rates, get_stock_prices, read_excel_file


def test_read_excel_file_not_found():
    result = read_excel_file("no_file.xlsx")
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 0


@patch("src.utils.pd.read_excel")
def test_read_excel_file_ok(mock_read):
    test_data = pd.DataFrame({"a": [1, 2]})
    mock_read.return_value = test_data

    result = read_excel_file("test.xlsx")
    assert len(result) == 2


def test_filter_by_date():
    data = pd.DataFrame({"Дата операции": ["31.12.2021 16:44:00", "30.11.2021 19:18:22"]})
    result = filter_by_date(data, "2021-12-31 23:59:59")
    assert len(result) == 1


@patch("src.utils.requests.get")
def test_get_currency_rates(mock_get):
    mock_response = MagicMock()
    mock_response.json.return_value = {"rates": {"USD": 0.013, "EUR": 0.011}}
    mock_get.return_value = mock_response

    result = get_currency_rates(["USD"])
    assert len(result) == 1
    assert result[0]["currency"] == "USD"


@patch("src.utils.requests.get")
def test_get_stock_prices(mock_get):
    mock_response = MagicMock()
    mock_response.json.return_value = {"close": 150.50}
    mock_get.return_value = mock_response

    result = get_stock_prices(["AAPL"])
    assert len(result) == 1
    assert result[0]["stock"] == "AAPL"


def test_get_date_from_string():
    from src.utils import get_date_from_string

    result = get_date_from_string("31.12.2021 16:44:00")
    assert result is not None
    assert result.year == 2021
    assert result.month == 12
    assert result.day == 31


def test_get_date_from_string_invalid():
    from src.utils import get_date_from_string

    result = get_date_from_string("invalid date")
    assert result is None


def test_filter_by_date_range():
    from datetime import datetime

    import pandas as pd

    from src.utils import filter_by_date_range

    data = pd.DataFrame({"Дата операции": ["31.12.2021 16:44:00", "30.11.2021 19:18:22", "01.12.2021 10:00:00"]})
    start_date = datetime(2021, 12, 1)
    end_date = datetime(2021, 12, 31)

    result = filter_by_date_range(data, start_date, end_date)
    assert len(result) == 2


def test_filter_by_date_range_empty():
    from datetime import datetime

    import pandas as pd

    from src.utils import filter_by_date_range

    data = pd.DataFrame()
    start_date = datetime(2021, 12, 1)
    end_date = datetime(2021, 12, 31)

    result = filter_by_date_range(data, start_date, end_date)
    assert len(result) == 0
