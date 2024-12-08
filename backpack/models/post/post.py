from backpack.db.orm.model import table, Model, Field, GenerationStrategy, ForeignKey
from backpack.db.orm.types import String, DateTime, Integer, Boolean
from backpack.models.user import User
from backpack.models.profile.profile import Profile

@table("Post")
class Post(Model):

    id = Field(String, column="postId", primary_key=True, generator=GenerationStrategy.NANOID)
    user_id = Field(String, column="userId", required=True, foreign_key=ForeignKey("userId", String, table=User))
    text = Field(String)
    media_url = Field(String, column="mediaURL")
    likes = Field(Integer, required=True, default=0)
    reposts = Field(Integer, required=True, default=0)
    comments = Field(Integer, required=True, default=0)
    is_repost = Field(Boolean, column="isRepost", required=True, default=False)
    reposted_id = Field(String, column="repostedId", foreign_key=ForeignKey("postId", String, table_name="Post"))
    was_edited_at = Field(DateTime, column="wasEditedAt")
    created_at = Field(DateTime, column="createdAt", required=True, default=DateTime.now())
    updated_at = Field(DateTime, column="updatedAt", required=True, default=DateTime.now())

    def __init__(self,
        user_id: String = None,
        text: String = None,
        media_url: String = None,
        is_repost: Boolean = False,
        reposted_id: String = None
    ):
        super().__init__(user_id=user_id, text=text, media_url=media_url, is_repost=is_repost, reposted_id=reposted_id)

    def to_dict(self, show_profile: bool = True):
        if self.is_repost and not (self.text or self.media_url):
            result = {
                "postId": self.id,
                "isRepost": self.is_repost,
                "reposted": self.find_one(id=self.reposted_id).to_dict() if self.reposted_id else None,
                "createdAt": self.created_at
            }
        else:
            result = {
                "postId": self.id,
                "text": self.text,
                "mediaURL": self.media_url,
                "likes": self.likes,
                "reposts": self.reposts,
                "comments": self.comments,
                "wasEditedAt": self.was_edited_at,
                "isRepost": self.is_repost,
                "reposted": self.find_one(id=self.reposted_id).to_dict() if self.reposted_id else None,
                "createdAt": self.created_at,
                "updatedAt": self.updated_at
            }

        if show_profile:
            result["profile"] = Profile.find_one(user_id=self.user_id).to_dict()

        return result