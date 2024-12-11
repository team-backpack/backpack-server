from backpack.db.orm.model import table, Model, Field, GenerationStrategy, ForeignKey, Default
from backpack.db.orm.types import String, DateTime, Boolean
from backpack.models.user import User
from backpack.models.profile.profile import Profile

@table("Message")
class Message(Model):

    id = Field(String, column="messageId", primary_key=True, generator=GenerationStrategy.NANOID)
    sender_id = Field(String, column="senderId", required=True, foreign_key=ForeignKey("userId", String, table=User))
    receiver_id = Field(String, column="receiverId", required=True, foreign_key=ForeignKey("userId", String, table=User))
    text = Field(String, required=True)
    seen = Field(Boolean, required=True, default=False)
    was_edited_at = Field(DateTime, column="wasEditedAt")
    created_at = Field(DateTime, column="createdAt", required=True, default=Default.NOW)

    def __init__(self,
        sender_id: String = None,
        receiver_id: String = None,
        text: String = None
    ):
        super().__init__(sender_id=sender_id, receiver_id=receiver_id, text=text)

    def to_dict(self, show_sender = False, show_receiver = False, show_participants_id = False):

        result = {
            "messageId": self.id,
            "text": self.text,
            "seen": self.seen,
            "wasEditedAt": self.was_edited_at,
            "createdAt": self.created_at
        }

        if show_participants_id:
            result["senderId"] = self.sender_id
            result["receiverId"] = self.receiver_id

        if show_sender:
            sender = Profile.find_one(user_id=self.sender_id)
            result["sender"] = sender.to_dict() if sender else User.find_one(id=self.sender_id).to_dict()

        if show_receiver:
            receiver = Profile.find_one(user_id=self.receiver_id)
            result["receiver"] = receiver.to_dict() if receiver else User.find_one(id=self.receiver_id).to_dict()

        return result