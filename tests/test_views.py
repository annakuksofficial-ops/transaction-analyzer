import json
from datetime import datetime

import pandas as pd
import pytest

from src.views import get_cards_info, get_greeting, get_top_transactions, main_page


@pytest.fixture
def sample_dataframe():
    """Создает тестовые данные для тестов"""
    data = pd.DataFrame(
        {
            "Номер карты": ["*7197", "*7197", "*5091"],
            "Сумма операции": [-100, -50, -200],
            "Дата операции": ["31.12.2021 16:44:00", "30.12.2021 19:18:22", "29.12.2021 10:00:00"],
            "Категория": ["Супермаркеты", "Супермаркеты", "Каршеринг"],
            "Описание": ["Колхоз", "Колхоз", "Ситидрайв"],
        }
    )
    return data


@pytest.fixture
def empty_dataframe():
    """Создает пустой DataFrame"""
    return pd.DataFrame()


@pytest.fixture
def one_card_dataframe():
    """Создает данные только с одной картой"""
    data = pd.DataFrame({"Номер карты": ["*7197", "*7197"], "Сумма операции": [-100, -50]})
    return data


@pytest.fixture
def one_transaction_dataframe():
    """Создает данные с одной транзакцией"""
    data = pd.DataFrame(
        {
            "Дата операции": [datetime(2021, 12, 31, 16, 44)],
            "Сумма операции": [-160],
            "Категория": ["Супермаркеты"],
            "Описание": ["Колхоз"],
        }
    )
    return data


@pytest.mark.parametrize(
    "time_str,expected",
    [
        ("2021-12-31 10:00:00", "Доброе утро"),
        ("2021-12-31 15:00:00", "Добрый день"),
        ("2021-12-31 20:00:00", "Добрый вечер"),
        ("2021-12-31 03:00:00", "Доброй ночи"),
    ],
)
def test_get_greeting_parametrized(time_str, expected):
    """Проверяет приветствие для разного времени"""
    result = get_greeting(time_str)
    assert result == expected


# Простые тесты для get_greeting
def test_get_greeting_morning():
    result = get_greeting("2021-12-31 10:00:00")
    assert result == "Доброе утро"


def test_get_greeting_day():
    result = get_greeting("2021-12-31 15:00:00")
    assert result == "Добрый день"


def test_get_greeting_evening():
    result = get_greeting("2021-12-31 20:00:00")
    assert result == "Добрый вечер"


def test_get_greeting_night():
    result = get_greeting("2021-12-31 03:00:00")
    assert result == "Доброй ночи"


def test_get_cards_info_empty(empty_dataframe):
    """Проверяет get_cards_info с пустыми данными"""
    result = get_cards_info(empty_dataframe)
    assert result == []


def test_get_cards_info_one_card(one_card_dataframe):
    """Проверяет get_cards_info с одной картой"""
    result = get_cards_info(one_card_dataframe)
    assert len(result) == 1
    assert result[0]["last_digits"] == "7197"
    assert result[0]["total_spent"] == 150


def test_get_cards_info_multiple_cards(sample_dataframe):
    """Проверяет get_cards_info с несколькими картами"""
    result = get_cards_info(sample_dataframe)
    assert len(result) == 2

    card1 = result[0]
    assert card1["last_digits"] == "7197"
    assert card1["total_spent"] == 150

    card2 = result[1]
    assert card2["last_digits"] == "5091"
    assert card2["total_spent"] == 200


def test_get_top_transactions(one_transaction_dataframe):
    """Проверяет get_top_transactions с одной транзакцией"""
    result = get_top_transactions(one_transaction_dataframe)
    assert len(result) == 1
    assert result[0]["amount"] == 160


def test_get_top_transactions_empty(empty_dataframe):
    """Проверяет get_top_transactions с пустыми данными"""
    result = get_top_transactions(empty_dataframe)
    assert result == []


def test_main_page_works():
    """Проверяет, что main_page возвращает корректный JSON"""
    result = main_page("2021-12-31 16:44:00")
    result_data = json.loads(result)

    assert "greeting" in result_data
    assert "cards" in result_data
    assert "top_transactions" in result_data
    assert "currency_rates" in result_data
    assert "stock_prices" in result_data


def test_events_page_week():
    from src.utils import read_excel_file
    from src.views import events_page

    df = read_excel_file("data/operations.xlsx")
    result = events_page(df, "W")
    import json

    data = json.loads(result)
    assert "expenses" in data
    assert "income" in data


def test_events_page_month():
    from src.utils import read_excel_file
    from src.views import events_page

    df = read_excel_file("data/operations.xlsx")
    result = events_page(df, "M")
    import json

    data = json.loads(result)
    assert "expenses" in data


def test_events_page_year():
    from src.utils import read_excel_file
    from src.views import events_page

    df = read_excel_file("data/operations.xlsx")
    result = events_page(df, "Y")
    import json

    data = json.loads(result)
    assert "expenses" in data


def test_events_page_all():
    from src.utils import read_excel_file
    from src.views import events_page

    df = read_excel_file("data/operations.xlsx")
    result = events_page(df, "ALL")
    import json

    data = json.loads(result)
    assert "expenses" in data


def test_events_page_empty():
    import pandas as pd

    from src.views import events_page

    df = pd.DataFrame()
    result = events_page(df, "M")
    import json

    data = json.loads(result)
    assert data["expenses"]["total_amount"] == 0
