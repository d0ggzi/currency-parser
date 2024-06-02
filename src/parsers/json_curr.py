import json
import logging
from datetime import datetime, timedelta

from src.models.country_curr import Currency
from src.settings.config import settings
from src.parsers.currency import CurrencyParser

logger = logging.getLogger(__name__)


class JsonCurrParser:
    def __init__(self):
        self.filename = settings.CURR_CONFIG
        self.basic_curr_date = settings.BASIC_CURR_DATE

    def parse_county_curr(self) -> list[Currency]:
        """
        Parse the JSON file and return a list of Currency objects.

        :return: list of Currency objects
        """
        res_currencies = []
        with open(self.filename, "r") as f:
            logger.info("Parsing JSON file")
            country_curr = json.load(f)
            for elem in country_curr:
                elem_value = self.parse_basic_curr(elem['cur_code'])
                res_currencies.append(Currency(**elem, value=elem_value))
        return res_currencies

    def parse_basic_curr(self, cur_code: int) -> float:
        """
        Get a basic currency of the given currency code.

        :param cur_code: currency code
        :return: basic currency
        """
        date = datetime.strptime(self.basic_curr_date, "%d.%m.%Y")
        next_day = date + timedelta(days=1)
        logger.debug("Parsing basic currency of the currency code %s", cur_code)
        date_values = CurrencyParser.parse(cur_code, date, next_day)
        if not date_values:
            raise ValueError("There is no data on given basic currency date %s", self.basic_curr_date)
        return date_values[0].value

