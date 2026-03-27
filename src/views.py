import json
import logging
from datetime import datetime, timedelta

import pandas as pd

from src.utils import (filter_by_date, filter_by_date_range, get_currency_rates, get_date_from_string,
                       get_stock_prices, read_excel_file)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="logs/views.log",
    filemode="w",
)
logger = logging.getLogger("views")


def get_greeting(date_time_str):
    """Определяет какое сейчас время суток и возвращает приветствие"""
    time_obj = datetime.strptime(date_time_str, "%Y-%m-%d %H:%M:%S")
    hour = time_obj.hour

    if hour >= 5 and hour < 12:
        return "Доброе утро"
    elif hour >= 12 and hour < 18:
        return "Добрый день"
    elif hour >= 18 and hour < 23:
        return "Добрый вечер"
    else:
        return "Доброй ночи"


def get_cards_info(data):
    """Собирает данные по каждой карте: последние 4 цифры, сколько потратили, кешбэк"""
    if len(data) == 0 or "Номер карты" not in data.columns:
        return []

    cards_list = []

    all_cards = data["Номер карты"].unique()

    for card in all_cards:
        if str(card) == "nan":
            continue

        card_data = data[data["Номер карты"] == card]

        total = 0
        for money in card_data["Сумма операции"]:
            if money < 0:
                total = total + abs(money)

        cashback_total = round(total / 100, 2)

        last_numbers = str(card)[-4:]

        card_info = {"last_digits": last_numbers, "total_spent": total, "cashback": cashback_total}

        cards_list.append(card_info)

    return cards_list


def get_top_transactions(data):
    """Находит 5 самых больших трат"""
    expenses_only = []

    for idx in range(len(data)):
        row = data.iloc[idx]
        if row["Сумма операции"] < 0:
            expenses_only.append(
                {
                    "date": row["Дата операции"],
                    "amount": abs(row["Сумма операции"]),
                    "category": row["Категория"],
                    "description": row["Описание"],
                    "amount_abs": abs(row["Сумма операции"]),
                }
            )

    for i in range(len(expenses_only)):
        for j in range(i + 1, len(expenses_only)):
            if expenses_only[i]["amount_abs"] < expenses_only[j]["amount_abs"]:
                temp = expenses_only[i]
                expenses_only[i] = expenses_only[j]
                expenses_only[j] = temp

    top_5 = expenses_only[:5]

    result = []
    for trans in top_5:
        if isinstance(trans["date"], pd.Timestamp):
            date_str = trans["date"].strftime("%d.%m.%Y")
        else:
            date_str = str(trans["date"])

        category_str = ""
        if pd.notna(trans["category"]):
            category_str = trans["category"]

        description_str = ""
        if pd.notna(trans["description"]):
            description_str = trans["description"]

        result.append(
            {"date": date_str, "amount": trans["amount"], "category": category_str, "description": description_str}
        )

    return result


def main_page(date_time_str):
    """Главная функция - собирает всё вместе и возвращает JSON"""
    print("Начинаю работу...")
    logger.info("Запуск с датой: " + date_time_str)

    print("Читаю файл с транзакциями...")
    all_data = read_excel_file("data/operations.xlsx")

    print("Фильтрую по дате...")
    filtered_data = filter_by_date(all_data, date_time_str)

    print("Загружаю настройки...")
    file = open("user_settings.json", "r", encoding="utf-8")
    settings_text = file.read()
    file.close()
    settings = json.loads(settings_text)

    currencies = settings["user_currencies"]
    stocks = settings["user_stocks"]

    print("Получаю курсы валют...")
    currency_data = get_currency_rates(currencies)

    print("Получаю цены акций...")
    stock_data = get_stock_prices(stocks)

    print("Собираю ответ...")
    result = {
        "greeting": get_greeting(date_time_str),
        "cards": get_cards_info(filtered_data),
        "top_transactions": get_top_transactions(filtered_data),
        "currency_rates": currency_data,
        "stock_prices": stock_data,
    }

    print("Превращаю в JSON...")
    json_result = json.dumps(result, ensure_ascii=False, indent=2)

    print("Готово")
    logger.info("Всё сделано")

    return json_result


