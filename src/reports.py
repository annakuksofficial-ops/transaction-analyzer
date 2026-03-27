import json
import logging
from datetime import datetime, timedelta
from functools import wraps

import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="logs/reports.log",
    filemode="w",
)
logger = logging.getLogger("reports")


def save_to_file(filename="report.json"):
    """Декоратор - сохраняет результат в файл"""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)

            with open(filename, "w", encoding="utf-8") as f:
                if isinstance(result, pd.DataFrame):
                    data_for_json = result.to_dict(orient="records")
                    f.write(json.dumps(data_for_json, ensure_ascii=False, indent=2, default=str))
                else:
                    f.write(json.dumps(result, ensure_ascii=False, indent=2, default=str))

            print("Сохранил в файл:", filename)
            logger.info("Сохранено в " + filename)
            return result

        return wrapper

    return decorator


@save_to_file("spending_by_category.json")
def spending_by_category(transactions_data, category_name, start_date=None):
    """Показывает траты по выбранной категории за последние 3 месяца"""
    print("Смотрю траты по категории:", category_name)
    logger.info("Категория: " + category_name)

    if len(transactions_data) == 0:
        print("Нет данных")
        logger.warning("Нет данных для анализа")
        return pd.DataFrame()

    if start_date is None:
        last_date = None
        for idx in range(len(transactions_data)):
            date_val = transactions_data.iloc[idx]["Дата операции"]
            if isinstance(date_val, str):
                try:
                    trans_date = datetime.strptime(date_val, "%d.%m.%Y %H:%M:%S")
                    if last_date is None or trans_date > last_date:
                        last_date = trans_date
                except Exception:
                    pass
            else:
                if last_date is None or date_val > last_date:
                    last_date = date_val

        if last_date is None:
            last_date = datetime.now()
        end_date = last_date
    else:
        end_date = datetime.strptime(start_date, "%Y-%m-%d")

    start_3_months = end_date - timedelta(days=90)

    print("Период с", start_3_months, "по", end_date)
    logger.info("Период с " + str(start_3_months) + " по " + str(end_date))

    all_expenses = []

    for idx in range(len(transactions_data)):
        row = transactions_data.iloc[idx]

        category = row["Категория"]
        if pd.isna(category):
            category = ""

        if category != category_name:
            continue

        amount = row["Сумма операции"]
        if amount >= 0:
            continue

        date_str = row["Дата операции"]

        if isinstance(date_str, str):
            try:
                trans_date = datetime.strptime(date_str, "%d.%m.%Y %H:%M:%S")
            except Exception:
                continue
        else:
            trans_date = date_str

        if trans_date >= start_3_months and trans_date <= end_date:
            all_expenses.append(row)

    result_df = pd.DataFrame(all_expenses)

    print("Нашёл", len(result_df), "транзакций")
    logger.info("Найдено " + str(len(result_df)) + " транзакций")

    return result_df


def spending_by_weekday(transactions_data, start_date=None):
    """Показывает средние траты по дням недели за последние 3 месяца"""
    print("Анализ трат по дням недели")
    logger.info("Анализ трат по дням недели")

    if len(transactions_data) == 0:
        print("Нет данных")
        logger.warning("Нет данных для анализа")
        return pd.DataFrame()

    if start_date is None:
        last_date = None
        for idx in range(len(transactions_data)):
            date_val = transactions_data.iloc[idx]["Дата операции"]
            if isinstance(date_val, str):
                try:
                    trans_date = datetime.strptime(date_val, "%d.%m.%Y %H:%M:%S")
                    if last_date is None or trans_date > last_date:
                        last_date = trans_date
                except Exception:
                    pass
            else:
                if last_date is None or date_val > last_date:
                    last_date = date_val

        if last_date is None:
            last_date = datetime.now()
        end_date = last_date
    else:
        end_date = datetime.strptime(start_date, "%Y-%m-%d")

    start_3_months = end_date - timedelta(days=90)
    print("Период с", start_3_months, "по", end_date)

    days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
    weekday_spent = {day: 0 for day in days}
    weekday_count = {day: 0 for day in days}

    for idx in range(len(transactions_data)):
        row = transactions_data.iloc[idx]

        amount = row["Сумма операции"]
        if amount >= 0:
            continue

        date_str = row["Дата операции"]

        if isinstance(date_str, str):
            try:
                trans_date = datetime.strptime(date_str, "%d.%m.%Y %H:%M:%S")
            except Exception:
                continue
        else:
            trans_date = date_str

        if trans_date >= start_3_months and trans_date <= end_date:
            weekday = trans_date.weekday()
            day_name = days[weekday]
            weekday_spent[day_name] = weekday_spent[day_name] + abs(amount)
            weekday_count[day_name] = weekday_count[day_name] + 1

    result = []
    for day in days:
        if weekday_count[day] > 0:
            avg_spent = round(weekday_spent[day] / weekday_count[day], 2)
        else:
            avg_spent = 0
        result.append({"weekday": day, "avg_spent": avg_spent, "transactions_count": weekday_count[day]})

    print("Готово!")
    return json.dumps(result, ensure_ascii=False, indent=2)
