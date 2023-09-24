#!/usr/bin/env python3

from random import randint



from app import app
from models import db, Recipe, User
from sqlalchemy.exc import IntegrityError
import traceback


with app.app_context():

    print("Deleting all records...")
    User.query.delete()
    db.session.commit()

    Recipe.query.delete()
    db.session.commit()

   
