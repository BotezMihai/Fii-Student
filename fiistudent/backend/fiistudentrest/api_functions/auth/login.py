from google.cloud import datastore
from fiistudentrest.models import ndb, Student, Token, Professor
import uuid
import hashlib
import hug
import jwt

from datetime import datetime, timedelta

config = {
    'jwt_secret': 'super-secret-key-please-change',
    # Token will expire in 3600 seconds if it is not refreshed and the user will be required to log in again.
    'token_expiration_seconds': 3600,
    # If a request is made at a time less than 1000 seconds before expiry, a new jwt is sent in the response header.
    'token_refresh_seconds': 1000,
    'jwt_algorithm': 'HS256'
}


def hash_password(password):
    """ Encode a password """
    # uuid is used to generate a random number
    salt = uuid.uuid4().hex
    return hashlib.sha256(salt.encode() + password.encode()).hexdigest() + ':' + salt


def check_password(hashed_password, user_password):
    """ Decode a password """
    password, salt = hashed_password.split(':')
    return password == hashlib.sha256(salt.encode() + user_password.encode()).hexdigest()


def login_function(email, password):
    """ Verify if the user exists in the datastore """
    query = Student.query()
    query.add_filter('email', '=', email)
    # deleted query.add_filter('password', '=', password)
    query_it = query.fetch()
    for ent in query_it:
        if ent is None:
            print('The user is not in our database or introduced the wrong credentials.')
        elif check_password(ent.password, password):  # unchecked modification here
            print('The user exists in our database.')
            return ent
    return None


def login_function_professor(email, password):
    query = Professor.query()
    query.add_filter('email', '=', email)
    query_it = query.fetch()
    for ent in query_it:
        if ent is None:
            print('The user is not in our database or introduced the wrong credentials.')
        elif check_password(ent.password, password):
            print('The user exists in our database.')
            return ent
    return None


def update_token_student(jwt_token, user):
    """ Updates existing token for user or creates new one """

    query = Token.query()
    query.add_filter('user', '=', user.key)
    query_list = list(query.fetch())

    if query_list:
        for token_entity in query_list:
            token_entity.token = jwt_token.decode("utf-8")
            token_entity.put()
    else:
        token = Token(token=jwt_token.decode("utf-8"), user_student=user.key)
        token.put()


def update_token_professor(jwt_token, user):
    """ Updates existing token for user or creates new one """

    query = Token.query()
    query.add_filter('user', '=', user.key)
    query_list = list(query.fetch())

    if query_list:
        for token_entity in query_list:
            token_entity.token = jwt_token.decode("utf-8")
            token_entity.put()
    else:
        token = Token(token=jwt_token.decode("utf-8"), user_professor=user.key)
        token.put()


def generate_token(user):
    """ Generates token encoding user urlsafe and time """

    payload = {
        'user_url': user.urlsafe,
        'exp': datetime.utcnow() + timedelta(seconds=config['token_expiration_seconds'])
    }
    return jwt.encode(payload, config['jwt_secret'], config['jwt_algorithm'])


def exists_token(token):
    """ Chekcs whether the token exists in the database """

    query = Token.query()
    query.add_filter('token', '=', token)
    query_list = list(query.fetch())

    if query_list:
        for token_entity in query_list:
            if token_entity:
                return True

    return False


def verify_token(authorization):
    """ Checks if given token is valid """
    try:
        token = authorization.split(' ')[1]
        decoding = jwt.decode(token, config['jwt_secret'], config['jwt_algorithm'])
        if not exists_token(token):
            return None

        return decoding['user_url']

    except jwt.InvalidTokenError:
        return None


@hug.local()
@hug.cli()
@hug.get()
def login(email: hug.types.text, password: hug.types.text):
    """Verify if the user exists in the datastore and return an appropriate json response for every scenario"""
    user = login_function(email.lower(), password)
    user_professor = login_function_professor(email, password)
    if user != None:
        jwt_token = generate_token(user)
        update_token_student(jwt_token, user)
        return {'token': jwt_token.decode("utf-8"), 'errors': []}
    elif user_professor != None:
        jwt_token = generate_token(user_professor)
        update_token_professor(jwt_token, user_professor)
        return {'token': jwt_token.decode("utf-8"), 'errors': []}
    else:
        return {'status': 'error', 'errors': [
            {'for': 'login', 'message': 'The username or password you entered did not match our records.'}]}


if __name__ == '__main__':
    login.interface.cli()
