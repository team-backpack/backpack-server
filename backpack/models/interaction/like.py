from backpack.db.orm.model import table, Model, Field, GenerationStrategy, ForeignKey
from backpack.db.orm.types import String, Integer
from backpack.models.user import User
from backpack.models.post import Post

@table("Likes")
class Like(Model):

    id = Field(Integer, column="likeId", primary_key=True, generator=GenerationStrategy.INCREMENT)
    user = Field(User, column="userId", required=True, foreign_key=ForeignKey("userId", String))
    post = Field(Post, column="postId", required=True, foreign_key=ForeignKey("postId", String))

    def __init__(self, 
        user: User = None,
        post: Post = None
    ):
        super().__init__(user=user, post=post)