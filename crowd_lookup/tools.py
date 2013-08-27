import json
import random
import urllib
import imghdr
import models
import names
import manager

def _check_valid(gag_id, user, valid_key):
    if gag_id in [None, ''] or user  == None:
        return False
    return valid_key == user.key

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    else:
        return request.META.get('REMOTE_ADDR')

def get_basic_info(request):
    user_mgr = manager.UserMgr()

    gag_id = request.GET.get('gag_id', None)
    user_id = request.GET.get('user_id', None)
    user_ip = get_client_ip(request)
    valid_key = request.GET.get('valid_key', None)
    user = user_mgr.get(user_id)

    return gag_id, user, user_ip, _check_valid(gag_id, user, valid_key)

def make_json_respond(status, respond=None):
    res = {}
    res['status'] = status
    if respond is not None:
        res['respond'] = respond
    return json.dumps(res)

def normalize_str(string):
    return string.strip().lower()

def _make_dicts(objs):
    return [obj.to_dict() for obj in objs]

def gen_user_info():
    user_mgr = manager.UserMgr()
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

def gen_user_name():
    return random.choice(names.front) + random.choice(names.middle) + random.choice(names.back)

def is_image(url):
    tmp_fname = '/tmp/%d' % random.randint(0, 99999)
    urllib.urlretrieve(url, tmp_fname)
    return imghdr.what(tmp_fname) != None

def _substCost(x,y):
    if x == y: return 0
    else: return 2

def  minEditDist(target, source):
    n = len(target)
    m = len(source)

    distance = [[0 for i in range(m+1)] for j in range(n+1)]

    for i in range(1,n+1):
        distance[i][0] = distance[i-1][0] + 1

    for j in range(1,m+1):
        distance[0][j] = distance[0][j-1] + 1

    for i in range(1,n+1):
        for j in range(1,m+1):
           distance[i][j] = min(distance[i-1][j]+1,
                                distance[i][j-1]+1,
                                distance[i-1][j-1]+_substCost(source[j-1],target[i-1]))
    return distance[n][m]


