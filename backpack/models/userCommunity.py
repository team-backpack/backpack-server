from backpack.db.orm.model import table, Model, Field, GenerationStrategy, ForeignKey
from backpack.db.orm.types import String, Boolean

@table("UserCommunity")
class UserCommunity(Model):

    id = Field(String, column="userCommunityId", primary_key=True, generator=GenerationStrategy.UUID)
    user_id = Field(String, column="userId", required=True, foreign_key=ForeignKey("userId", String))
    community_id = Field(String, column="communityId", required=True, foreign_key=ForeignKey("communityId", String))
    role = Field(String, required=True)
    is_suspended = Field(Boolean, required=True, default=False)

    def __init__(self,
        user_id: String = None,
        community_id: String = None,
        role: String = None
    ):
        super().__init__(user_id=user_id, community_id=community_id, role=role)