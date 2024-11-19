from typing import TypeVar
from backpack.models.user import User

class Field:

    def __init__(self, type: str, name: str = "", required: bool = False, unique: bool = False, primary_key: bool = False, foreign_key: dict = {}):
        self.name = name
        self.type = type
        self.required = required
        self.unique = unique
        self.primary_key = primary_key
        self.foreign_key = foreign_key

    def sqlize(self):
        return f"""
            {self.type} {"NOT NULL" if self.required else ""} {"UNIQUE" if self.unique else ""} 
            {f"\nPRIMARY KEY ({self.name})" if self.primary_key else ""} 
            {f"\nFOREIGN KEY ({self.name}) REFERENCES {self.foreign_key["table"]}({self.foreign_key["field"]})" if self.foreign_key else ""}
        """.strip()

class IntegerField(Field):
    def __init__(self, name: str = "", required: bool = False, unique: bool = False, primary_key: bool = False,  foreign_key: dict = {}):
        super().__init__(type="INT", name=name, required=required, unique=unique, primary_key=primary_key, foreign_key=foreign_key)


class StringField(Field):
    def __init__(self, name: str = "", max_length: int = 255, required: bool = False, unique: bool = False, primary_key: bool = False,  foreign_key: dict = {}):
        super().__init__(type=f"VARCHAR({max_length})", name=name, required=required, unique=unique, primary_key=primary_key, foreign_key=foreign_key)

id = IntegerField(name="post_id", required=True, foreign_key={ "table": "Post", "field": "post_id" })


class ModelMeta(type):
    def __new__(cls, name, bases, dct):
        if name == 'Model':
            return super().__new__(cls, name, bases, dct)

        fields = {v.name if v.name else k: v for k, v in dct.items() if isinstance(v, Field)}
        dct["__fields__"] = fields
        dct["__tablename__"]
        return super().__new__(cls, name, bases, dct)

class Model(metaclass=ModelMeta):

    @classmethod
    def create_table(self):
        fields = [f"{name} {field.sqlize()}" for name, field in self.__fields__.items()]
        query = f"CREATE TABLE IF NOT EXISTS {self.__tablename__} ({', '.join(fields)});"
        print(query)

class Person(Model):
    __tablename__ = "person"

    name = StringField(max_length=50)
    age = IntegerField()
    id = StringField(name="person_id", primary_key=True)

Person.create_table()

T = User

class Repository:

    TABLE_NAME = ""

    def insert(self, model: T):
        columns = list(model.__dict__.keys())
        values = tuple(model.__dict__.values())

        sql = f"""
            INSERT INTO {self.TABLE_NAME} ({", ".join(columns)})
            VALUES ({", ".join(["%s"] * len(values))})
        """
        print(sql, values)

    def find_one(self, where: dict = {}):
        where_clause = " AND ".join([f"{key if key != "id" else self.TABLE_NAME.lower() + "_id"} = %s" for key in where.keys()])
        values = tuple(where.values())

        sql = f"""
            SELECT * FROM {self.TABLE_NAME}
            WHERE {where_clause}
            LIMIT 1
        """
        print(sql, values)

    def find_all(self, where: dict = {}):
        where_clause = " AND ".join([f"{key if key != "id" else self.TABLE_NAME.lower() + "_id"} = %s" for key in where.keys()])
        values = tuple(where.values())

        sql = f"""
            SELECT * FROM {self.TABLE_NAME}
            WHERE {where_clause}
        """
        print(sql, values)

    def update(self, model: T):

        formatted_keys = [key.lower().replace(f"_{self.TABLE_NAME}__", "") for key in model.__dict__.keys()]

        sql = f"""
            UPDATE {self.TABLE_NAME}
            SET {", ".join([f"{key} = %s" for key in formatted_keys if key != "id"])}
            WHERE {self.TABLE_NAME.lower() + "_id"} = {model.id}
        """
        print(sql)

    def delete(self, where: dict = {}):
        where_clause = " AND ".join([f"{key if key != "id" else self.TABLE_NAME.lower() + "_id"} = %s" for key in where.keys()])

        sql = f"""
            DELETE FROM {self.TABLE_NAME}
            WHERE {where_clause}
        """
        print(sql, where.values())


class UserRepository(Repository):
    TABLE_NAME = "User"