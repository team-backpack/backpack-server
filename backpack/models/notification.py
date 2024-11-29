from backpack.db.orm.model import table, Model, Field, GenerationStrategy, ForeignKey
from backpack.db.orm.types import String

@table("Notification")
class Notification(Model):

    id = Field(String, column="notificationId", primary_key=True, generator=GenerationStrategy.UUID)
    user_id = Field(String, column="userId", required=True, foreign_key=ForeignKey("user_id", String))
    post_id = Field(String, column="postId", required=True, foreign_key=ForeignKey("post_id", String))
    content = Field(String, required=True)
    type = Field(String, required=True)

    def __init__(self,
        user_id: String = None,
        post_id: String = None,
        content: String = None,
        type: String = None
    ):
        super().__init__(user_id=user_id, post_id=post_id, content=content, type=type)
    