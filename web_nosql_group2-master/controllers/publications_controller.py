from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt
from bson.objectid import ObjectId
from errors.not_found import NotFound
from errors.validation_error import ValidationError

from models import Publication

@jwt_required(optional=True)
def publications_route_handler():
    logged_in_user = get_jwt() # palauttaa saman datan kuin jwt.io:ssa decoded-sarakkeessa
    
    if request.method == 'GET':
       
        if logged_in_user: # on kirjauduttu sisään
            if logged_in_user['role'] == 'admin': # rooli admin
                publications = Publication.get_all()
            elif logged_in_user['role'] == 'user': # jos on normikäyttäjä
                publications = Publication.get_by_owner_and_visibility(
                    user=logged_in_user,
                    visibility=[1,2])
        else:
            publications = Publication.get_by_visibility()

        # publications_in_json_format = Publication.list_to_json(publications)
        return jsonify(publications=Publication.list_to_json(publications))
    elif request.method == 'POST':
        owner = None
        if logged_in_user:
            owner = ObjectId(logged_in_user['sub']) # sub on sisäänkirjautuneen käyttäjän _id
        # saadaan data clientiltä (tässä tapauksessa insomnia)
        request_body = request.get_json()

        title = request_body['title']
        description = request_body['description']
        url = request_body['url']
        # ao. rivi kutsuu Publication-luokan __init__-metodia autom.
        # lähetetään __init__-metodille insomnian tiedot  
        new_publication = Publication(title, description, url, owner=owner)
        # koska create EI OLE @staticmethod
        # self viittaa muuttujaan new_publication
        new_publication.create()
        return jsonify(publication=new_publication.to_json())


@jwt_required()
def like_publication_route_handler(_id):
    if request.method == 'PATCH':
        logged_in_user = get_jwt()
        publication = Publication.get_by_id(_id)
        found_index = -1
        for count, user_id in enumerate(publication.likes):
            if str(user_id) == logged_in_user['sub']:
                found_index = count
                break
        if found_index > -1: # sisäänkirjutunut käyttäjä
            # on aiemmin tykännyt postauksesta ja tykkäys pitää poista listasta
            del publication.likes[found_index]
        else: # jos käyttäjä ei ole aiemmin tykännyt, lisätään se listaan
            publication.likes.append(ObjectId(logged_in_user['sub']))
        
        publication.like()
        return jsonify(publication=publication.to_json())

@jwt_required()
def share_publication_route_handler(_id):
    if request.method == 'PATCH':
        publication = Publication.get_by_id(_id)
        publication.share()
        return jsonify(publication=publication.to_json())


@jwt_required(optional=True)
def publication_route_handler(_id):
    if request.method == 'GET':
        # 1 tee models.py-tiedostoon Publication-classiin static method get_by_id,
        publication = Publication.get_by_id(_id)
        
        # joka hakee _id:n perusteella valitun publicationin
        # 2. palauta publication jsonifylla
        return jsonify(publication=publication.to_json())
    elif request.method == 'DELETE':
        logged_in_user = get_jwt()
        if logged_in_user:
            if logged_in_user['role'] == 'user':
                publication = Publication.get_by_id(_id)
                if publication.owner is not None and str(publication.owner) == logged_in_user['sub']:
                    publication.delete()
                raise NotFound(message='Publication not found')
        raise NotFound(message='Publication not found')
    elif request.method == 'PATCH':
        logged_in_user = get_jwt()
        if logged_in_user:
            if logged_in_user['role'] == 'user':
                publication = Publication.get_by_id(_id)
                if publication.owner is not None and str(publication.owner) == logged_in_user['sub']:
                    request_body = request.get_json()
                    if request_body:
                        if 'title' in request_body and 'description' in request_body:
                            publication.title = request_body['title']
                            publication.description = request_body['description']
                            publication.update()
                            return jsonify(publication=publication.to_json())
                        raise ValidationError(message='Title and description are required')
                    raise ValidationError(message='Body is required')

                raise NotFound(message='Publication not found')
        raise NotFound(message='Publication not found')
    
    
    
        
        