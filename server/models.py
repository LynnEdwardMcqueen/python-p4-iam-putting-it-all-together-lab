from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_serializer import SerializerMixin

from config import db, bcrypt

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable = False, unique = True)
    _password_hash = db.Column(db.String)
    image_url = db.Column(db.String)
    bio = db.Column(db.String)
    recipes = db.relationship('Recipe', backref='user')

    def __repr__(self):
        return f'<User {self.username} {self.id}>'

    pass

    @hybrid_property
    def password_hash(self):
        raise AttributeError("password hash access restricted")
        return self._password_hash
    
    @password_hash.setter
    def password_hash(self, password):
        password_hash = bcrypt.generate_password_hash(
            password.encode('utf-8'))
        self._password_hash = password_hash.decode('utf-8')

    def authenticate(self, password):
        return bcrypt.check_password_hash(
            self._password_hash, password.encode('utf-8'))
    
    # this was created sinse the to_dict() method is not working. 
    def get_user_dictionary(self):
        return {
            "username": self.username,
            "image_url": self.image_url,
            "bio": self.bio,
            "id": self.id
        }


class Recipe(db.Model, SerializerMixin):
    __tablename__ = 'recipes'
    __table_args__ = (
        db.CheckConstraint('length(instructions) >= 50'),
    )
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable = False)
    instructions = db.Column(db.String, nullable = False )
    minutes_to_complete = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    # This was created since the to_dict() method is not working.  The id and user_id fields are not
    # required for anything, so they are left out.
    def get_recipe_dictionary(self):
        return {
            "title" : self.title,
            "instructions" : self.instructions,
            "minutes_to_complete" : self.minutes_to_complete,
        }
    def __repr__(self):
        return f'<Recipe {self.id} {self.title} {self.minutes_to_complete} {self.user_id}>'
    pass