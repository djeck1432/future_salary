import requests
import os
from terminaltables import AsciiTable
from dotenv import load_dotenv
from itertools import count


url_sj = 'https://api.superjob.ru/2.0/vacancies/'
url_hh = 'https://api.hh.ru/vacancies'
most_popular_programing_languages = ['JavaScript', 'Python', 'Java', 'Ruby', 'PHP', 'C++', 'C#', 'C', 'Go']


def predict_rub_salary(salaries):
    rub_salary = []
    for payment_from, payment_to in salaries:
        if payment_from is not None and payment_to is not None:
            rub_salary.append(int(payment_from + payment_to) // 2)
        elif payment_from and payment_to is not None:
            rub_salary.append(int(payment_from * 1.2))
        elif payment_to and payment_from is not None:
            rub_salary.append(int(payment_to * 0.8))
    return rub_salary


def get_main_requst_hh(language):
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
    all_pages = []
    for page in count(0, 1):
        params = {
            'text': language,
            'only_with_salary': 'true',
            'period': 30,
            'area': 1,
            'page': page
        }
        page_response = requests.get(url_hh, params=params)
        page_response.raise_for_status()
        pages = page_response.json()['pages']
        if page == pages:
            break
        else:
            all_pages.append(predict_rub_salary_hh(language))
    return all_pages


def predict_rub_salary_hh(language):
    vacancies_salary = get_main_requst_hh(language)
    salaries = [vacancies_salary['items'][num]['salary'] for num, vacancy in enumerate(vacancies_salary)]
    salaries_from_to = [(salary['from'], salary['to']) for salary in salaries]
    return predict_rub_salary(salaries_from_to)


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

def get_main_request_sj(language, headers):
    params = {
        'keyword': language,
        'catalogues': ['Разработка', 'Программирование'],
        'town': 'Москва'
    }
    response = requests.get(url_sj, params=params, headers=headers)
    response.raise_for_status()
    return response.json()


def get_pagination_sj(language, headers):
    page = 0
    pages = 1
    all_pages = []
    while pages != 0:
        params = {
            'keyword': language,
            'catalogues': ['Разработка', 'Программирование'],
            'town': 'Москва',
            'page': page
        }
        page_response = requests.get(url_sj, params=params, headers=headers)
        page_response.raise_for_status()
        all_pages.append(page_response.json()['objects'])
        pages = len(page_response.json()['objects'])
        page += 1
    return all_pages


def predict_rub_salary_for_sj(pagination):
    salaries = []
    for num_of_page, page in enumerate(pagination):
        for num, vacancies in enumerate(pagination[num_of_page]):
            salaries.append((pagination[num_of_page][num]['payment_from'], pagination[num_of_page][num]['payment_to']))
    return predict_rub_salary(salaries)


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
    load_dotenv()
    access_token = os.getenv('SECRET_TOKEN')
    headers = {'X-Api-App-Id': access_token}

    table_data_hh = [['Язык программирования ', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата']]
    for language in most_popular_programing_languages:
        pagination = get_pagination_hh(language)
        table_data_hh.append([
            language,
            get_main_requst_hh(language)['found'],
            get_vacancies_processed_hh(pagination),
            get_average_salary_hh(pagination)
        ])
    title = 'HeadHunter'
    table_instance = AsciiTable(table_data_hh, title)
    table_instance.justify_columns[4] = 'right'
    print(table_instance.table)
    print()

    table_data_sj = [['Язык программирования ', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата']]
    for language in most_popular_programing_languages:
        pagination_sj = get_pagination_sj(language, headers)
        table_data_sj.append([language,
                              get_main_request_sj(language, headers)['total'],
                              get_vacancies_processed_sj(pagination_sj),
                              get_average_salary_sj(pagination_sj),
                              ])
    title = 'SuperJob'
    table_instance = AsciiTable(table_data_sj, title)
    table_instance.justify_columns[4] = 'right'
    print(table_instance.table)


if __name__ == '__main__':
    main()
