# Create your views here.

from django.http import HttpResponse
from django.shortcuts import render_to_response
import models
from dictionary import NineDict
from logger import Logger
from tools import get_basic_info, make_json_respond
from manager import AllManagers

dictt = NineDict()
log = Logger()
mgr = AllManagers()

def index(request):
    gag_id = 'ajYbzzx'
    user_id = 84920
    word_str = request.GET.get('word_str', '')
    word_id = request.GET.get('word_id', None)
    urls = []
    urls.append(('get recomm', 
                 '/lookup/recomm/get/?gag_id=%s&user_id=%d&valid_key=hello' % (gag_id, user_id)))
    if word_str != '':
        urls.append(('query explain: %s' % word_str, 
                     '/lookup/explain/query/?gag_id=%s&user_id=%d&valid_key=hello&word_str=%s' % (gag_id, user_id, word_str)))
    if word_id:
        urls.append(('query explain: %s' % word_id,
                     '/lookup/explain/query/?gag_id=%s&user_id=%d&valid_key=hello&word_id=%s' % (gag_id, user_id, word_id)))
        urls.append(('delete recomm: %s' % word_id,
                     '/lookup/recomm/delete/?gag_id=%s&user_id=%d&valid_key=hello&word_id=%s' % (gag_id, user_id, word_id)))
    return render_to_response('index.html', {'gag_id': gag_id, 'urls': urls})

def test(request):
    gag_id, user, user_ip, is_valid = get_basic_info(request)
    word = mgr.word.get(word_str='sss')
    recomm = mgr.recomm.get(gag_id=gag_id, word=word)
    return HttpResponse(make_json_respond('OKAY', recomm.id))

def get_recomm(request):
    gag_id, user, user_ip, is_valid = get_basic_info(request)
    if not is_valid:
        log.put(gag_id, user, user_ip, 'GET_RECOMM', False, 'key invalid')
        return HttpResponse(make_json_respond('INVALID'))

    recomm = dictt.get_recomm(gag_id, user)
    if recomm == None:
        log.put(gag_id, user, user_ip, 'GET_RECOMM', True, 'something went wrong')
        return HttpResponse(make_json_respond('FAIL'))
    log.put(gag_id, user, user_ip, 'GET_RECOMM', True, 'got %d recomm' % len(recomm))
    return HttpResponse(make_json_respond('OKAY', recomm))

def delete_recomm(request):
    gag_id, user, user_ip, is_valid = get_basic_info(request)
    if not is_valid:
        return HttpResponse(make_json_respond('INVALID'))

    word_id = request.GET.get('word_id', None)

    word = mgr.word.get(word_id=word_id)
    success = dictt.delete_recomm(word, gag_id, user)
    if not success:
        return HttpResponse(make_json_respond('FAIL'))
    return HttpResponse(make_json_respond('OKAY'))

def query_explain(request):
    gag_id, user, user_ip, is_valid = get_basic_info(request)
    if not is_valid:
        return HttpResponse(make_json_respond('INVALID'))

    word_id = request.GET.get('word_id', None)
    word_str = request.GET.get('word_str', '')

    if word_id is not None:
        word = mgr.word.get(word_id=word_id)
    else:
        word = mgr.word.get(word_str=word_str)

    expls = dictt.get_expls(word, gag_id, user)
    if expls == None:
        return HttpResponse(make_json_respond('FAIL'))
    return HttpResponse(make_json_respond('OKAY', expls))

def delete_explain(request):
    gag_id, user, user_ip, is_valid = get_basic_info(request)
    if not is_valid:
        return HttpResponse(make_json_respond('INVALID'))

    word_id = request.GET.get('word_id', None)
    expl_id = request.GET.get('expl_id', None)

    word = mgr.word.get(word_id=word_id)
    expl = mgr.explain.get(expl_id=expl_id)

    success = dictt.delete_expl(expl, word, gag_id, user)
    if not success:
        return HttpResponse(make_json_respond('FAIL'))
    return HttpResponse(make_json_respond('OKAY'))

def provide_explain(request):
    gag_id, user, user_ip, is_valid = get_basic_info(request)
    if not is_valid:
        return HttpResponse(make_json_respond('INVALID'))

    word_id = request.GET.get('word_id', None)
    expl_str = request.GET.get('expl_str', '')

    word = mgr.word.get(word_id=word_id)
    expl = mgr.explain.get(expl_str=expl_str, word=word)

    success = dictt.add_expl(expl, word, gag_id, user)
    if not success:
        return HttpResponse(make_json_respond('FAIL'))
    return HttpResponse(make_json_respond('OKAY'))


