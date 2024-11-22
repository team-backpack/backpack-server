from typing import TypeVar
from datetime import date, datetime

T = TypeVar("T", int, float, str, date, datetime)

class MappedType:
    type: T = None
    name = ""

class Integer(MappedType, int):
    type = int
    name = "INTEGER"

class String(MappedType, str):
    type = str
    max_length = 255
    name = f"VARCHAR({max_length})"

    def __init__(self, max_length: int = 255):
        self.max_length = max_length
        self.name = f"VARCHAR({max_length})"

class Date(MappedType, date):
    type = date
    name = "DATE"
    
    @staticmethod
    def today():
        return date.today()
    
    @staticmethod
    def of(day: int, month: int, year: int):
        return date(year, month, day)

class DateTime(MappedType, datetime):
    type = datetime
    name = "DATETIME"
    
    @staticmethod
    def now():
        return datetime.now()

class Boolean(MappedType):
    type = bool
    name = "BOOLEAN"