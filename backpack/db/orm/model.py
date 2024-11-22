from backpack.db.orm.field import Field, GenerationStrategy
from backpack.db.orm.types import MappedType
from backpack.db.connection import *

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

    def __init__(self, **args):
        for field_name, field in self.__fields__.items():
            
            if field.generator == GenerationStrategy.UUID:
                setattr(self, field_name, args.get(field_name, str(field.generator())))
            else:
                setattr(self, field_name, args.get(field_name, field.default))

        self.create_table()

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
    def _build_where_clause(self, where: dict):
        fields = {k: v.column for k, v in self.__fields__.items()} 
        valid_keys = [key for key in where.keys() if key in fields]
        valid_columns = [fields[key] for key in valid_keys]
        clause = " AND ".join([f"{key} = %s" for key in valid_columns])
        params = [where[key] for key in valid_keys]
        return clause, params

    @property
    def id(self):
        primary_key = next((field for field in self.__fields__.values() if field.primary_key), None)
        return getattr(self, primary_key.column)

    @classmethod
    def create_table(self):
        fields = [f"{field.column} {field.sqlize()}" for _, field in self.__fields__.items()]
        query = f"CREATE TABLE IF NOT EXISTS {self.__tablename__} ({', '.join(fields)});"

        with create_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query)
                conn.commit()

    def insert(self):
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
        where_clause, params = self._build_where_clause(where)

        sql = f"""
            SELECT * FROM {self.__tablename__}
            {f"WHERE {where_clause}" if where_clause else ""}
            LIMIT 1
        """

        with create_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute(sql, params)
                return self.__generate_model(cursor.fetchone())

    @classmethod         
    def find_all(self, **where):
        where_clause, params = self._build_where_clause(where)

        sql = f"""
            SELECT * FROM {self.__tablename__}
            {f"WHERE {where_clause}" if where_clause else ""}
        """

        with create_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute(sql, params)
                return [self.__generate_model(model) for model in cursor.fetchall()]

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
        where_clause, params = self._build_where_clause(where)

        sql = f"""
            DELETE FROM {self.__tablename__}
            WHERE {where_clause}
        """
        
        with create_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, params)
                conn.commit()

    @classmethod
    def __generate_model(cls, result: dict):
        if not result:
            return None
        instance = cls()
        for column, value in result.items():
            field_name = next((k for k, v in cls.__fields__.items() if v.column == column), None)
            if cls.__fields__[field_name].foreign_key:
                primary_key_name = next(name for name, field in cls.__fields__[field_name].mapped.__fields__.items() if field.primary_key)
                fk = cls.__fields__[field_name].mapped.find_one(where={ primary_key_name: value })
                setattr(instance, field_name, fk)
            else:
                setattr(instance, field_name, value)
        return instance
    
    def __str__(self):
        return f"{self.__class__.__name__} ({", ".join(f'{field}: {getattr(self, field)}' for field in self.__fields__.keys())})"

def table(name: str):
    def wrapper(cls):
        cls.__tablename__ = name
        return cls
    return wrapper