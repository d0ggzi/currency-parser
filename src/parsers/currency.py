import logging

import requests
from bs4 import BeautifulSoup
from src.models.country_curr import Currency, DateValue, CurrencyValues
from datetime import datetime

logger = logging.getLogger(__name__)


class CurrencyParser:
    def __init__(self, currencies: list[Currency]):
        self.currencies = currencies

    def scrape_currencies(self, start_date: datetime, end_date: datetime) -> list[CurrencyValues]:
        """
        Run parser for every currency with date between start_date and end_date.

        :param start_date:
        :param end_date:
        :return: list of CurrencyValues objects
        """
        curr_values_all = []
        for currency in self.currencies:
            curr_values = CurrencyValues(currency=currency)
            date_values = self.parse(currency.cur_code, start_date, end_date)
            curr_values.values += date_values
            curr_values.relative_values += [DateValue(value=round(elem.value - currency.value, 4), date=elem.date)
                                            for elem in date_values]
            curr_values_all.append(curr_values)
        return curr_values_all

    @staticmethod
    def _get_link(cur_code, start_date: datetime, end_date: datetime) -> str:
        """
        Create link with given parameters to parse

        :param cur_code: currency code
        :param start_date:
        :param end_date:
        :return: link url
        """
        s_day, s_month, s_year = start_date.day, start_date.month, start_date.year
        e_day, e_month, e_year = end_date.day, end_date.month, end_date.year
        url = (f"https://www.finmarket.ru/currency/rates/?id=10148&pv=1&cur={cur_code}&"
               f"bd={s_day}&bm={s_month}&by={s_year}&ed={e_day}&em={e_month}&ey={e_year}&x=11&y=8#archive")
        return url

    @staticmethod
    def parse(cur_code, start_date: datetime, end_date: datetime) -> list[DateValue]:
        """
        Parse www.finmarket.ru for given currency code and date between start_date and end_date.

        :param cur_code: currency code
        :param start_date:
        :param end_date:
        :return: list of DateValue objects
        """
        date_values = []

        url = CurrencyParser._get_link(cur_code, start_date, end_date)
        response = requests.get(url)
        logger.debug("Getting response from %s", url)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')
        currency_table = soup.find('table', class_='karramba')

        rows = currency_table.find_all('tr')[1:]
        logger.debug("Found table with %d rows", len(rows))
        for row in rows:
            columns = row.find_all('td')
            currency_date = datetime.strptime(columns[0].text.strip(), "%d.%m.%Y")
            currency_value = float(columns[2].text.strip().replace(",", "."))
            date_value = DateValue(date=currency_date, value=currency_value)
            date_values.append(date_value)
        return date_values
