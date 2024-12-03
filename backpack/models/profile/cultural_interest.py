from backpack.db.orm.model import table, Model, Field, GenerationStrategy, ForeignKey
from backpack.db.orm.types import String, Integer
from backpack.models.profile.profile import Profile

@table("CulturalInterest")
class CulturalInterest(Model):

    id = Field(Integer, column="culturalInterestId", primary_key=True, generator=GenerationStrategy.INCREMENT)
    name = Field(String, required=True, unique=True)
    flag = Field(String, required=True)
    color = Field(String, required=True)

    def __init__(self,
        name: String = None,
        flag: String = None,
        color: String = None
    ):
        super().__init__(name=name, flag=flag, color=color)


@table("ProfileCulturalInterest")
class ProfileCulturalInterest(Model):

    id = Field(Integer, column="id", primary_key=True, generator=GenerationStrategy.INCREMENT)
    profile = Field(Profile, column="profileId", foreign_key=ForeignKey("profileId", String))
    cultural_interest = Field(CulturalInterest, column="culturalInterestId", foreign_key=ForeignKey("culturalInterestId", Integer))

    def __init__(self,
        profile: Profile = None,
        cultural_interest: CulturalInterest = None
    ):
        super().__init__(profile=profile, cultural_interest=cultural_interest)