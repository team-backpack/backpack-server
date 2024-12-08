from backpack.db.orm.model import table, Model, Field, GenerationStrategy, ForeignKey
from backpack.db.orm.types import String, Integer
from backpack.models.user import User
from backpack.models.post.post import Post

@table("Likes")
class Like(Model):

    id = Field(Integer, column="likeId", primary_key=True, generator=GenerationStrategy.INCREMENT)
    user_id = Field(String, column="userId", required=True, foreign_key=ForeignKey("userId", String, table=User))
    post_id = Field(String, column="postId", required=True, foreign_key=ForeignKey("postId", String, table=Post))

    def __init__(self, 
        user_id: String = None,
        post_id: String = None
    ):
        super().__init__(user_id=user_id, post_id=post_id)