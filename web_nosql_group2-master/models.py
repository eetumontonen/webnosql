import random
import string
import pymongo
from bson.objectid import ObjectId
from pymongo.server_api import ServerApi
from passlib.hash import pbkdf2_sha256 as sha256

from errors.not_found import NotFound 

# pymongo connection string


client = pymongo.MongoClient("mongodb+srv://web_nosql_db:a1XiUzqY9kHqxOed@cluster0.rr8t2.mongodb.net/?retryWrites=true&w=majority", server_api=ServerApi('1'))
db = client.group2


# jokaiselle MongoDB:n collectionille / esim. MySQL tablelle
# tehdään luokka (tämä luokka on ns. model-luokka)
# jokainen model-luokka sisältää samat tiedot, kuin tietokannan 
# collection / table (esim. username)

# model-luokkaan kuuluu CRUD:n toiminallisuudet, joista jokainen
# on model-luokan funktio / metodi

# CRUD
# C => create()
# R => get_all() ja get_by_id()
# U => update()
# D => delete()

# mitä hyötyä modelista sitten on, 
# jos CRUD:n voi tehdä suoraan controlleriinkin?
# koska Separation of Concerns
# Käytännössä Separation of Corncerns tarkoittaa tässä sitä, että 
# controllerin tehtävä on huolehtia route_handlereista, 
# eikä tietokantahauista



# CRUD-logiikka kuuluu modeliin, koska model on 'portinvartija'
# tietokannan ja koodin (controllerin) välissä
class User:
    
    
    def __init__(self, username, password=None, role='user', _id=None):
        self.username = username
        self.password = password
        self.role = role
        
        if _id is not None:
            _id = str(_id)
        self._id = _id
    
    # CRUD:n osa U
    def update(self):
        db.users.update_one({'_id': ObjectId(self._id)},
        {
            '$set': {'username': self.username}
        })
    
    # CRUD:n osa U (Käyttäen static methodia)
    @staticmethod
    def update_by_id(_id, new_username):
        db.users.update_one({'_id': ObjectId(_id)}, {
            '$set': {'username': new_username}
        })

        user = User.get_by_id(_id)
        return user



    
    
    # CRUD:n osa D (Yksittäisen käyttäjän poisto)
    def delete(self):
        db.users.delete_one({'_id': ObjectId(self._id)})
    
    # CRUD:n osa D (Yksittäisen käyttäjän poisto staattisella metodilla)
    @staticmethod
    def delete_by_id(_id):
        db.users.delete_one({'_id': ObjectId(_id)})

    
    # CRUD:n R (READ) => haetaan kaikki käyttäjät
    @staticmethod
    def get_all():
        users = []
        users_cursor = db.users.find()
        for user in users_cursor:
            users.append(User(user['username'], _id=user['_id']))
        return users
    
    @staticmethod
    def get_by_username(username):
        user_dictionary = db.users.find_one({'username': username})
        if user_dictionary is None:
            raise NotFound(message='User not found')
        user = User(username, password=user_dictionary['password'], _id=user_dictionary['_id'])
        return user
    
    @staticmethod
    def get_by_id(_id):
        user_dictionary = db.users.find_one({'_id': ObjectId(_id)})
        user = User(user_dictionary['username'], _id=_id)
        return user
    
    # CRUD:n C (eli tässä lisätään käyttäjä)
    def create(self):
        result = db.users.insert_one({
            'username': self.username,
            'password': sha256.hash(self.password),
            'role': self.role
        })
        self._id = str(result.inserted_id)
    
    def to_json(self):
        user_in_json_format = {
            '_id': str(self._id),
            'username': self.username,
            'role': self.role
        }

        return user_in_json_format
    
    @staticmethod
    def list_to_json(users):
        users_list_in_json = []
        for user in users:
            users_list_in_json.append(user.to_json())
        return users_list_in_json

