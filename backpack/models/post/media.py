from backpack.db.orm.model import table, Model, Field, GenerationStrategy, ForeignKey
from backpack.db.orm.types import String

@table("Media")
class Media(Model):

    id = Field(String, column="mediaId", primary_key=True, generator=GenerationStrategy.NANOID)
    url = Field(String, required=True)
    post_id = Field(String, column="postId", foreign_key=ForeignKey("postId", String, table_name="Post"))

    def __init__(self,
        url: String = None,
        post_id: String = None
    ):
        super().__init__(url=url, post_id=post_id)