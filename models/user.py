from mongoengine import Document, StringField
from bson import ObjectId

class User(Document):
    meta = {'collection': 'users'}  # optional, but helps if you use a custom collection

    username = StringField(required=True, unique=True)
    password = StringField(required=True)

    @classmethod
    def get_by_id(cls, user_id):
        try:
            return cls.objects(id=ObjectId(user_id)).first()
        except Exception:
            return None
