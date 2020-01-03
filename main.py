import requests
import os
from terminaltables import AsciiTable
from dotenv import load_dotenv
from itertools import count

URL_HH = 'https://api.hh.ru/vacancies'
URL_SJ = 'https://api.superjob.ru/2.0/vacancies/'
MOST_POPULAR_PROGRAMING_LANGUAGES = ['JavaScript', 'Python', 'Java', 'Ruby', 'PHP', 'C++', 'C#', 'C', 'Go']



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
    response = requests.get(URL_HH, params=params)
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
        page_response = requests.get(URL_HH, params=params)
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
    amount = 0
    for page in range(pages):
        amount += sum(pagination[page])
    return int(amount // get_vacancies_processed_hh(pagination))


# SuperJob vacancies

def get_main_request_sj(language, headers):
    params = {
        'keyword': language,
        'catalogues': ['Разработка', 'Программирование'],
        'town': 'Москва'
    }
    response = requests.get(URL_SJ, params=params, headers=headers)
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
        page_response = requests.get(URL_SJ, params=params, headers=headers)
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
    amount = sum(predict_rub_salary_for_sj(pagination))
    return amount // len(predict_rub_salary_for_sj(pagination))


def create_table(title, table_data):
    table_instance = AsciiTable(table_data, title)
    table_instance.justify_columns[4] = 'right'
    return print(table_instance.table)


def main():
    load_dotenv()
    access_token = os.getenv('SECRET_TOKEN')
    headers = {'X-Api-App-Id': access_token}

    table_data_hh = [['Язык программирования ', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата']]
    for language in MOST_POPULAR_PROGRAMING_LANGUAGES:
        pagination = get_pagination_hh(language)
        table_data_hh.append([language,
                              get_main_requst_hh(language)['found'],
                              get_vacancies_processed_hh(pagination),
                              get_average_salary_hh(pagination)
                              ])
    create_table('HeadHunter', table_data_hh)

    table_data_sj = [['Язык программирования ', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата']]
    for language in MOST_POPULAR_PROGRAMING_LANGUAGES:
        pagination_sj = get_pagination_sj(language, headers)
        table_data_sj.append([language,
                              get_main_request_sj(language, headers)['total'],
                              get_vacancies_processed_sj(pagination_sj),
                              get_average_salary_sj(pagination_sj),
                              ])
    create_table('SuperJob', table_data_sj)


if __name__ == '__main__':
    main()
