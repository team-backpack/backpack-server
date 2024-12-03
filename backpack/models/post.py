from backpack.db.orm.model import table, Model, Field, GenerationStrategy, ForeignKey
from backpack.db.orm.types import String, DateTime, Integer, Boolean
from backpack.models.user import User

@table("Post")
class Post(Model):

    id = Field(String, column="postId", primary_key=True, generator=GenerationStrategy.NANOID)
    user = Field(User, column="userId", required=True, foreign_key=ForeignKey("userId", String))
    text = Field(String)
    content_url = Field(String, column="contentUrl")
    likes = Field(Integer, required=True, default=0)
    shares = Field(Integer, required=True, default=0)
    comments = Field(Integer, required=True, default=0)
    is_shared_post = Field(Boolean, column="isSharedPost", required=True, default=False)
    was_edited_at = Field(DateTime, column="wasEditedAt")
    created_at = Field(DateTime, column="createdAt", required=True, default=DateTime.now())
    updated_at = Field(DateTime, column="updatedAt", required=True, default=DateTime.now())

    def __init__(self,
        user: User = None,
        text: String = None,
        content_url: String = None,
        is_shared_post: Boolean = False
    ):
        super().__init__(user=user, text=text, content_url=content_url, is_shared_post=is_shared_post)

    def to_dict(self):
        return {
            "postId": self.id,
            "user": self.user.to_dict(),
            "text": self.text,
            "contentURL": self.content_url,
            "likes": self.likes,
            "shares": self.shares,
            "comments": self.comments,
            "wasEditedAt": self.was_edited_at,
            "isSharedPost": self.is_shared_post,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at
        }