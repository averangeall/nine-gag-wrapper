import json
import random
import models
from manager import UserMgr

def _check_valid(gag_id, user, valid_key):
    if gag_id in [None, ''] or user  == None:
        return False
    # TODO: make the validation working
    return valid_key == 'hello'

def _get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    else:
        return request.META.get('REMOTE_ADDR')

def get_basic_info(request):
    user_mgr = UserMgr()

    gag_id = request.GET.get('gag_id', None)
    user_id = request.GET.get('user_id', None)
    user_ip = _get_client_ip(request)
    valid_key = request.GET.get('valid_key', None)
    user = user_mgr.get(user_id)

    return gag_id, user, user_ip, _check_valid(gag_id, user, valid_key)

def make_json_respond(status, respond=None):
    res = {}
    res['status'] = status
    if respond is not None:
        res['respond'] = respond
    return json.dumps(res)

def normalize_str(self, string):
    return string.strip().lower()

def _make_dicts(objs):
    return [obj.to_dict() for obj in objs]

def gen_user_info():
    user_mgr = UserMgr()
    while True:
        user_id = random.randint(1, 2 ** 30)
        if user_mgr.get(user_id) == None:
            break

    user_key = ''
    choices = [chr(i) for i in range(ord('0'), ord('9') + 1)] + \
              [chr(i) for i in range(ord('A'), ord('Z') + 1)] + \
              [chr(i) for i in range(ord('a'), ord('z') + 1)]
    for i in range(32):
        user_key += random.choice(choices)

    return user_id, user_key
