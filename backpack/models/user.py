from datetime import date, datetime

class User:

    def __init__(
        self, 
        id: str = None,
        username: str = None, 
        display_name: str = None, 
        email: str = None, 
        password: str = None, 
        birth_date: date = None, 
        verification_token: str = None, 
        verified: bool = None, 
        created_at: datetime = None
    ):
        self.__id = id
        self.__username = username
        self.__display_name = display_name
        self.__email = email
        self.__password = password
        self.__birth_date = birth_date
        self.__verification_token = verification_token
        self.__verified = verified
        self.__created_at = created_at

    @property
    def id(self):
        return self.__id

    @id.setter
    def id(self, value):
        self.__id = value

    @property
    def username(self):
        return self.__username

    @username.setter
    def username(self, value):
        self.__username = value

    @property
    def display_name(self):
        return self.__display_name

    @display_name.setter
    def display_name(self, value):
        self.__display_name = value

    @property
    def email(self):
        return self.__email

    @email.setter
    def email(self, value):
        self.__email = value

    @property
    def password(self):
        return self.__password

    @password.setter
    def password(self, value):
        self.__password = value

    @property
    def birth_date(self):
        return self.__birth_date

    @birth_date.setter
    def birth_date(self, value):
        self.__birth_date = value

    @property
    def verification_token(self):
        return self.__verification_token

    @verification_token.setter
    def verification_token(self, value):
        self.__verification_token = value

    @property
    def verified(self):
        return self.__verified

    @verified.setter
    def verified(self, value):
        self.__verified = value

    @property
    def created_at(self):
        return self.__created_at

    @created_at.setter
    def created_at(self, value):
        self.__created_at = value