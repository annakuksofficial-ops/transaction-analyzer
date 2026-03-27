import json
import logging
import re

import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="logs/services.log",
    filemode="w",
)
logger = logging.getLogger("services")


def simple_search(search_word, all_transactions):
    """Ищет транзакции где есть нужное слово в описании или категории"""
    print("Ищу слово:", search_word)
    logger.info("Поиск: " + search_word)

    found = []
    word_lower = search_word.lower()

    for one_transaction in all_transactions:
        description = str(one_transaction.get("Описание", ""))
        category = str(one_transaction.get("Категория", ""))

        description_lower = description.lower()
        category_lower = category.lower()

        if word_lower in description_lower or word_lower in category_lower:
            found.append(one_transaction)

    print("Нашёл", len(found), "транзакций")
    logger.info("Найдено " + str(len(found)) + " штук")

    result_json = json.dumps(found, ensure_ascii=False, indent=2, default=str)

    return result_json


def cashback_categories(transactions, year, month):
    """Считает кешбэк по категориям за месяц"""
    print("Анализ кешбэка за", year, "-", month)
    logger.info("Анализ кешбэка за " + str(year) + "-" + str(month))

    month_trans = []
    for t in transactions:
        date_str = t.get("Дата операции", "")
        if isinstance(date_str, str):
            if len(date_str) > 10:
                trans_year = int(date_str[6:10])
                trans_month = int(date_str[3:5])
                if trans_year == year and trans_month == month:
                    month_trans.append(t)

    print("Найдено транзакций за месяц:", len(month_trans))
    logger.info("Найдено транзакций за месяц: " + str(len(month_trans)))

    cat_spent = {}
    for t in month_trans:
        amount = t.get("Сумма операции", 0)
        if amount >= 0:
            continue

        category = t.get("Категория", "")
        if category == "" or pd.isna(category):
            continue

        spent = abs(amount)
        if category in cat_spent:
            cat_spent[category] = cat_spent[category] + spent
        else:
            cat_spent[category] = spent

    cashback = {}
    for cat in cat_spent:
        cb = cat_spent[cat] // 100
        if cb > 0:
            cashback[cat] = cb

    result_dict = {}
    for i in range(100):
        biggest_cat = ""
        biggest_val = 0
        for cat in cashback:
            if cashback[cat] > biggest_val and cat not in result_dict:
                biggest_val = cashback[cat]
                biggest_cat = cat
        if biggest_cat != "":
            result_dict[biggest_cat] = biggest_val

    print("Найдено категорий с кешбэком:", len(result_dict))
    logger.info("Найдено категорий с кешбэком: " + str(len(result_dict)))

    return json.dumps(result_dict, ensure_ascii=False, indent=2)


def search_phone_numbers(transactions):
    """Ищет транзакции, где в описании есть номер телефона"""
    print("Ищу транзакции с номерами телефонов")
    logger.info("Поиск транзакций с номерами телефонов")

    found = []

    for t in transactions:
        description = t.get("Описание", "")

        if pd.isna(description):
            continue

        text = str(description)

        if re.search(r"\+7", text):
            found.append(t)

    print("Найдено транзакций с телефонами:", len(found))
    logger.info("Найдено транзакций с телефонами: " + str(len(found)))

    return json.dumps(found, ensure_ascii=False, indent=2, default=str)
