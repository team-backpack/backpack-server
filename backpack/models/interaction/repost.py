from backpack.db.orm.model import table, Model, Field, GenerationStrategy, ForeignKey
from backpack.db.orm.types import String, Integer
from backpack.models.post import Post

@table("Repost")
class Repost(Model):

    id = Field(Integer, column="likeId", primary_key=True, generator=GenerationStrategy.INCREMENT)
    post = Field(Post, column="postId", foreign_key=ForeignKey("postId", String))
    reposted = Field(Post, column="repostedId", required=True, foreign_key=ForeignKey("postId", String))

    def __init__(self, 
        post: Post = None,
        reposted: Post = None
    ):
        super().__init__(post=post, reposted=reposted)

    def to_dict(self):
        return {
            "post": self.post.to_dict() if self.post else None,
            "reposted": self.reposted.to_dict(),
        }