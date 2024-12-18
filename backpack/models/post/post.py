from backpack.db.orm.model import table, Model, Field, GenerationStrategy, ForeignKey, Default
from backpack.db.orm.types import String, DateTime, Integer, Boolean
from backpack.models.user import User
from backpack.models.profile.profile import Profile
from backpack.models.post.media import Media

@table("Post")
class Post(Model):

    id = Field(String, column="postId", primary_key=True, generator=GenerationStrategy.NANOID)
    user_id = Field(String, column="userId", required=True, foreign_key=ForeignKey("userId", String, table=User))
    text = Field(String)
    likes = Field(Integer, required=True, default=0)
    reposts = Field(Integer, required=True, default=0)
    comments = Field(Integer, required=True, default=0)
    is_repost = Field(Boolean, column="isRepost", required=True, default=False)
    reposted_id = Field(String, column="repostedId", foreign_key=ForeignKey("postId", String, table_name="Post"))
    repost_type = Field(String, column="repostType")
    commented_id = Field(String, column="commentedId", foreign_key=ForeignKey("postId", String, table_name="Post"))
    was_edited_at = Field(DateTime, column="wasEditedAt")
    created_at = Field(DateTime, column="createdAt", required=True, default=Default.NOW)
    updated_at = Field(DateTime, column="updatedAt", required=True, default=Default.NOW)

    def __init__(self,
        user_id: String = None,
        text: String = None,
        is_repost: Boolean = False,
        reposted_id: String = None,
        commented_id: String = None
    ):
        repost_type = None
        if is_repost:
            repost_type = "quote" if text else "simple"

        super().__init__(user_id=user_id, text=text, is_repost=is_repost, reposted_id=reposted_id, commented_id=commented_id, repost_type=repost_type)

    def to_dict(self, show_profile: bool = True, show_commented: bool = False, show_reposted: bool = False, show_parents_ids: bool = True):
        if self.repost_type == "simple":
            result = {
                "postId": self.id,
                "isRepost": self.is_repost,
                "repostType": self.repost_type,
                "reposted": self.find_one(id=self.reposted_id).to_dict() if self.reposted_id else None,
                "createdAt": self.created_at
            }
        else:
            result = {
                "postId": self.id,
                "text": self.text,
                "mediaURLs": [media.url for media in Media.find_all(post_id=self.id)],
                "likes": self.likes,
                "reposts": self.reposts,
                "comments": self.comments,
                "wasEditedAt": self.was_edited_at,
                "isRepost": self.is_repost,
                "repostType": self.repost_type,
                "createdAt": self.created_at,
                "updatedAt": self.updated_at
            }

        if show_profile:
            result["profile"] = Profile.find_one(user_id=self.user_id).to_dict()
        
        if show_reposted:
            result["reposted"] = self.find_one(id=self.reposted_id).to_dict() if self.reposted_id else None

        if show_commented:
            result["commented"] = self.find_one(id=self.commented_id).to_dict() if self.commented_id else None

        if show_parents_ids:
            result["repostedId"] = self.reposted_id
            result["commentedId"] = self.commented_id

        return result