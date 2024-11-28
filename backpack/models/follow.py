from backpack.db.orm.model import table, Model, Field, GenerationStrategy, ForeignKey
from backpack.db.orm.types import String

@table("Follow")
class Follow(Model):

    id = Field(String, column="followId", primary_key=True, generator=GenerationStrategy.UUID)
    user_id_1 = Field(String, column="userId1", required=True, foreign_key=ForeignKey("userId", String))
    user_id_2 = Field(String, column="userId2", required=True, foreign_key=ForeignKey("userId", String))

    def __init__(self, 
        user_id_1: String = None,
        user_id_2: String = None
    ):
        super().__init__(user_id_1=user_id_1, user_id_2=user_id_2)
