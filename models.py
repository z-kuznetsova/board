from datetime import date
from django.db.models import *

#pg_db = PostgresqlDatabase('board', user='root', password='1',
 #                          host='localhost', port=5432)

	
#print("kek")

class User(Model):
    id = IntegerField()
    registration_date = DateTimeField()

class Board(Model):
    text = CharField()
    date = DateTimeField()
    #user = ForeignKeyField(User)