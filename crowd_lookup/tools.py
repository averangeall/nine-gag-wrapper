import json
import models

def _check_valid(gag_id, user_id, valid_key):
    if gag_id == '' or user_id == '' or valid_key == '':
        return False
    try:
        models.User.objects.get(id=user_id)
    except:
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
    gag_id = request.GET.get('gag_id', None)
    user_id = request.GET.get('user_id', None)
    user_ip = _get_client_ip(request)
    valid_key = request.GET.get('valid_key', None)
    return gag_id, user_id, user_ip, _check_valid(gag_id, user_id, valid_key)

def make_json_respond(status, respond=None):
    res = {}
    res['status'] = status
    if respond is not None:
        res['respond'] = respond
    return json.dumps(res)
