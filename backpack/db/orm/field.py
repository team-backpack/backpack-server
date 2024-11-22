from enum import Enum
from uuid import uuid4
from backpack.db.orm.types import *
from backpack.db.orm.model import Model

class GenerationStrategy(Enum):
    UUID = uuid4
    INCREMENT = None


class ForeignKey:

    def __init__(self, references: str, type: MappedType):
        self.references = references
        self.type = type


class Field:

    def __init__(self, mapped: MappedType | Model, column: str = "", required: bool = False, unique: bool = False, primary_key: bool = False, foreign_key: ForeignKey = None, default: T = None, generator: GenerationStrategy = None):
        self.column = column
        self.required = required
        self.unique = unique
        self.primary_key = primary_key
        self.foreign_key = foreign_key
        self.mapped = mapped
        self.default = default
        self.generator = generator

    def sqlize(self):
        not_null = "NOT NULL" if self.required else ""
        unique = "UNIQUE" if self.unique else ""
        default = (
            f"DEFAULT {self.default}"
            if self.default and not isinstance(self.default, (date, datetime))
            else "DEFAULT CURRENT_DATE()"
            if isinstance(self.default, date)
            else "DEFAULT CURRENT_TIMESTAMP"
            if isinstance(self.default, datetime)
            else ""
        )
        auto_increment = "AUTO_INCREMENT" if self.generator == GenerationStrategy.INCREMENT else ""
        primary_key = "PRIMARY KEY" if self.primary_key else ""
        foreign_key = (
            f", FOREIGN KEY ({self.column}) REFERENCES {self.mapped.__tablename__}({self.foreign_key.references}) ON DELETE CASCADE"
            if self.foreign_key
            else ""
        )

        return " ".join(filter(None, [self.mapped.name if not self.foreign_key else self.foreign_key.type.name, not_null, unique, default, auto_increment, primary_key, foreign_key]))
    
    def __str__(self):
        return f"{self.__class__.__name__} ({", ".join(f"{key}: {value}" for key, value in self.__dict__.items())})"