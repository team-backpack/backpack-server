from backpack.db.orm.model import table, Model, Field, GenerationStrategy, ForeignKey
from backpack.db.orm.types import String, Integer
from backpack.models.user import User
from backpack.models.profile.location import Location
from backpack.models.profile.language import Language

@table("Profile")
class Profile(Model):

    id = Field(String, column="profileId", primary_key=True, generator=GenerationStrategy.NANOID)
    display_name = Field(String, column="displayName", required=True)
    description = Field(String)
    picture_url = Field(String, column="pictureURL")
    banner_url = Field(String, column="bannerURL")
    user_id = Field(String, column="userId", unique=True, foreign_key=ForeignKey("userId", String, table=User))
    location = Field(Location, column="locationId", foreign_key=ForeignKey("locationId", Integer))
    language = Field(Language, column="languageId", foreign_key=ForeignKey("languageId", Integer))

    def __init__(self,
        user_id: String = None,
        display_name: String = None,
        description: String = None,
        picture_url: String = None,
        banner_url: String = None,
        location: Location = None,
        language: Language = None
    ):
        super().__init__(user_id=user_id, display_name=display_name, description=description, picture_url=picture_url, banner_url=banner_url, location=location, language=language)

    def to_dict(self, show_user: bool = True):
        result = {
            "profileId": self.id,
            "displayName": self.display_name,
            "description": self.description,
            "pictureURL": self.picture_url,
            "bannerURL": self.banner_url,
            "location": self.location.to_dict() if self.location else None,
            "language": self.language.to_dict() if self.language else None
        }

        if show_user:
            result["user"] = User.find_one(id=self.user_id).to_dict()

        return result
