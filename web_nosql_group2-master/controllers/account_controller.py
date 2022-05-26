from flask import jsonify, request
from flask_jwt_extended import get_jwt, jwt_required
from errors.validation_error import ValidationError
from passlib.hash import pbkdf2_sha256 as sha256


from models import User
from validators.account import validate_account

@jwt_required()
# @validate_account
def account_route_handler():
    if request.method == 'GET':
        logged_in_user = get_jwt()
        # print(logged_in_user)
        
        account = User.get_by_id(logged_in_user['sub'])
        return jsonify(account=account.to_json())
    elif request.method == 'PATCH':
        logged_in_user = get_jwt()
        account = User.get_by_id(logged_in_user['sub'])
        request_body = request.get_json()
        if request_body:
            if 'username' in request_body:
                username = request_body['username']
                account.username = username
                account.update()
                #User.update_by_id
                return jsonify(account=account.to_json())
            raise ValidationError(message='username is required')
        raise ValidationError(message='request body is required')

@jwt_required()
def account_password_route_handler():
    if request.method == 'PATCH':
        logged_in_user = get_jwt()
        account = User.get_by_id(logged_in_user['sub'])
        request_body = request.get_json()
        if request_body:
            if 'password' in request_body:
                password = request_body['password']
                account.password = sha256.hash(password)
                account.update()
                return jsonify(account=account.to_json())
            raise ValidationError(message='username is required')
        raise ValidationError(message='request body is required')
            
            
