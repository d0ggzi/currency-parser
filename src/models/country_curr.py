from datetime import datetime

from pydantic import BaseModel


class Currency(BaseModel):
    ru_name: str
    en_name: str
    cur_code: int
    value: float


class CountriesByCurrency(BaseModel):
    currency: Currency
    countries: list[str] = []


class DateValue(BaseModel):
    date: datetime
    value: float


class CurrencyValues(BaseModel):
    currency: Currency
    values: list[DateValue] = []
    relative_values: list[DateValue] = []
