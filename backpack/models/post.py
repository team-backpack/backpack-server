from backpack.db.orm.model import table, Model, Field, GenerationStrategy, ForeignKey
from backpack.db.orm.types import String, DateTime, Integer, Boolean
from backpack.models.user import User

@table("Post")
class Post(Model):

    id = Field(String, column="postId", primary_key=True, generator=GenerationStrategy.NANOID)
    user = Field(User, column="userId", required=True, foreign_key=ForeignKey("userId", String))
    text = Field(String)
    media_url = Field(String, column="contentUrl")
    likes = Field(Integer, required=True, default=0)
    reposts = Field(Integer, required=True, default=0)
    comments = Field(Integer, required=True, default=0)
    is_shared_post = Field(Boolean, column="isSharedPost", required=True, default=False)
    was_edited_at = Field(DateTime, column="wasEditedAt")
    created_at = Field(DateTime, column="createdAt", required=True, default=DateTime.now())
    updated_at = Field(DateTime, column="updatedAt", required=True, default=DateTime.now())

    def __init__(self,
        user: User = None,
        text: String = None,
        media_url: String = None,
        is_shared_post: Boolean = False
    ):
        super().__init__(user=user, text=text, media_url=media_url, is_shared_post=is_shared_post)

    def to_dict(self, show_user: bool = True):
        result = {
            "postId": self.id,
            "text": self.text,
            "mediaURL": self.media_url,
            "likes": self.likes,
            "reposts": self.reposts,
            "comments": self.comments,
            "wasEditedAt": self.was_edited_at,
            "isSharedPost": self.is_shared_post,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at
        }

        if show_user:
            result["user"] = self.user.to_dict()

        return result