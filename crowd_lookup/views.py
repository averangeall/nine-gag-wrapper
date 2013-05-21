# Create your views here.

from django.http import HttpResponse
from django.shortcuts import render_to_response
from dictionary import NineDict
from logger import Logger
from tools import get_basic_info, make_json_respond

dictt = NineDict()
log = Logger()

def index(request):
    testings = [
        ('get recomm', '/lookup/recomm/get/?gag_id=ae8ffg&user_id=hf823&valid_key=hello'),
        ('delete recomm', '/lookup/recomm/delete/?gag_id=ae8ffg&user_id=hf823&valid_key=hello&word_id=35'),
    ]
    return render_to_response('index.html', {'testings': testings})

def get_recomm(request):
    gag_id, user_id, user_ip, is_valid = get_basic_info(request)
    if not is_valid:
        log.put(gag_id, user_id, user_ip, 'GET_RECOMM', False, 'key invalid')
        return HttpResponse(make_json_respond('INVALID'))

    recomm = dictt.get_recomm(gag_id, user_id)
    if recomm == None:
        log.put(gag_id, user_id, user_ip, 'GET_RECOMM', True, 'something went wrong')
        return HttpResponse(make_json_respond('FAIL'))
    log.put(gag_id, user_id, user_ip, 'GET_RECOMM', True, 'got %d recomm' % len(recomm))
    return HttpResponse(make_json_respond('OKAY', recomm))

def delete_recomm(request):
    gag_id, user_id, user_ip, is_valid = get_basic_info(request)
    if not is_valid:
        return HttpResponse(make_json_respond('INVALID'))

    word_id = request.GET.get('word_id', None)
    success = dictt.delete_recomm(word_id, gag_id, user_id)
    if not success:
        return HttpResponse(make_json_respond('FAIL'))
    return HttpResponse(make_json_respond('OKAY'))

def query_explain(request):
    gag_id, user_id, user_ip, is_valid = get_basic_info(request)
    if not is_valid:
        return HttpResponse(make_json_respond('INVALID'))

    word_id = request.GET.get('word_id', None)
    if word_id is not None:
        expls = dictt.get_expls_by_word_id(word_id, gag_id, user_id)
    else:
        word_str = request.GET.get('word_str', '')
        expls = dictt.get_expls_by_word_str(word_str, gag_id, user_id)
    if expls == None:
        return HttpResponse(make_json_respond('FAIL'))
    return HttpResponse(make_json_respond('OKAY', expls))

def delete_explain(request):
    gag_id, user_id, user_ip, is_valid = get_basic_info(request)
    if not is_valid:
        return HttpResponse(make_json_respond('INVALID'))

    word_id = request.GET.get('word_id', None)
    expl_id = request.GET.get('expl_id', None)
    success = dictt.delete_expl(expl_id, word_id, gag_id, user_id)
    if not success:
        return HttpResponse(make_json_respond('FAIL'))
    return HttpResponse(make_json_respond('OKAY'))

def provide_explain(request):
    gag_id, user_id, user_ip, is_valid = get_basic_info(request)
    if not is_valid:
        return HttpResponse(make_json_respond('INVALID'))

    word_id = request.GET.get('word_id', None)
    expl_str = request.GET.get('expl_str', '')
    success = dictt.add_expl(expl_str, word_id, gag_id, user_id)
    if not success:
        return HttpResponse(make_json_respond('FAIL'))
    return HttpResponse(make_json_respond('OKAY'))


