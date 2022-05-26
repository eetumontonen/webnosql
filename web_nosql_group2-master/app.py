
from flask import Flask, jsonify
from controllers.account_controller import account_password_route_handler, account_route_handler
from controllers.auth_controller import LoginRouteHandler, register_route_handler
from controllers.publications_controller import like_publication_route_handler, publication_route_handler, publications_route_handler, share_publication_route_handler
from errors.not_found import NotFound
from errors.validation_error import ValidationError
from flask_jwt_extended import JWTManager
from controllers.users_controller import user_route_handler, users_route_handler

app = Flask(__name__)
app.config.from_object('config.Config')
jwt = JWTManager(app)



@app.errorhandler(NotFound)
def not_found_error_handler(err):
    return jsonify(err=err.args), 404

@app.errorhandler(ValidationError)
def validation_error_handler(err):
    return jsonify(err=err.args), 400

""" @app.errorhandler(401)
def validate_unauthorized(err):
    return jsonify(err=str(err)), 401 """

""" @app.errorhandler(Exception)
def generic_exception_handler(err):
    return jsonify(err=str(err)), 500 """



@app.route('/')
def home_route_handler():
    return """Tämä on todiste siitä, että softa toimii oikein. 
    Muista, että add_url_rulen 1. argumentti tai @app.routen argumentti pitää olla sama kuin Insomniassa"""

app.add_url_rule('/api/users', view_func=users_route_handler, methods=['GET', 'POST'])
app.add_url_rule('/api/users/<_id>', view_func=user_route_handler, methods=['GET','DELETE', 'PATCH'])
app.add_url_rule('/api/register', view_func=register_route_handler, methods=['POST'])
app.add_url_rule('/api/login', view_func=LoginRouteHandler.as_view('login_route_handler'), methods=['POST', 'PATCH'])
app.add_url_rule('/api/account', view_func=account_route_handler, methods=['GET', 'PATCH'])
app.add_url_rule('/api/account/password', view_func=account_password_route_handler, methods=['PATCH'])

app.add_url_rule('/api/publications', view_func=publications_route_handler, methods=['GET', 'POST'])
app.add_url_rule('/api/publications/<_id>', view_func=publication_route_handler, methods=['GET', 'PATCH', 'DELETE'])
app.add_url_rule('/api/publications/<_id>/like', view_func=like_publication_route_handler, methods=['PATCH'])
app.add_url_rule('/api/publications/<_id>/share', view_func=share_publication_route_handler, methods=['PATCH'])


if __name__ == '__main__':
    # kun debug-muuttujan arvo on True, serveri on ns. debug-tilassa
    # tämä tarkoittaa sitä, 
    # että se käynnistyy autom. uudelleen, kun koodi muuttuu
    app.run(debug=True) 
