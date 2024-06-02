import logging
import random

from src.container import APP_CONTAINER
from datetime import datetime

logger = logging.getLogger(__name__)


class ParserAdapter:
    def __init__(self):
        self.db = APP_CONTAINER.database()

    @staticmethod
    def check_start_and_end_date(start_date: str, end_date: str):
        """
        Checks weather start and end date are valid.

        :param start_date:
        :param end_date:
        :return: None
        """
        start_date, end_date = datetime.strptime(start_date, "%Y-%m-%d"), datetime.strptime(end_date, "%Y-%m-%d")
        date_now = datetime.now()
        if end_date > date_now:
            raise ValueError(f"Некорректная дата конца. Она должна быть не позже {date_now.strftime('%Y-%m-%d')}")
        elif start_date < datetime(day=3, month=7, year=1992):
            raise ValueError("Некорректная дата начала. Она должна быть не раньше 03.07.1992")
        elif start_date > end_date:
            raise ValueError("Дата начала должна быть раньше даты конца")
        logger.debug("Dates start=%s and end=%s are valid", start_date, end_date)

    def parse(self, start_date: str, end_date: str):
        """
        Parses countries and currency values between start and end date.

        :param start_date:
        :param end_date:
        :return: None
        """
        self.check_start_and_end_date(start_date, end_date)
        start_date, end_date = datetime.strptime(start_date, "%Y-%m-%d"), datetime.strptime(end_date, "%Y-%m-%d")
        if end_date.year - start_date.year > 2:
            raise ValueError("Некорректно указанный промежуток. Разница в годах не должна быть больше 2")

        logger.info("Parsing countries")
        country_parser = APP_CONTAINER.country_parser()
        countries = country_parser.scrape_countries()
        self.db.insert_countries(countries)

        logger.info("Parsing currency values")
        currency_parser = APP_CONTAINER.currency_parser()
        currencies = currency_parser.scrape_currencies(start_date=start_date, end_date=end_date)
        self.db.insert_curr_values(currencies)

    def get_all_countries(self) -> list[str]:
        """
        Get all countries.

        :return: list of countries in string format
        """
        logger.info("Getting all countries")
        return self.db.get_all_countries()

    def get_data_values(self, input_countries: list[str], start_date: str, end_date: str) -> dict:
        """
        Returns currency values and datetime for input countries between start and end date.

        :param input_countries: list of countries
        :param start_date:
        :param end_date:
        :return: data in dictionary format for Chart.js
        """
        self.check_start_and_end_date(start_date, end_date)
        if not input_countries:
            raise ValueError("Укажите страны для вывода графиков")
        curr_colors = {}
        datasets = []
        logger.info("Getting data for %d countries", len(input_countries))
        for country in input_countries:
            curr_dataset = dict()
            currency_id, date_values = self.db.get_currencies_for_country(country, start_date, end_date)
            curr_dataset["label"] = country
            curr_dataset["data"] = [el.value for el in date_values]
            if currency_id in curr_colors:
                curr_dataset["borderColor"] = curr_colors[currency_id]
            else:
                new_color = "#" + ''.join([random.choice('0123456789ABCDEF') for _ in range(6)])
                curr_dataset["borderColor"] = new_color
                curr_colors[currency_id] = new_color
            datasets.append(curr_dataset)

        data = {
            "labels": [el.date.strftime("%Y-%m-%d") for el in date_values],
            "datasets": datasets
        }

        return data