def events_page(data, date_range="M"):
    """Страница "События" - показывает расходы и доходы"""
    print("Страница События, диапазон:", date_range)

    last_date = None
    for i in range(len(data)):
        date_str = data.iloc[i]["Дата операции"]
        if isinstance(date_str, str):
            trans_date = get_date_from_string(date_str)
            if trans_date is not None:
                if last_date is None or trans_date > last_date:
                    last_date = trans_date

    if last_date is None:
        last_date = datetime.now()

    if date_range == "W":
        start_date = last_date - timedelta(days=7)
    elif date_range == "M":
        start_date = datetime(last_date.year, last_date.month, 1)
    elif date_range == "Y":
        start_date = datetime(last_date.year, 1, 1)
    else:
        start_date = datetime(2000, 1, 1)

    print("Период с", start_date, "по", last_date)

    filtered_data = filter_by_date_range(data, start_date, last_date)
    print("После фильтрации строк:", len(filtered_data))

    expenses_list = []
    for i in range(len(filtered_data)):
        row = filtered_data.iloc[i]
        if row["Сумма операции"] < 0:
            expenses_list.append(row)
    expenses_df = pd.DataFrame(expenses_list)

    total_expenses = 0
    for i in range(len(expenses_df)):
        total_expenses = total_expenses + abs(expenses_df.iloc[i]["Сумма операции"])

    income_list = []
    for i in range(len(filtered_data)):
        row = filtered_data.iloc[i]
        if row["Сумма операции"] > 0:
            income_list.append(row)
    income_df = pd.DataFrame(income_list)

    total_income = 0
    for i in range(len(income_df)):
        total_income = total_income + income_df.iloc[i]["Сумма операции"]

    cat_dict = {}
    for i in range(len(expenses_df)):
        row = expenses_df.iloc[i]
        cat = row["Категория"]
        if pd.isna(cat):
            cat = "Без категории"
        amount = abs(row["Сумма операции"])
        if cat in cat_dict:
            cat_dict[cat] = cat_dict[cat] + amount
        else:
            cat_dict[cat] = amount

    cat_items = []
    for cat in cat_dict:
        cat_items.append([cat, cat_dict[cat]])

    for i in range(len(cat_items)):
        for j in range(i + 1, len(cat_items)):
            if cat_items[i][1] < cat_items[j][1]:
                temp = cat_items[i]
                cat_items[i] = cat_items[j]
                cat_items[j] = temp

    main_cats = []
    other_sum = 0
    for i in range(len(cat_items)):
        if i < 7:
            main_cats.append({"category": cat_items[i][0], "amount": round(cat_items[i][1])})
        else:
            other_sum = other_sum + cat_items[i][1]

    if other_sum > 0:
        main_cats.append({"category": "Остальное", "amount": round(other_sum)})

    transfers_sum = 0
    cash_sum = 0
    for i in range(len(expenses_df)):
        row = expenses_df.iloc[i]
        cat = row["Категория"]
        if pd.isna(cat):
            continue
        amount = abs(row["Сумма операции"])
        if "Перевод" in cat:
            transfers_sum = transfers_sum + amount
        if "Наличные" in cat:
            cash_sum = cash_sum + amount

    transfers_and_cash = []
    if transfers_sum > 0:
        transfers_and_cash.append({"category": "Переводы", "amount": round(transfers_sum)})
    if cash_sum > 0:
        transfers_and_cash.append({"category": "Наличные", "amount": round(cash_sum)})

    income_dict = {}
    for i in range(len(income_df)):
        row = income_df.iloc[i]
        cat = row["Категория"]
        if pd.isna(cat):
            cat = "Без категории"
        amount = row["Сумма операции"]
        if cat in income_dict:
            income_dict[cat] = income_dict[cat] + amount
        else:
            income_dict[cat] = amount

    inc_items = []
    for cat in income_dict:
        inc_items.append([cat, income_dict[cat]])

    for i in range(len(inc_items)):
        for j in range(i + 1, len(inc_items)):
            if inc_items[i][1] < inc_items[j][1]:
                temp = inc_items[i]
                inc_items[i] = inc_items[j]
                inc_items[j] = temp

    main_income = []
    for i in range(len(inc_items)):
        main_income.append({"category": inc_items[i][0], "amount": round(inc_items[i][1])})

    result = {
        "expenses": {
            "total_amount": round(total_expenses),
            "main": main_cats,
            "transfers_and_cash": transfers_and_cash,
        },
        "income": {"total_amount": round(total_income), "main": main_income},
    }

    print("Готово")
    return json.dumps(result, ensure_ascii=False, indent=2)
