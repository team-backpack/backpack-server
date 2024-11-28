from backpack.db.orm.model import table, Model, Field, GenerationStrategy, ForeignKey
from backpack.db.orm.types import String

@table("Profile")
class Profile(Model):

    id = Field(String, column="profileId", primary_key=True, generator=GenerationStrategy.UUID)
    user_id = Field(String, column="userId", unique=True, foreign_key=ForeignKey("userId", String))
    display_name = Field(String, column="displayName")
    description = Field(String)
    picture_url = Field(String, column="pictureUrl", required=True)
    banner_url = Field(String, column="bannerUrl", required=True)

    def __init__(self,
        user_id: String = None,
        display_name: String = None,
        description: String = None,
        picture_url: String = None,
        banner_url: String = None
    ):
        super().__init__(user_id=user_id, display_name=display_name, description=description, picture_url=picture_url, banner_url=banner_url)