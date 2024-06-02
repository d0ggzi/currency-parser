import logging
import sqlite3

from src.models.country_curr import Currency, CurrencyValues, DateValue

logger = logging.getLogger(__name__)


class Database:
    def __init__(self):
        self.conn = sqlite3.connect('database.db')
        self._create_tables()

    def _create_tables(self):
        """
        Create the database tables if they do not exist yet.

        :return: None
        """
        logger.debug("Creating DB tables")
        with self.conn as con:
            con.execute("""CREATE TABLE IF NOT EXISTS currencies(
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            ru_name VARCHAR(50) NOT NULL,
                            en_name VARCHAR(50) NOT NULL,
                            cur_code INTEGER NOT NULL,
                            basic_value REAL NOT NULL,
                            UNIQUE (ru_name, en_name, cur_code)
                        )""")
            con.execute("""CREATE TABLE IF NOT EXISTS countries(
                            name VARCHAR(50) NOT NULL,
                            cur_id INTEGER NOT NULL,
                            FOREIGN KEY (cur_id)  REFERENCES currencies (id)
                            UNIQUE (name, cur_id)
                        )""")
            con.execute("""CREATE TABLE IF NOT EXISTS curr_value(
                            cur_id INTEGER NOT NULL,
                            value REAL NOT NULL,
                            relative_value REAL NOT NULL,
                            datetime TEXT NOT NULL,
                            FOREIGN KEY (cur_id)  REFERENCES currencies (id),
                            UNIQUE (cur_id, datetime)
                        )""")

    def insert_currencies(self, currencies: list[Currency]):
        """
        Insert currencies into DB or update currency code or basic value

        :param currencies:
        :return: None
        """
        logger.debug("Inserting currencies in DB")
        with self.conn as con:
            for currency in currencies:
                con.execute("INSERT INTO currencies (ru_name, en_name, cur_code, basic_value) VALUES (?, ?, ?, ?)"
                            "ON CONFLICT DO UPDATE SET cur_code = ?, basic_value = ? WHERE cur_code IS DISTINCT FROM ? OR basic_value IS DISTINCT FROM ?",
                            (currency.ru_name, currency.en_name, currency.cur_code, currency.value, currency.cur_code,
                             currency.value, currency.cur_code, currency.value,))

    def insert_countries(self, countries_by_curr: dict[str, list[str]]):
        """
        Insert countries into DB or update country's currency

        :param countries_by_curr:
        :return: None
        """
        logger.debug("Inserting countries in DB")
        with self.conn as con:
            for curr_name, countries in countries_by_curr.items():
                cursor = con.cursor()
                cursor.execute("SELECT id FROM currencies WHERE ru_name = ?", (curr_name,))
                cur_id = cursor.fetchone()[0]
                for country in countries:
                    con.execute("INSERT INTO countries (name, cur_id) VALUES (?, ?)"
                                "ON CONFLICT DO UPDATE SET cur_id = ? WHERE cur_id IS DISTINCT FROM ?",
                                (country, cur_id, cur_id, cur_id))

    def insert_curr_values(self, currency_values: list[CurrencyValues]):
        """
        Insert currency values into DB or update its value or relative value

        :param currency_values:
        :return: None
        """
        logger.debug("Inserting currency values in DB")
        with self.conn as con:
            for currency_value in currency_values:
                cursor = con.cursor()
                cursor.execute("SELECT id FROM currencies WHERE en_name = ?", (currency_value.currency.en_name,))
                cur_id = cursor.fetchone()[0]
                for date_value, relative_value in zip(currency_value.values, currency_value.relative_values):
                    cur_datetime = date_value.date.strftime('%Y-%m-%d')
                    con.execute("INSERT INTO curr_value (cur_id, value, relative_value, datetime) VALUES (?, ?, ?, ?)"
                                "ON CONFLICT DO UPDATE SET value = ?, relative_value = ? WHERE value IS DISTINCT FROM ? OR relative_value IS DISTINCT FROM ?",
                                (cur_id, date_value.value, relative_value.value, cur_datetime, date_value.value,
                                 relative_value.value, date_value.value, relative_value.value))

    def get_all_countries(self) -> list[str]:
        """
        Get names of all countries from DB

        :return: list of countries
        """
        logger.debug("Getting all countries from DB")
        with self.conn as con:
            cursor = con.cursor()
            cursor.execute("SELECT name FROM countries")
            countries = cursor.fetchall()
            countries = [el[0] for el in countries]
            return countries

    def get_currencies_for_country(self, country: str, start_date, end_date) -> (int, list[DateValue]):
        """
        Get list of relative values and datetimes for given country and date between start and end date

        :param country:
        :param start_date:
        :param end_date:
        :return: tuple of currency id and list of DateValue objects
        """
        logger.debug("Getting currency values from DB for %s", country)
        with self.conn as con:
            cursor = con.cursor()
            cursor.execute("SELECT cur_id FROM countries WHERE name = ?", (country,))
            currency_id = cursor.fetchone()[0]

            cursor.execute("SELECT relative_value, datetime FROM curr_value WHERE cur_id = ? AND datetime BETWEEN ? AND ?",
                           (currency_id, start_date, end_date))
            db_data = cursor.fetchall()

            date_values = []
            for el in db_data:
                date_value = DateValue(value=el[0], date=el[1])
                date_values.append(date_value)

            return currency_id, date_values
