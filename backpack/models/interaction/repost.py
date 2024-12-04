from backpack.db.orm.model import table, Model, Field, GenerationStrategy, ForeignKey
from backpack.db.orm.types import String, Integer
from backpack.models.post import Post
from backpack.models.user import User

@table("Repost")
class Repost(Model):

    id = Field(Integer, column="repostId", primary_key=True, generator=GenerationStrategy.INCREMENT)
    post = Field(Post, column="postId", foreign_key=ForeignKey("postId", String))
    reposted = Field(Post, column="repostedId", required=True, foreign_key=ForeignKey("postId", String))
    user = Field(User, column="userId", required=True, foreign_key=ForeignKey("userId", String))

    def __init__(self, 
        user: User = None,
        post: Post = None,
        reposted: Post = None
    ):
        super().__init__(user=user, post=post, reposted=reposted)

    def to_dict(self, show_user: bool = True):
        result = {
            "post": self.post.to_dict() if self.post else None,
            "reposted": self.reposted.to_dict()
        }

        if show_user:
            result["user"] = self.user.to_dict()

        return result