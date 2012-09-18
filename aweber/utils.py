import os
import random
import string
import time

import urllib
import random
import time
import string
from django.utils.hashcompat import sha_constructor
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordResetForm
from django.conf import settings

from django.utils.hashcompat import sha_constructor

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


def get_unique_username(length=20):
    length = 10
    for i in range(length):
        username = get_random_string(length+i)
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
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


def get_aweber_args(request):
    args = {
        'name': urllib.unquote(request.GET.get('name', '')).strip(),
        'email': urllib.unquote(request.GET.get('email', '')).strip(),
        'type': urllib.unquote(request.GET.get('meta_adtracking', '')).strip(),
    }

    if 'name' in args:
        args['first_name'], args['last_name'] = get_first_last_from_name(args['name'])

    return args


def get_or_create_user(email):
    username = email.split('@')[0].strip()
    user, created = User.objects.get_or_create(email=email)
    if does_username_exist(username) or len(username) < 3:
        username = get_unique_username()
    user.username = username
    user.is_active = False
    user.set_unusable_password()
    user.save()
    return user, created


def get_user_or_none(email):
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return None
    return user





