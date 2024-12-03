from backpack.db.orm.model import table, Model, Field, GenerationStrategy
from backpack.db.orm.types import String, Integer

@table("Language")
class Language(Model):
    id = Field(Integer, column="languageId", primary_key=True, generator=GenerationStrategy.INCREMENT)
    name = Field(String, required=True, unique=True)
    code = Field(String, column="code", required=True, unique=True)
    script = Field(String, column="script")

    def __init__(self, name=None, code=None, script=None):
        super().__init__(name=name, code=code, script=script)

    def to_dict(self):
        return {
            "languageId": self.id,
            "name": self.name,
            "code": self.code,
            "script": self.script
        }