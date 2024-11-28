from backpack.db.orm.model import table, Model, Field, GenerationStrategy
from backpack.db.orm.types import String

@table("Location")
class Location(Model):

    id = Field(String, column="locationId", primary_key=True, generator=GenerationStrategy.UUID)
    region = Field(String, required=True, unique=True)
    city = Field(String, required=True, unique=True)
    country = Field(String, required=True, unique=True)

    def __init__(self,
        region: String = None, 
        city: String = None, 
        country: String = None
    ):
        super().__init__(region=region, city=city, country=country)