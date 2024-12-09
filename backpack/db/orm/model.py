from backpack.db.orm.types import MappedType
from backpack.db.connection import create_connection
from enum import Enum
from uuid import uuid4
import nanoid
from datetime import date, datetime

class ModelMeta(type):
    def __new__(cls, name, bases, dct):
        if name == "Model":
            return super().__new__(cls, name, bases, dct)

        fields = {}
        for k, v in dct.items():
            if isinstance(v, Field):
                if not v.column:
                    v.column = k
                fields[k] = v

        dct["__fields__"] = fields
        dct["__tablename__"] = dct.get("__tablename__", name)

        cls_instance = super().__new__(cls, name, bases, dct)
        cls_instance._cached_fields = fields

        return cls_instance


class Model(metaclass=ModelMeta):

    _tables_created = False

    def __init__(self, **args):

        for field_name, field in self.__fields__.items():
            
            if field.generator == GenerationStrategy.UUID or field.generator == GenerationStrategy.NANOID:
                setattr(self, field_name, args.get(field_name, str(field.generator())))
            else:
                setattr(self, field_name, args.get(field_name, field.default))

    def __setattr__(self, name, value):
        if name in self.__fields__:
            field = self.__fields__[name]
            expected_type = None

            if isinstance(field.mapped, MappedType):
                expected_type = field.mapped.type
            elif isinstance(field.mapped, type) and issubclass(field.mapped, Model):
                expected_type = field.mapped

            if value is not None and expected_type and not isinstance(value, expected_type):
                raise ValueError(f"Invalid type for field {name}: expected {expected_type}, got {type(value)}")
            
        super().__setattr__(name, value)

    def __getattr__(self, name):
        if name in self.__fields__ and isinstance(self.__fields__[name].mapped, Model):
            foreign_key_field = self.__fields__[name].foreign_key.references
            related_class = self.__fields__[name].mapped
            return related_class.find_one({foreign_key_field: getattr(self, name)})
        raise AttributeError(f"{name} not found")

    @classmethod
    def _build_where_clause(self, **where):
        fields = {k: v.column for k, v in self.__fields__.items()}
        valid_keys = [key for key in where.keys() if key in fields]
        valid_columns = [fields[key] for key in valid_keys]
        clause = " AND ".join([f"{key} = %s" for key in valid_columns])
        params = [where[key].id if issubclass(type(where[key]), Model) else where[key] for key in valid_keys]
        return clause, params

    @property
    def id(self):
        primary_key = next((field for field in self.__fields__.values() if field.primary_key), None)
        return getattr(self, primary_key.column)

    @classmethod
    def create_table(self):
        if self._tables_created:
            return

        fields = [f"{field.column} {field.sqlize()}" for _, field in self.__fields__.items()]
        query = f"CREATE TABLE IF NOT EXISTS {self.__tablename__} ({', '.join(fields)});"

        with create_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query)
                conn.commit()

        self._tables_created = True

    def insert(self):
        self.create_table()
        
        params = []
        for name in self.__fields__.keys():
            value = getattr(self, name, None)
            if isinstance(value, Model):
                value = value.id if value else None
            params.append(value)

        columns = tuple([field.column for field in self.__fields__.values() if field is not None])

        sql = f"""
            INSERT INTO {self.__tablename__} ({", ".join(columns)})
            VALUES ({", ".join(["%s"] * len(params))})
        """

        with create_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, params)
                
                primary_key = next(field for field in self.__fields__.values() if field.primary_key)
                if primary_key.generator == GenerationStrategy.INCREMENT:
                    setattr(self, primary_key.column, cursor.lastrowid)
                conn.commit()

    @classmethod
    def find_one(self, **where):
        self.create_table()

        where_clause, params = self._build_where_clause(**where)

        sql = f"""
            SELECT * FROM {self.__tablename__}
            {f"WHERE {where_clause}" if where_clause else ""}
            LIMIT 1
        """

        with create_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute(sql, params)
                return self._generate_model(cursor.fetchone())

    @classmethod         
    def find_all(self, **where):
        self.create_table()

        where_clause, params = self._build_where_clause(**where)

        sql = f"""
            SELECT * FROM {self.__tablename__}
            {f"WHERE {where_clause}" if where_clause else ""}
        """

        with create_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute(sql, params)
                return [self._generate_model(model) for model in cursor.fetchall()]

    def update(self):
        params = [getattr(self, key).id if isinstance(getattr(self, key), Model) else getattr(self, key) for key in self.__fields__.keys() if not self.__fields__[key].primary_key]

        sql = f"""
            UPDATE {self.__tablename__}
            SET {", ".join([f"{field.column} = %s" for field in self.__fields__.values() if not field.primary_key])}
            WHERE {next(field.column for field in self.__fields__.values() if field.primary_key)} = %s
        """

        params.append(self.id)
        
        with create_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, tuple(params))
                conn.commit()

    @classmethod
    def delete(self, **where):
        self.create_table()
        
        where_clause, params = self._build_where_clause(**where)

        sql = f"""
            DELETE FROM {self.__tablename__}
            WHERE {where_clause}
        """
        
        with create_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, params)
                conn.commit()

    @classmethod
    def _generate_model(cls, result: dict):
        if not result:
            return None
        instance = cls()
        for column, value in result.items():
            field_name = next((k for k, v in cls.__fields__.items() if v.column == column), None)
            if not field_name:
                continue
            is_model_fk = cls.__fields__.get(field_name).foreign_key and issubclass(cls.__fields__.get(field_name).mapped, Model)
            if is_model_fk and value != None:
                primary_key_name: str = [name for name, field in cls.__fields__[field_name].mapped.__fields__.items() if field.primary_key][0]
                fk = cls.__fields__[field_name].mapped.find_one(**{primary_key_name: value})
                setattr(instance, field_name, fk)
            else:
                setattr(instance, field_name, value)
        return instance
    
    @classmethod
    def select(self):
        self.create_table()

        query_parts = {
            "select": f"SELECT * FROM {self.__tablename__}",
            "where": "",
            "order_by": "",
            "join": "",
            "limit": ""
        }
        params = []

        class QueryBuilder:
            def __init__(self, model: Model):
                self.model = model
                self.related_model: Model = None

            def where(self, **conditions):
                clause, where_params = self.model._build_where_clause(**conditions)
                query_parts["where"] = f"WHERE {clause}" if clause else ""
                params.extend(where_params)
                return self

            def order_by(self, *columns, descending=False):
                fields = {k: v.column for k, v in self.model.__fields__.items()}
                valid_columns = [fields[col] for col in columns if col in fields]
                if valid_columns:
                    direction = "DESC" if descending else "ASC"
                    query_parts["order_by"] = f"ORDER BY {', '.join(valid_columns)} {direction}"
                return self

            def join(self, related_model: Model, on_field: str, to_field: str):
                self.related_model = related_model
                related_table = related_model.__tablename__
                on_column = self.model.__fields__[on_field].column
                to_column = related_model.__fields__[to_field].column
                query_parts["join"] += f" INNER JOIN {related_table} ON {self.model.__tablename__}.{on_column} = {related_table}.{to_column}"
                return self

            def execute(self, limit: int = None):
                if limit:
                    query_parts["limit"] = f"LIMIT {limit}"

                query = " ".join(part for part in query_parts.values() if part)
                with create_connection() as conn:
                    with conn.cursor(dictionary=True) as cursor:
                        cursor.execute(query, tuple(params))
                        return self.model._generate_model(cursor.fetchone()) \
                                if limit == 1 \
                                else [self.model._generate_model(row) if not self.related_model else (self.model._generate_model(row), self.related_model._generate_model(row)) for row in cursor.fetchall()]

            def one(self):
                return self.execute(limit=1)

        return QueryBuilder(self)
    
    def __str__(self):
        att = ", ".join(f'{field}: {getattr(self, field)}' for field in self.__fields__.keys())
        return f"{self.__class__.__name__} ({att})"

