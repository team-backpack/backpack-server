from backpack.db.orm.model import table, Model, Field, GenerationStrategy, ForeignKey
from backpack.db.orm.types import Integer, String
from backpack.models.user import User

@table("Follow")
class Follow(Model):

    id = Field(Integer, column="followId", primary_key=True, generator=GenerationStrategy.INCREMENT)
    follower_id = Field(String, column="followerId", required=True, foreign_key=ForeignKey("userId", String, table=User))
    following_id = Field(String, column="followingId", required=True, foreign_key=ForeignKey("userId", String, table=User))

    def __init__(self, 
        follower_id: String = None,
        following_id: String = None
    ):
        super().__init__(follower_id=follower_id, following_id=following_id)
