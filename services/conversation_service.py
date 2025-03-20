import uuid
import datetime
from utils.db_utils import MongoDB

class ConversationService:
    def __init__(self):
        self.db = MongoDB()
        self.collection_name = "conversations"

    def get_conversation(self, conversation_id=None):
        if conversation_id:
            conv = self.db.find_document(self.collection_name, {"conversation_id": conversation_id})
            if conv:
                return conv
        conversation_id = f"CONV-{str(uuid.uuid4())[:8].upper()}"
        new_conv = {
            "conversation_id": conversation_id,
            "history": [],
            "context": {},
            "created_at": datetime.datetime.now()
        }
        self.db.insert_document(self.collection_name, new_conv)
        return new_conv

    def add_message(self, conversation_id, role, content):
        self.db.get_collection(self.collection_name).update_one(
            {"conversation_id": conversation_id},
            {"$push": {"history": {"role": role, "content": content, "timestamp": datetime.datetime.now()}}}
        )

    def set_context(self, conversation_id, key, value):
        self.db.get_collection(self.collection_name).update_one(
            {"conversation_id": conversation_id},
            {"$set": {f"context.{key}": value}}
        )

    def get_context(self, conversation_id, key):
        conv = self.db.find_document(self.collection_name, {"conversation_id": conversation_id})
        return conv["context"].get(key) if conv and "context" in conv else None
