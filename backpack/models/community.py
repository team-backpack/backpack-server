from backpack.db.orm.model import table, Model, Field, GenerationStrategy
from backpack.db.orm.types import String, DateTime

@table("Community")
class Community(Model):

    id = Field(String, column="communityId", primary_key=True, generator=GenerationStrategy.UUID)
    description = Field(String, required=True)
    display_name = Field(String, required=True)
    name = Field(String, required=True, unique=True)
    banner_url = Field(String, column="bannerUrl", required=True)
    created_at = Field(DateTime, column="createdAt", required=True, default=DateTime.now())

    def __init__(self,
        description: String = None,
        display_name: String = None,
        name: String = None,
        banner_url: String = None
    ):
        super().__init__(description=description, display_name=display_name, name=name, banner_url=banner_url)
    