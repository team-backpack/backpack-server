from typing import Any
from backpack.db.orm.model import table, Model, Field, GenerationStrategy, ForeignKey
from backpack.db.orm.types import String

@table("Conversation")
class Conversation(Model):

    id = Field(String, column="conversationId", primary_key=True, generator=GenerationStrategy.UUID)
    user_id = Field(String, column="userId", required=True, foreign_key=ForeignKey("userId", String))

    def __init__(self,
        user_id: String = None
    ):
        super().__init__(user_id=user_id)