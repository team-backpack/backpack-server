from backpack.db.orm.model import table, Model, Field, GenerationStrategy, ForeignKey
from backpack.db.orm.types import String, DateTime, Integer, Boolean

@table("Post")
class Post(Model):

    id = Field(String, column="postId", primary_key=True, generator=GenerationStrategy.UUID)
    user_id = Field(String(36), column="userId", required=True, foreign_key=ForeignKey("userId", String))
    text = Field(String)
    content_url = Field(String, column="contentUrl")
    likes = Field(Integer, required=True, default=0)
    is_shared_post = Field(Boolean, column="isSharedPost", required=True)
    was_edited = Field(Boolean, column="wasEdited",  required=True, default=False)
    created_at = Field(DateTime, column="createdAt", required=True, default=DateTime.now())
    updated_at = Field(DateTime, column="updatedAt", required=True, default=DateTime.now())

    def __init__(self,
        user_id: String = None,
        text: String = None,
        content_url: String = None,
        is_shared_post: Boolean = None
    ):
        super().__init__(user_id=user_id, text=text, content_url=content_url, is_shared_post=is_shared_post)
