import json

from src.reports import spending_by_category
from src.services import simple_search
from src.utils import read_excel_file
from src.views import main_page


def main():
    """Запускает все функции по очереди"""
    print("=" * 50)
    print("НАЧИНАЮ РАБОТУ")
    print("=" * 50)

    print("\n1. ГЛАВНАЯ СТРАНИЦА")
    print("-" * 30)

    result = main_page("2021-12-31 16:44:00")
    data = json.loads(result)

    print("Приветствие:", data["greeting"])
    print("Количество карт:", len(data["cards"]))
    print("Курсы валют:", data["currency_rates"])

    print("\n2. ПОИСК ПО СЛОВУ")
    print("-" * 30)

    all_data = read_excel_file("data/operations.xlsx")
    all_transactions = all_data.to_dict(orient="records")

    search_result = simple_search("Колхоз", all_transactions)
    found_list = json.loads(search_result)

    print("Нашёл", len(found_list), "транзакций со словом 'Колхоз'")

    print("\n3. ОТЧЕТ ПО КАТЕГОРИИ")
    print("-" * 30)

    report = spending_by_category(all_data, "Супермаркеты", "2021-12-31")

    if len(report) > 0:
        total_sum = 0
        for money in report["Сумма операции"]:
            total_sum = total_sum + abs(money)

        print("Транзакций:", len(report))
        print("Общая сумма:", round(total_sum, 2))
    else:
        print("Нет транзакций по этой категории")

    print("\n" + "=" * 50)
    print("РАБОТА ЗАКОНЧЕНА")
    print("=" * 50)


if __name__ == "__main__":
    main()
