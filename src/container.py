from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Singleton, Factory

from src.settings.config import Settings
from src.database.sqlite import Database

from src.parsers.countries import CountryParser
from src.parsers.currency import CurrencyParser
from src.parsers.json_curr import JsonCurrParser


class AppContainer(DeclarativeContainer):
    currencies = JsonCurrParser().parse_county_curr()
    currency_parser: Singleton["CurrencyParser"] = Singleton(CurrencyParser, currencies=currencies)
    country_parser: Singleton["CountryParser"] = Singleton(CountryParser, currencies=currencies)
    app_settings: Singleton["Settings"] = Singleton(Settings)
    database: Factory["Database"] = Factory(Database)


APP_CONTAINER = AppContainer()
