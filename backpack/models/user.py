from backpack.db.orm.model import table, Model, Field, GenerationStrategy
from backpack.db.orm.types import String, Date, DateTime, Boolean

@table("User")
class User(Model):

    id = Field(String, column="userId", primary_key=True, generator=GenerationStrategy.UUID)
    username = Field(String(25), required=True, unique=True)
    display_name = Field(String(50), column="displayName")
    email = Field(String(50), required=True, unique=True)
    password = Field(String, required=True)
    birth_date = Field(Date, column="birthDate", required=True)
    verification_token = Field(String, column="verificationToken")
    verified = Field(Boolean, required=True, default=False)
    created_at = Field(DateTime, column="createdAt", required=True, default=DateTime.now())
    updated_at = Field(DateTime, column="updatedAt", required=True, default=DateTime.now())

    def __init__(self, 
        username: String = None,
        display_name: String = None,
        email: String = None,
        password: String = None,
        birth_date: Date = None,
    ):
        super().__init__(username=username, display_name=display_name, email=email, password=password, birth_date=birth_date)

print(User.select().where(id="62b5d10f-0f9b-48a7-934c-9e599a3828c7").one())