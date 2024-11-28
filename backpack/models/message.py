from backpack.db.orm.model import table, Model, Field, GenerationStrategy, ForeignKey
from backpack.db.orm.types import String, DateTime

@table("Message")
class Message(Model):

    id = Field(String, column="messageId", primary_key=True, generator=GenerationStrategy.UUID)
    conversation_id = Field(String, column="conversationId", required=True, foreign_key=ForeignKey("conversationId", String))
    content = Field(String, required=True)
    created_at = Field(DateTime, column="createdAt", required=True, default=DateTime.now())

    def __init__(self,
        conversation_id: String = None,
        content: String = None
    ):
        super().__init__(conversation_id=conversation_id, content=content)