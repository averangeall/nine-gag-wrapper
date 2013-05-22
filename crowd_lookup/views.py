# Create your views here.

from django.http import HttpResponse
from django.shortcuts import render_to_response
from dictionary import NineDict
from logger import Logger
from tools import get_basic_info, make_json_respond

dictt = NineDict()
log = Logger()

def index(request):
    gag_id = 'ajYbzzx'
    user_id = 84920
    word_str = request.GET.get('word_str', '')
    urls = []
    urls.append(('get recomm', 
                 '/lookup/recomm/get/?gag_id=%s&user_id=%d&valid_key=hello' % (gag_id, user_id)))
    if word_str != '':
        urls.append(('query explain: %s' % word_str, 
                     '/lookup/explain/query/?gag_id=%s&user_id=%d&valid_key=hello&word_str=%s' % (gag_id, user_id, word_str)))
    return render_to_response('index.html', {'gag_id': gag_id, 'urls': urls})

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


