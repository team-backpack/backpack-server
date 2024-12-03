from backpack.db.orm.model import table, Model, Field, GenerationStrategy, ForeignKey
from backpack.db.orm.types import String, Integer

@table("Country")
class Country(Model):
    id = Field(Integer, column="countryId", primary_key=True, generator=GenerationStrategy.INCREMENT)
    name = Field(String, required=True, unique=True)
    code = Field(String, column="countryCode", unique=True, required=True)
    continent = Field(String, required=True)

    def __init__(self, name=None, code=None, continent=None):
        super().__init__(name=name, code=code, continent=continent)


@table("Region")
class Region(Model):
    id = Field(Integer, column="regionId", primary_key=True, generator=GenerationStrategy.INCREMENT)
    name = Field(String, required=True)
    country = Field(Country, column="countryId", foreign_key=ForeignKey("countryId", Integer))

    def __init__(self, name=None, country=None):
        super().__init__(name=name, country=country)


@table("City")
class City(Model):
    id = Field(Integer, column="cityId", primary_key=True, generator=GenerationStrategy.INCREMENT)
    name = Field(String, required=True)
    region = Field(Region, column="regionId", foreign_key=ForeignKey("regionId", Integer))

    def __init__(self, name=None, region=None):
        super().__init__(name=name, region=region)


@table("Location")
class Location(Model):

    id = Field(Integer, column="locationId", primary_key=True, generator=GenerationStrategy.INCREMENT)
    country = Field(Country, column="countryId", required=True, foreign_key=ForeignKey("countryId", Integer))
    region = Field(Region, column="regionId", required=True, foreign_key=ForeignKey("regionId", Integer))
    city = Field(City, column="cityId", required=True, foreign_key=ForeignKey("cityId", Integer))

    def __init__(self,
        country: Country = None,
        region: Region = None, 
        city: City = None
    ):
        super().__init__(country=country, region=region, city=city)