def table(name: str):
    def wrapper(cls):
        cls.__tablename__ = name
        return cls
    return wrapper


class GenerationStrategy(Enum):
    UUID = uuid4
    NANOID = nanoid.generate
    INCREMENT = None


class ForeignKey:

    def __init__(self, references: str, type: MappedType = None, table: Model = None, table_name: str = None):
        self.references = references
        self.type = type
        self.table = table
        self.table_name = table_name


class Field:
    
    def __init__(self, mapped: MappedType | Model, column: str = "", required: bool = False, unique: bool = False, primary_key: bool = False, foreign_key: ForeignKey = None, default: MappedType | type = None, generator: GenerationStrategy = None):
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
        
        default = ""
        if self.default and not isinstance(self.default, (date, datetime, bool)):
            default = f"DEFAULT {self.default}"
        elif isinstance(self.default, datetime):
            default = "DEFAULT CURRENT_TIMESTAMP"
        elif isinstance(self.default, date):
            default = "DEFAULT CURRENT_DATE"
        elif isinstance(self.default, bool):
            default = "DEFAULT TRUE" if self.default else "DEFAULT FALSE"

        auto_increment = "AUTO_INCREMENT" if self.generator == GenerationStrategy.INCREMENT else ""
        primary_key = "PRIMARY KEY" if self.primary_key else ""

        foreign_key = ""
        if self.foreign_key:
            if issubclass(self.mapped, Model):
                table = self.mapped.__tablename__
            elif self.foreign_key.table:
                table = self.foreign_key.table.__tablename__
            else: table = self.foreign_key.table_name
            foreign_key = (
                f", FOREIGN KEY ({self.column}) REFERENCES {table}({self.foreign_key.references}) ON DELETE CASCADE"
            )

        return " ".join(filter(None, [self.mapped.name if not self.foreign_key else self.foreign_key.type.name, not_null, unique, default, auto_increment, primary_key, foreign_key]))
    
    def __str__(self):
        att = ", ".join(f"{key}: {value}" for key, value in self.__dict__.items())
        return f"{self.__class__.__name__} ({att})"