from backpack.db.orm.model import table, Model, Field, GenerationStrategy, Default, ForeignKey
from backpack.db.orm.types import String, DateTime, Boolean
from backpack.models.user import User
from backpack.models.profile.profile import Profile
from backpack.utils.constants import role_to_response

@table("Community")
class Community(Model):

    id = Field(String, column="communityId", primary_key=True, generator=GenerationStrategy.UUID)
    name = Field(String, required=True, unique=True)
    display_name = Field(String, column="displayName", required=True)
    description = Field(String, required=True)
    banner_url = Field(String, column="bannerURL", required=True)
    created_at = Field(DateTime, column="createdAt", required=True, default=Default.NOW)
    updated_at = Field(DateTime, column="updatedAt", required=True, default=Default.NOW)

    def __init__(self,
        name: String = None,
        display_name: String = None,
        description: String = None,        
        banner_url: String = None
    ):
        super().__init__(description=description, display_name=display_name, name=name, banner_url=banner_url)

    def to_dict(self, show_participants: bool = False, show_participants_ids: bool = False):
        result =  {
            "communityId": self.id,
            "name": self.name,
            "displayName": self.display_name,
            "description": self.description,
            "bannerURL": self.banner_url,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at
        }

        if show_participants or show_participants_ids:
            result["participants"] = { "administrators": [], "moderators": [], "members": [] }
            participants = Participant.find_all(community_id=self.id, limit=10)

            for participant in participants:
                obj = participant.to_dict() if show_participants else participant.user_id

                key = ""
                if participant.role in role_to_response.keys():
                    key = role_to_response[participant.role]

                result["participants"][key].append(obj)

        return result
    

@table("Participant")
class Participant(Model):

    id = Field(String, column="participantId", primary_key=True, generator=GenerationStrategy.NANOID)
    user_id = Field(String, column="userId", required=True, foreign_key=ForeignKey("userId", String, table=User))
    community_id = Field(String, column="communityId", required=True, foreign_key=ForeignKey("communityId", String, table=Community))
    role = Field(String, required=True)
    is_suspended = Field(Boolean, required=True, default=False)
    since = Field(DateTime, required=True, default=Default.NOW)

    def __init__(self,
        user_id: String = None,
        community_id: String = None,
        role: String = "member"
    ):
        super().__init__(user_id=user_id, community_id=community_id, role=role)

    def to_dict(self, show_profile: bool = True, show_user_id: bool = False):
        result =  {
            "participantId": self.id,
            "communityId": self.community_id,
            "role": self.role,
            "isSuspended": self.is_suspended,
            "since": self.since
        }

        if show_profile:
            result["profile"] = Profile.find_one(user_id=self.user_id).to_dict()
        
        if show_user_id:
            result["userId"] = self.user_id

        return result
    