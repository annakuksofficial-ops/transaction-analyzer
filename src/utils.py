import logging
from datetime import datetime

import pandas as pd
import requests

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="logs/utils.log",
    filemode="w",
)
logger = logging.getLogger("utils")


def read_excel_file(file_path):
    """Читает Excel файл и возвращает данные"""
    print("Читаю файл:", file_path)
    logger.info("Чтение файла: " + file_path)

    try:
        data = pd.read_excel(file_path)
        print("Файл прочитан успешно, строк:", len(data))
        logger.info("Успешно прочитано " + str(len(data)) + " строк")
        return data
    except Exception as error:
        print("Ошибка при чтении файла:", error)
        logger.error("Ошибка чтения файла: " + str(error))
        return pd.DataFrame()


def filter_by_date(data, date_string):
    """Оставляет только транзакции с начала месяца до указанной даты"""
    print("Фильтрую транзакции по дате:", date_string)
    logger.info("Фильтрация по дате: " + date_string)

    target_date = datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
    start_of_month = target_date.replace(day=1, hour=0, minute=0, second=0)
    print("Начало месяца:", start_of_month)
    print("Конечная дата:", target_date)

    data["Дата операции"] = pd.to_datetime(data["Дата операции"], format="%d.%m.%Y %H:%M:%S")

    mask = (data["Дата операции"] >= start_of_month) & (data["Дата операции"] <= target_date)
    filtered_data = data[mask].copy()

    print("Было строк:", len(data))
    print("Осталось строк:", len(filtered_data))
    logger.info("После фильтрации осталось " + str(len(filtered_data)) + " строк")

    return filtered_data


def get_currency_rates(currencies_list):
    """Получает курсы валют через интернет"""
    print("Запрашиваю курсы для валют:", currencies_list)
    logger.info("Запрос курсов для валют: " + str(currencies_list))

    rates_result = []

    for currency in currencies_list:
        print("Получаю курс для", currency)

        try:
            url = "https://api.exchangerate-api.com/v4/latest/RUB"
            response = requests.get(url)
            data = response.json()
            rate = 1 / data["rates"].get(currency, 1)
            rate = round(rate, 2)
            rates_result.append({"currency": currency, "rate": rate})
            print("Курс", currency, ":", rate)
            logger.info("Курс " + currency + ": " + str(rate))
        except Exception as error:
            print("Ошибка при получении курса", currency, ":", error)
            logger.error("Ошибка получения курса " + currency + ": " + str(error))
            rates_result.append({"currency": currency, "rate": 0})

    return rates_result


def get_stock_prices(stocks_list):
    """Получает цены акций через интернет"""
    print("Запрашиваю цены для акций:", stocks_list)
    logger.info("Запрос цен для акций: " + str(stocks_list))

    prices_result = []

    for stock in stocks_list:
        print("Получаю цену для", stock)

        try:
            url = "https://api.marketstack.com/v1/tickers/" + stock + "/eod/latest"
            params = {"access_key": "demo"}
            response = requests.get(url, params=params)
            data = response.json()
            price = data.get("close", 100.0)
            price = round(price, 2)
            prices_result.append({"stock": stock, "price": price})
            print("Цена", stock, ":", price)
            logger.info("Цена " + stock + ": " + str(price))
        except Exception as error:
            print("Ошибка при получении цены", stock, ":", error)
            logger.error("Ошибка получения цены " + stock + ": " + str(error))
            prices_result.append({"stock": stock, "price": 0})

    return prices_result


def get_date_from_string(date_str):
    """Превращает строку с датой в объект даты"""
    try:
        day = int(date_str[0:2])
        month = int(date_str[3:5])
        year = int(date_str[6:10])
        return datetime(year, month, day)
    except Exception:
        return None


def filter_by_date_range(data, start_date, end_date):
    """Фильтрует данные по диапазону дат"""
    result = []
    for i in range(len(data)):
        row = data.iloc[i]
        date_str = row["Дата операции"]
        if isinstance(date_str, str):
            trans_date = get_date_from_string(date_str)
            if trans_date is not None:
                if trans_date >= start_date and trans_date <= end_date:
                    result.append(row)
    if len(result) == 0:
        return pd.DataFrame()
    return pd.DataFrame(result)
