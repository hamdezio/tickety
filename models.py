from mongoengine import Document, StringField, DateTimeField, SequenceField, ReferenceField
import datetime

ALLOWED_PRIORITIES = {'low', 'medium', 'high'}
ALLOWED_STATUSES = {'open', 'in progress', 'resolved', 'closed'}
ROLES = {'client', 'admin'}

class User(Document):
    username = StringField(required=True, unique=True)
    password = StringField(required=True)  # hashed password
    role = StringField(required=True, choices=ROLES)

class Ticket(Document):
    ticket_id = SequenceField(primary_key=True)
    user = ReferenceField(User, required=True)   # Owner of ticket
    title = StringField(required=True)
    description = StringField(required=True)
    priority = StringField(required=True, choices=ALLOWED_PRIORITIES)
    status = StringField(default='open', choices=ALLOWED_STATUSES)
    created_at = DateTimeField(default=datetime.datetime.utcnow)
