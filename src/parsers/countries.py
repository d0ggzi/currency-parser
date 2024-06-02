import logging

import requests
from bs4 import BeautifulSoup
from src.models.country_curr import Currency

logger = logging.getLogger(__name__)


class CountryParser:
    def __init__(self, currencies: list[Currency]):
        self.url = "https://www.iban.ru/currency-codes"
        self.currency_names = set([el.ru_name for el in currencies])

    def scrape_countries(self) -> dict[str, list[str]]:
        """
        Parse www.iban.ru to get countries and their currencies.

        :return: dictionary where keys are currencies and values are lists of countries.
        """
        response = requests.get(self.url)
        logger.debug("Getting response from %s", self.url)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')
        currency_table = soup.find('table', class_='table-bordered')

        countries_by_curr = dict()
        rows = currency_table.find_all('tr')[1:]
        logger.debug("Found table with %d rows", len(rows))
        for row in rows:
            columns = row.find_all('td')

            currency_name = columns[1].text.strip()
            if currency_name in self.currency_names:
                country = columns[0].text.strip()
                countries_by_curr[currency_name] = countries_by_curr.get(currency_name, []) + [country]
        return countries_by_curr

