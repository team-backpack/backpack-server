from backpack.db.orm.model import table, Model, Field, GenerationStrategy, ForeignKey
from backpack.db.orm.types import String, Boolean, DateTime
from backpack.utils.token import token

@table("ChangePasswordRequest")
class ChangePasswordRequest(Model):

    id = Field(String, column="changePasswordRequestId", primary_key=True, generator=GenerationStrategy.UUID)
    user_id = Field(String(36), column="userId", required=True, foreign_key=ForeignKey("userId", String))
    validated = Field(Boolean, default=False)
    validation_token = Field(String(36), column="validationToken")
    validation_date = Field(DateTime, column="createdAt", required=True, default=DateTime.now())

    def __init__(self, 
        user_id: String = None
    ):
        super().__init__(user_id=user_id)

    def generate_validation_token(self):
        self.verification_token = token()
        self.token_sent_at = DateTime.now()

        return self.verification_token