import os
import random
import string
import time

import urllib
import random
import time
import string
import urlparse

from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordResetForm
from django.conf import settings
from django.utils.hashcompat import sha_constructor
from django.template.defaultfilters import stringfilter

import defaults


@stringfilter
def unquote(value):
    return urllib.unquote(value)
    
def get_random_string(str_len=20):
    randtime = str(time.time()).split('.')[0]
    rand = ''.join([random.choice(randtime+string.letters+string.digits) for i in range(str_len)])
    random_string = sha_constructor(rand).hexdigest()[:str_len]
    return random_string


def get_uuid():
    """ Get a unique universal id """
    return str(uuid.uuid4()).lower()


def does_username_exist(username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return False

    return True

def does_email_exist(username):
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return False

    return True

def get_unique_username(length=20):
    length = 10
    for i in range(length):
        username = get_random_string(length+i)
        if not does_username_exist(username):
            return username

    return get_unique_string(28)


def get_first_last_from_name(name):
    first = ''
    last = ''
    if name:
        n = name.split(' ')
        if len(n) == 2:
            first = n[0]
            last = ' '.join(n[1:])
        elif len(n) > 2:
            first = ' '.join(n[:2])
            last = ' '.join(n[2:])
    return first, last


def get_aweber_params(get_data):
    params_dict = dict(urlparse.parse_qsl(unquote(get_data.urlencode())))
    try:
        params_dict['first_name'], params_dict['last_name'] = get_first_last_from_name(params_dict['name'])
    except:
        pass
    return params_dict

def create_new_user(email, name, password, is_active=False):
    username = email.split('@')[0].strip()
    if does_username_exist(username) or len(username) < 3:
        username = get_unique_username()
    new_user = User.objects.create_user(username, email, password)
    new_user.first_name, new_user.last_name = get_first_last_from_name(name)
    new_user.is_active = is_active
    new_user.save()
    return new_user

def get_user_by_email_or_none(email):
    user = None
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        pass
    return user
        
def encode_email(email, salt=defaults.AWEBER_EMAIL_ENCODING_SALT):
    encoded_email = sha_constructor(email+salt).hexdigest()
    return encoded_email


def is_email_valid(email, encoded_email):
    encoded = encode_email(email, defaults.AWEBER_EMAIL_ENCODING_SALT)
    return encoded_email == encoded




