from backpack.db.orm.model import table, Model, Field, GenerationStrategy, ForeignKey
from backpack.db.orm.types import String, Integer
from backpack.models.profile.profile import Profile

@table("GeneralInterest")
class GeneralInterest(Model):

    id = Field(Integer, column="generalInterestId", primary_key=True, generator=GenerationStrategy.INCREMENT)
    name = Field(String, required=True, unique=True)
    image_url = Field(String, column="imageURL", required=True)

    def __init__(self,
        name: String = None,
        image_url: String = None,
        color: String = None
    ):
        super().__init__(name=name, image_url=image_url, color=color)


@table("ProfileGeneralInterest")
class ProfileGeneralInterest(Model):

    id = Field(Integer, column="id", primary_key=True, generator=GenerationStrategy.INCREMENT)
    profile = Field(Profile, column="profileId", foreign_key=ForeignKey("profileId", String))
    general_interest = Field(GeneralInterest, column="generalInterestId", foreign_key=ForeignKey("generalInterestId", Integer))

    def __init__(self,
        profile: Profile = None,
        general_interest: GeneralInterest = None
    ):
        super().__init__(profile=profile, general_interest=general_interest)