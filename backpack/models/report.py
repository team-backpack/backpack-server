from backpack.db.orm.model import table, Model, Field, GenerationStrategy, ForeignKey
from backpack.db.orm.types import String, DateTime

@table("Report")
class Report(Model):

    id = Field(String, column="reportId", primary_key=True, generator=GenerationStrategy.UUID)
    post_id = Field(String, foreign_key=ForeignKey("postId", String))
    comunity_id = Field(String, foreign_key=ForeignKey("comunityId", String))
    report_reason_id = Field(String, foreign_key=ForeignKey("reportReasonId", String))
    user_id = Field(String, foreign_key=ForeignKey("userId", String))
    text = Field(String)
    created_at = Field(DateTime, column="createdAt", required=True, defaul=DateTime.now())

    def __init__(self, 
        text: String = None,
        post_id: String = None,
        comunity_id: String = None,
        report_reason_id: String = None,
        user_id: String = None
    ):
        super().__init__(
            text=text, 
            post_id=post_id, 
            comunity_id=comunity_id, 
            report_reason_id=report_reason_id, 
            user_id=user_id
        )