class Publication:
    def __init__(self, 
    title, 
    description, 
    url, 
    owner=None, 
    likes=[],
    shares=0,
    tags=[],
    comments=[],
    visibility=2,
    share_link=None,
    _id=None):
        self.title = title
        self.description = description
        self.url = url
        self.owner = owner
        self.likes = likes
        self.shares = shares
        self.tags = tags
        self.comments = comments
        self.visibility = visibility # 2:näkyy kaikille,
        #1:näkyy vain kirjautuneille käyttäjille;
        # 0:vain itselle+admin
        self.share_link=share_link
        if _id is not None:
            # jos _id ei ole oletusarvo (eli None), silloin se pitää muuttaa merkkijonoksi
            # käyttäen str:ää
            # muuten jsonify-funktio epäonnistuu
            _id = str(_id)
        self._id = _id
    
    # CRUD:n osa U
    def update(self):
        db.publications.update_one({'_id': ObjectId(self._id)},
        {
            '$set': {'title': self.title, 'description': self.description}
        })
    
    # CRUD:n osa D (Yksittäisen käyttäjän poisto)
    def delete(self):
        db.publications.delete_one({'_id': ObjectId(self._id)})
    
    @staticmethod
    def get_by_id(_id):
        # 1 tee koodi joka hakee db:n publications collectionista _id:lla yhden publicationin
        publication_dictionary = db.publications.find_one({'_id': ObjectId(_id)})
        if publication_dictionary is None:
            raise NotFound(message='Publication not found')
        # voit ottaa tähän mallia user-classin get_by_id:stä
        # 2 tee tuloksesta Publication-tyyppinen muuttuja kaikkine attribuutteineen
        title = publication_dictionary['title']
        description = publication_dictionary['description']
        url = publication_dictionary['url']
        owner = publication_dictionary['owner']
        likes = publication_dictionary['likes']
        tags = publication_dictionary['tags']
        comments = publication_dictionary['comments']
        visibility = publication_dictionary['visibility']
        share_link = publication_dictionary['share_link']
        shares = publication_dictionary['shares']
        _id = publication_dictionary['_id']
        publication = Publication(
            title, 
            description, 
            url, 
            owner=owner, 
            likes=likes,
            tags=tags,
            comments=comments,
            visibility=visibility,
            share_link=share_link,
            shares=shares,
            _id =_id
        )
        # voit ottaa tähän mallia get_by_visibilityn luupin sisältä
        # (huom. älä kopioi luuppia ja listaa, koska nyt haetaan vain yksi publication)
        # 3. palauta 2. kohdassa tehty muuttuja
        return publication
        
    
    @staticmethod
    def get_by_visibility(visibility=2):
        publications_cursor = db.publications.find({'visibility': visibility})
        publications = []
        for publication_dictionary in publications_cursor:
            # voit käyttää tästä alaspäin koodia get_by_id-methodissa suoraan.
            title = publication_dictionary['title']
            description = publication_dictionary['description']
            url = publication_dictionary['url']
            owner = publication_dictionary['owner']
            likes = publication_dictionary['likes']
            tags = publication_dictionary['tags']
            comments = publication_dictionary['comments']
            visibility = publication_dictionary['visibility']
            share_link = publication_dictionary['share_link']
            shares = publication_dictionary['shares']
            _id = publication_dictionary['_id']
            publication = Publication(
                title, 
                description, 
                url, 
                owner=owner, 
                likes=likes,
                tags=tags,
                comments=comments,
                visibility=visibility,
                share_link=share_link,
                shares=shares,
                _id =_id
            )

            publications.append(publication)
        
        return publications

    

    @staticmethod
    def get_by_owner_and_visibility(user={}, visibility=[2]):
        
        publications_cursor = db.publications.find({
            '$or': [
                {'visibility': {'$in': visibility}},
                {'owner': ObjectId(user['sub'])}
                # jos visibility in [1,2]
                # tai owner = user['_id']
            ]
        })
        publications = []
        for publication_dictionary in publications_cursor:
            title = publication_dictionary['title']
            description = publication_dictionary['description']
            url = publication_dictionary['url']
            owner = publication_dictionary['owner']
            likes = publication_dictionary['likes']
            tags = publication_dictionary['tags']
            comments = publication_dictionary['comments']
            visibility = publication_dictionary['visibility']
            share_link = publication_dictionary['share_link']
            shares = publication_dictionary['shares']
            _id = publication_dictionary['_id']
            publication = Publication(
                title, 
                description, 
                url, 
                owner=owner, 
                likes=likes,
                tags=tags,
                comments=comments,
                visibility=visibility,
                share_link=share_link,
                shares=shares,
                _id =_id
            )

            publications.append(publication)
        
        return publications
        
        
    
    def create(self):
        result = db.publications.insert_one({
            'title': self.title,
            'description': self.description,
            'url': self.url,
            'owner': self.owner,
            'likes': self.likes,
            'shares': self.shares,
            'tags': self.tags,
            'comments': self.comments,
            'visibility': self.visibility,
            'share_link': self.share_link
        })

        self._id = str(result.inserted_id)
    
    @staticmethod
    def get_all():
        publications = []
        publications_cursor = db.publications.find()
        for publication in publications_cursor:
            title = publication['title']
            description = publication['description']
            url = publication['url']
            # tähän lisätään loput muuttujat myöhemmin
            publication_object = Publication(title, description, url)
            publications.append(publication_object)
        
        return publications

    @staticmethod
    def list_to_json(publications_list):
        publications_in_json_format = []
        for publication in publications_list:
            publication_in_json_format = publication.to_json()
            publications_in_json_format.append(publication_in_json_format)
        return publications_in_json_format



    def to_json(self):
        owner = self.owner
        likes = self.likes
        for count, user_id in enumerate(likes):
            likes[count] = str(user_id)
        if owner is not None:
            owner = str(owner)
        publication_in_json_format = {
            '_id': self._id,
            'title': self.title,
            'description': self.description,
            'url': self.url,
            'owner': owner,
            'likes': likes,
            'shares': self.shares,
            'tags': self.tags,
            'comments': self.comments,
            'visibility': self.visibility,
            'share_link': self.share_link
        }
        return publication_in_json_format
    
    def share(self):
        _filter = {'_id': ObjectId(self._id)}
        if self.share_link is None:
            letters = string.ascii_lowercase
            self.share_link = ''.join(random.choice(letters) for _ in range(8))
            _update = {'$set': {'share_link': self.share_link, 'shares':1}}
        else:
            _update = {'$inc': {'shares':1}}
        db.publications.update_one(_filter, _update)
    
    def like(self):
        db.publications.update_one({'_id': ObjectId(self._id)},
        {
            '$set': {'likes': self.likes}
        })


    

        

