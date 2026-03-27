import json

from src.services import cashback_categories, search_phone_numbers, simple_search


def test_simple_search_empty():
    result = simple_search("что-то", [])
    data = json.loads(result)
    assert data == []


def test_simple_search_found():
    transactions = [
        {"Описание": "Покупка в Колхоз", "Категория": "Супермаркеты"},
        {"Описание": "Ситидрайв", "Категория": "Каршеринг"},
    ]
    result = simple_search("Колхоз", transactions)
    data = json.loads(result)
    assert len(data) == 1
    assert "Колхоз" in data[0]["Описание"]


def test_simple_search_not_found():
    transactions = [{"Описание": "Покупка", "Категория": "Супермаркеты"}]
    result = simple_search("Колхоз", transactions)
    data = json.loads(result)
    assert len(data) == 0


def test_simple_search_by_category():
    transactions = [{"Описание": "Что-то", "Категория": "Супермаркеты"}]
    result = simple_search("супермаркеты", transactions)
    data = json.loads(result)
    assert len(data) == 1


def test_simple_search_case_insensitive():
    transactions = [{"Описание": "Покупка в КОЛХОЗ", "Категория": "Продукты"}]
    result = simple_search("колхоз", transactions)
    data = json.loads(result)
    assert len(data) == 1


def test_cashback_categories():
    """Тест для кешбэка"""
    transactions = [
        {"Дата операции": "31.12.2021 16:44:00", "Сумма операции": -160, "Категория": "Супермаркеты"},
        {"Дата операции": "30.12.2021 19:18:22", "Сумма операции": -50, "Категория": "Супермаркеты"},
    ]
    result = cashback_categories(transactions, 2021, 12)
    data = json.loads(result)
    assert "Супермаркеты" in data


def test_search_phone_numbers():
    """Тест для поиска телефонов"""
    transactions = [
        {"Описание": "МТС +7 921 11-22-33"},
        {"Описание": "Покупка в магазине"},
    ]
    result = search_phone_numbers(transactions)
    data = json.loads(result)
    assert len(data) == 1


def test_search_phone_numbers_empty():
    transactions = []
    result = search_phone_numbers(transactions)
    data = json.loads(result)
    assert data == []
