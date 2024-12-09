from backpack.db.orm.model import table, Model, Field, GenerationStrategy, ForeignKey
from backpack.db.orm.types import String, DateTime
from backpack.models.user import User
from backpack.models.profile.profile import Profile

@table("Message")
class Message(Model):

    id = Field(String, column="messageId", primary_key=True, generator=GenerationStrategy.NANOID)
    sender_id = Field(String, column="senderId", required=True, foreign_key=ForeignKey("userId", String, table=User))
    receiver_id = Field(String, column="receiverId", required=True, foreign_key=ForeignKey("userId", String, table=User))
    text = Field(String, required=True)
    was_edited_at = Field(DateTime, column="wasEditedAt")
    created_at = Field(DateTime, column="createdAt", required=True, default=DateTime.now())

    def __init__(self,
        sender_id: String = None,
        receiver_id: String = None,
        text: String = None
    ):
        super().__init__(sender_id=sender_id, receiver_id=receiver_id, text=text)

    def to_dict(self):

        result = {
            "text": self.text,
            "wasEditedAt": self.was_edited_at,
            "createdAt": self.created_at
        }

        sender = Profile.find_one(user_id=self.sender_id)
        result["sender"] = sender.to_dict() if sender else User.find_one(id=self.sender_id).to_dict()

        receiver = Profile.find_one(user_id=self.receiver_id)
        result["receiver"] = receiver.to_dict() if receiver else User.find_one(id=self.receiver_id).to_dict()

        return result