#!/usr/bin/env python3

from flask import request, session, make_response
from flask_restful import Resource


from config import app, db, api
from models import User, Recipe


def get_property_val_from_user_dict(value, user_dict ):
    if value in user_dict:
        return user_dict[value]
    return None


class Signup(Resource):
    def post(self):
        new_user_params = request.get_json()

        new_user = get_property_val_from_user_dict("username", new_user_params)

        new_user = User(
            username = get_property_val_from_user_dict("username", new_user_params ),
            image_url = get_property_val_from_user_dict("image_url", new_user_params ),
            bio = get_property_val_from_user_dict("bio", new_user_params )
        )
        new_user.password_hash = get_property_val_from_user_dict("password", new_user_params )
   
        try:
            db.session.add(new_user)
            db.session.commit()
            new_user_added = True
        except:
            new_user_added = False
        
        # Set up the session cookie.  We're in luck!
        if new_user_added:
            session["user_id"] = new_user.id
            response = make_response(
                new_user.get_user_dictionary(),
                201
            )
        else:
             response = {}, 422
        
        return response

class CheckSession(Resource):
    def get(self):  

        if session.get("user_id"):
 
            # They are logged in.  Send them goodness about them selves
            user_data = User.query.filter(User.id == session.get("user_id")).first()
    
            response = make_response (
                user_data.get_user_dictionary(), 200
            )
        else:

            response = make_response(
                {"Error": "Not Logged In" },
                401
            )
        return response
                        
                               
        

     


class Login(Resource):
    def post(self):
        login_params = request.get_json()

        user_check = User.query.filter(User.username == login_params["username"]).first()

        # have to check the truthiness of user_check in case the username is not found in the database
        if (user_check and user_check.authenticate(login_params["password"])) :
            response = make_response (
                user_check.get_user_dictionary(), 200
            )
        else :
            response = {"error" :"401 - Login Failed"}, 401

        return response

class Logout(Resource):
    def delete(self):
        if session.get("user_id"):
            session["user_id"] = None
            return {}, 204
        else :
            return {"error" : "401 - Not logged in"}, 401
            

class RecipeIndex(Resource):
    def post(self):
        recipe_info = request.get_json()

        if session.get("user_id"):
            new_recipe = Recipe (
                            instructions = get_property_val_from_user_dict("instructions", recipe_info), 
                            minutes_to_complete = get_property_val_from_user_dict("minutes_to_complete", recipe_info),
                            title = get_property_val_from_user_dict("title", recipe_info),
                            user_id = session.get("user_id")
                        )
            
            try :
                db.session.add(new_recipe)
                db.session.commit()
                recipe_success = True
                
            except:
                
                recipe_success = False

            if recipe_success :
                user = User.query.filter(User.id == session.get("user_id")).first()
                user_name = user.username
                response_dictionary = new_recipe.get_recipe_dictionary()
                response_dictionary["user"] = user.get_user_dictionary()
                response = make_response(
                    response_dictionary,
                    201
                )
                return response 
            else:
                return {"error": "Error 422 - Recipe Error"}, 422
        else:
            return {"error" : "Error 401 - Not logged in"}, 401

    def get(self):
        if session.get("user_id") :
            recipe_response_list = []
            recipe_list = Recipe.query.all()
            for recipe in recipe_list:
                user_info = User.query.filter(User.id == recipe.user_id ).first()
                recipe_response_list.append(recipe.get_recipe_dictionary())
                recipe_response_list[-1]["user"] = user_info.get_user_dictionary()

            response = make_response(
                recipe_response_list,
                200
            )
        else:
            response = {"error" : "Error 401 - Not logged in"}, 401
            
        return response


api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)
