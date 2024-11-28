from backpack.db.orm.model import table, Model, Field, GenerationStrategy
from backpack.db.orm.types import String

@table("CulturalInterest")
class CulturalInterest(Model):

    id = Field(String, column="culturalInterestId", primary_key=True, generator=GenerationStrategy.UUID)
    name = Field(String, required=True, unique=True)

    def __init__(self,
        name: String = None
    ):
        super().__init__(name=name)