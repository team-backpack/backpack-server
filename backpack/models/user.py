from backpack.db import orm

@orm.table("User")
class User(orm.Model):

    id = orm.Field(orm.String, column="userId", primary_key=True, generator=orm.GenerationStrategy.UUID)
    username: str = orm.Field(orm.String(25), required=True, unique=True)
    display_name = orm.Field(orm.String(50), column="displayName")
    email = orm.Field(orm.String(50), required=True, unique=True)
    password = orm.Field(orm.String, required=True)
    birth_date = orm.Field(orm.Date, column="birthDate", required=True)
    verification_token = orm.Field(orm.String, column="verificationToken")
    verified = orm.Field(orm.Boolean, required=True, default=False)
    created_at = orm.Field(orm.DateTime, column="createdAt", required=True, default=orm.DateTime.now())
    updated_at = orm.Field(orm.DateTime, column="updatedAt", required=True, default=orm.DateTime.now())