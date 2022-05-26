from flask import request
from errors.validation_error import ValidationError 

def validate_account(account_route_handler_func):
    def validate_account_wrapper(*args, **kwargs):
        request_body = request.get_json()
        if request.method == 'GET':
            return account_route_handler_func(*args, **kwargs)
        elif request.method == 'PATCH':
            # mennään tänne, jos request_body lähetetään insomniasta
            if request_body:
                # jos username-kenttä löytyy requst_bodysta,
                # kaikki on kunnossa ja voidaan mennä eteenpäin account_route_handleriin
                if 'username' in request_body:
                    return account_route_handler_func(*args, **kwargs)
                else:
                    # jos username ei ole request_bodyssa, siitä nostetaan virhe
                    raise ValidationError('Username is required')
            else:
                # tänne mennään, jos request bodya ei ole edes lähetetty (vasen sarake insomniassa)
                raise ValidationError('Body is required')
    return validate_account_wrapper # huomaa, että funktio palautetaan ilman sulkjua () perässä