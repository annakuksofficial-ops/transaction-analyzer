import pandas as pd

from src.reports import spending_by_category, spending_by_weekday


def test_spending_by_category_simple():
    data = pd.DataFrame(
        {
            "Дата операции": ["31.12.2021 16:44:00"],
            "Сумма операции": [-160],
            "Категория": ["Супермаркеты"],
            "Описание": ["Колхоз"],
        }
    )
    result = spending_by_category(data, "Супермаркеты", "2022-01-01")
    assert isinstance(result, pd.DataFrame)


def test_spending_by_category_no_date():
    """Тест без указания даты"""
    data = pd.DataFrame(
        {
            "Дата операции": ["31.12.2021 16:44:00"],
            "Сумма операции": [-160],
            "Категория": ["Супермаркеты"],
            "Описание": ["Колхоз"],
        }
    )
    result = spending_by_category(data, "Супермаркеты")
    assert isinstance(result, pd.DataFrame)


def test_spending_by_category_empty():
    data = pd.DataFrame()
    result = spending_by_category(data, "Супермаркеты")
    assert len(result) == 0


def test_spending_by_category_wrong_category():
    data = pd.DataFrame(
        {
            "Дата операции": ["31.12.2021 16:44:00"],
            "Сумма операции": [-160],
            "Категория": ["Каршеринг"],
            "Описание": ["Ситидрайв"],
        }
    )
    result = spending_by_category(data, "Супермаркеты", "2021-12-31")
    assert len(result) == 0


def test_spending_by_category_positive_amount():
    data = pd.DataFrame(
        {
            "Дата операции": ["31.12.2021 16:44:00"],
            "Сумма операции": [500],
            "Категория": ["Супермаркеты"],
            "Описание": ["Пополнение"],
        }
    )
    result = spending_by_category(data, "Супермаркеты", "2021-12-31")
    assert len(result) == 0


def test_spending_by_weekday_simple():
    """Тест для отчета по дням недели"""
    data = pd.DataFrame(
        {
            "Дата операции": ["31.12.2021 16:44:00"],  # пятница
            "Сумма операции": [-160],
            "Категория": ["Супермаркеты"],
            "Описание": ["Колхоз"],
        }
    )
    result = spending_by_weekday(data, "2022-01-01")
    import json

    data_result = json.loads(result)
    assert len(data_result) == 7


def test_spending_by_weekday_empty():
    data = pd.DataFrame()
    result = spending_by_weekday(data)
    assert result is not None


def test_spending_by_weekday_with_date():
    """Тест с указанием даты"""
    data = pd.DataFrame(
        {
            "Дата операции": ["31.12.2021 16:44:00", "30.12.2021 19:18:22"],
            "Сумма операции": [-160, -50],
            "Категория": ["Супермаркеты", "Супермаркеты"],
            "Описание": ["Колхоз", "Лента"],
        }
    )
    result = spending_by_weekday(data, "2022-01-01")
    import json

    data_result = json.loads(result)
    assert len(data_result) == 7


def test_spending_by_weekday_no_transactions():
    """Тест когда нет транзакций в периоде"""
    data = pd.DataFrame(
        {
            "Дата операции": ["31.12.2020 16:44:00"],
            "Сумма операции": [-160],
            "Категория": ["Супермаркеты"],
            "Описание": ["Колхоз"],
        }
    )
    result = spending_by_weekday(data, "2022-01-01")
    import json

    data_result = json.loads(result)
    for day in data_result:
        assert day["transactions_count"] == 0
