from backpack.db.orm.model import table, Model, Field, GenerationStrategy
from backpack.db.orm.types import String

@table("ReportReason")
class ReportReason(Model):

    id = Field(String, column="reportReasonId", primary_key=True, generator=GenerationStrategy.UUID)
    name = Field(String, required=True)
    description = Field(String, required=True)

    def __init__(self, 
        name: String = None,
        description: String = None
    ):
        super().__init__(name=name, description=description)