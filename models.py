from datetime import datetime

from mongoengine import EmbeddedDocument, Document, CASCADE
from mongoengine.fields import ReferenceField, BooleanField, DateTimeField, EmbeddedDocumentField, ListField, StringField

class Author(Document): #)(EmbeddedDocument):
    fullname = StringField(required=True, unique=True)
    born_date = StringField()
    born_location = StringField()
    description = StringField()
    meta = {"collection": "authors"}

class Quotes(Document):
    tags = ListField(StringField())
    author = ReferenceField(Author, reverse_delete_rule=CASCADE)
    quote = StringField()
    meta = {"collection": "quotes"}



