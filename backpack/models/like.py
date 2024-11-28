from backpack.db.orm.model import table, Model, Field, GenerationStrategy, ForeignKey
from backpack.db.orm.types import String, Integer

@table("Like")
class Like(Model):

    id = Field(String, column="likeId", primary_key=True, generator=GenerationStrategy.UUID)
    user_id = Field(String(36), column="userId", required=True, foreign_key=ForeignKey("userId", String))
    post_id = Field(String(36), column="postId", required=True, foreign_key=ForeignKey("postId", String))

    def __init__(self, 
        user_id: String = None,
        post_id: String = None
    ):
        super().__init__(user_id=user_id, post_id=post_id)