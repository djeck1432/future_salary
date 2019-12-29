import requests
import os
from terminaltables import AsciiTable
from dotenv import load_dotenv

load_dotenv()
access_token = os.getenv('SECRET_TOKEN')
url_sj = 'https://api.superjob.ru/2.0/vacancies/'
headers = {'X-Api-App-Id': access_token}
url_hh = 'https://api.hh.ru/vacancies'
most_popular_programing_languages = ['JavaScript', 'Python', 'Java', 'Ruby', 'PHP', 'C++', 'C#', 'C', 'Go']
vacancies = {language: '' for language in most_popular_programing_languages}


def main_url_requst_hh(language):
    params = {
        'text': language,
        'only_with_salary': 'true',
        'period': 30,
        'area': 1,
    }
    response = requests.get(url_hh, params=params)
    response.raise_for_status()
    return response.json()


def get_pagination_hh(language):
    pages = main_url_requst_hh(language)['pages']
    page = 0
    all_sites = []
    while page < pages:
        params = {
            'text': language,
            'only_with_salary': 'true',
            'period': 30,
            'area': 1,
            'page': page
        }
        page_response = requests.get(url_hh, params=params)
        page_response.raise_for_status()
        all_sites.append(predict_rub_salary_hh(language))
        page += 1
    return all_sites


def predict_rub_salary_hh(language):
    rub_salary = []
    vacancies_salary = main_url_requst_hh(language)
    salaries = [vacancies_salary['items'][num]['salary'] for num in range(len(vacancies_salary))]
    for salary in salaries:
        if salary['currency'] != 'RUR':
            continue
        elif salary['from'] and salary['to']:
            rub_salary.append(int((salary['from'] + salary['to']) // 2))
        elif salary['from']:
            rub_salary.append(int(salary['from'] * 1.2))
        elif salary['to']:
            rub_salary.append(int(salary['to'] * 0.8))
    return rub_salary


def get_vacancies_processed_hh(pagination):
    pages = len(pagination)
    amount_salary = 0
    for page in range(pages):
        amount_salary += len(pagination[page])
    return amount_salary


def get_average_salary_hh(pagination):
    pages = len(pagination)
    suma = 0
    for page in range(pages):
        suma += sum(pagination[page])
    return int(suma // get_vacancies_processed_hh(pagination))


# SuperJob vacancies

def main_url_request_sj(language):
    params = {
        'keyword': language,
        'catalogues': ['Разработка', 'Программирование'],
        'town': 'Москва'
    }
    response = requests.get(url_sj, params=params, headers=headers)
    response.raise_for_status()
    return response.json()


def get_pagination_sj(language):
    page = 0
    pages = 1
    all_sites = []
    while pages != 0:
        params = {
            'keyword': language,
            'catalogues': ['Разработка', 'Программирование'],
            'town': 'Москва',
            'page': page
        }
        page_response = requests.get(url_sj, params=params, headers=headers)
        page_response.raise_for_status()
        all_sites.append(page_response.json()['objects'])
        pages = len(page_response.json()['objects'])
        page += 1
    return all_sites


def predict_rub_salary_for_sj(pagination):
    rub_salary = []
    salaries = []
    for id in range(len(pagination)):
        for num in range(len(pagination[id])):
            salaries.append((pagination[id][num]['payment_from'], pagination[id][num]['payment_to']))
    for payment_from, payment_to in salaries:
        if payment_from > 0 and payment_to > 0:
            rub_salary.append(int(payment_from + payment_to) // 2)
        elif payment_from:
            rub_salary.append(int(payment_from * 1.2))
        elif payment_to:
            rub_salary.append(int(payment_to * 0.8))
    return rub_salary


def get_vacancies_processed_sj(pagination):
    pages = len(pagination)
    amount_salary = 0
    for page in range(pages):
        amount_salary += len(pagination[page])
    return amount_salary


def get_average_salary_sj(pagination):
    summa = sum(predict_rub_salary_for_sj(pagination))
    return summa // len(predict_rub_salary_for_sj(pagination))


def main():
    TABLE_DATA = [['Язык программирования ', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата']]
    for language in most_popular_programing_languages:
        pagination_sj = get_pagination_sj(language)
        TABLE_DATA.append([language,
                           main_url_request_sj(language)['total'],
                           get_vacancies_processed_sj(pagination_sj),
                           get_average_salary_sj(pagination_sj),
                           ])
    title = 'SuperJob'
    table_instance = AsciiTable(TABLE_DATA, title)
    table_instance.justify_columns[4] = 'right'
    print(table_instance.table)


def main():
    TABLE_DATA_HH = [['Язык программирования ', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата']]
    for language in most_popular_programing_languages:
        pagination = get_pagination_hh(language)
        TABLE_DATA_HH.append([
            language,
            main_url_requst_hh(language)['found'],
            get_vacancies_processed_hh(pagination),
            get_average_salary_hh(pagination)
        ])
    title = 'HeadHunter'
    table_instance = AsciiTable(TABLE_DATA_HH, title)
    table_instance.justify_columns[4] = 'right'
    print(table_instance.table)
    print()

    TABLE_DATA_SJ = [['Язык программирования ', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата']]
    for language in most_popular_programing_languages:
        pagination_sj = get_pagination_sj(language)
        TABLE_DATA_SJ.append([language,
                              main_url_request_sj(language)['total'],
                              get_vacancies_processed_sj(pagination_sj),
                              get_average_salary_sj(pagination_sj),
                              ])
    title = 'SuperJob'
    table_instance = AsciiTable(TABLE_DATA_SJ, title)
    table_instance.justify_columns[4] = 'right'
    print(table_instance.table)


if __name__ == '__main__':
    main()
