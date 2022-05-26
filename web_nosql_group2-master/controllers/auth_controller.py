from flask import jsonify, request
from passlib.hash import pbkdf2_sha256 as sha256
from errors.not_found import NotFound
from errors.validation_error import ValidationError
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt
from flask_jwt_extended import jwt_required
from flask.views import MethodView

from models import User
from validators.validate_password_and_username import validate_password_and_username

@validate_password_and_username
def register_route_handler():
    if request.method == 'POST':
        
        request_body = request.get_json()
        
        username = request_body['username']
        # username = request_body.get('username', 'defaultvalue')
        password = request_body['password']
        new_user = User(username, password=password)
        new_user.create()
        return ""


class LoginRouteHandler(MethodView):
    @validate_password_and_username
    def post(self):
        request_body = request.get_json()
        username = request_body['username']
        password = request_body['password']
        user = User.get_by_username(username)
        
        password_ok = sha256.verify(password, user.password)
        if password_ok:
            access_token = create_access_token(identity=str(user._id), 
            additional_claims={'username': user.username, 'role': user.role})
            refresh_token = create_refresh_token(identity=str(user._id))
            return jsonify(access_token=access_token, refresh=refresh_token)
        
        raise NotFound(message='User not found')

    @jwt_required(refresh=True)
    def patch(self):
        return ""
        

        
    


        






