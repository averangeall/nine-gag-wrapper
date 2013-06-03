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
    expl_id = request.GET.get('expl_id', None)
    expl_str = request.GET.get('expl_str', '')
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
        if expl_id:
            urls.append(('delete explain: %s' % expl_id,
                         '/lookup/explain/delete/?gag_id=%s&user_id=%d&valid_key=hello&expl_id=%s' % (gag_id, user_id, expl_id)))
            urls.append(('like explain: %s' % expl_id,
                         '/lookup/explain/like/?gag_id=%s&user_id=%d&valid_key=hello&expl_id=%s' % (gag_id, user_id, expl_id)))
        if expl_str != '':
            urls.append(('provide explain: %s, %s' % (word_id, expl_str),
                         '/lookup/explain/provide/?gag_id=%s&user_id=%d&valid_key=hello&word_id=%s&expl_str=%s' % (gag_id, user_id, word_id, expl_str)))
    dictt = {}
    dictt['gag_id'] = gag_id
    dictt['urls'] = urls
    dictt['word_str'] = word_str
    dictt['word_id'] = word_id if word_id is not None else ''
    dictt['expl_id'] = expl_id if expl_id is not None else ''
    dictt['expl_str'] = expl_str
    return render_to_response('index.html', dictt)

def test(request):
    gag_id = 'ajYbzzx'
    word = mgr.word.get(word_id=635)
    recomms = models.Prefer.objects.filter(expl__word=word)
    return HttpResponse(make_json_respond('OKAY', [recomm.to_dict() for recomm in recomms]))

def get_recomm(request):
    gag_id, user, user_ip, is_valid = get_basic_info(request)
    if not is_valid:
        log.put(gag_id, user, user_ip, 'GET_RECOMM', False, 'key invalid')
        return HttpResponse(make_json_respond('INVALID'))

    recomms = dictt.get_recomm(gag_id, user)
    if recomms == None:
        log.put(gag_id, user, user_ip, 'GET_RECOMM', True, 'something went wrong')
        return HttpResponse(make_json_respond('FAIL'))
    log.put(gag_id, user, user_ip, 'GET_RECOMM', True, 'got %d recomms' % len(recomms))
    return HttpResponse(make_json_respond('OKAY', recomms))

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

    expl_id = request.GET.get('expl_id', None)

    expl = mgr.explain.get(expl_id=expl_id)

    success = dictt.delete_expl(expl, gag_id, user)
    if not success:
        return HttpResponse(make_json_respond('FAIL'))
    return HttpResponse(make_json_respond('OKAY'))

def like_explain(request):
    gag_id, user, user_ip, is_valid = get_basic_info(request)
    if not is_valid:
        return HttpResponse(make_json_respond('INVALID'))

    expl_id = request.GET.get('expl_id', None)

    expl = mgr.explain.get(expl_id=expl_id)

    success = dictt.like_expl(expl, gag_id, user)
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
    expl = mgr.explain.add(expl_str=expl_str, word=word, init_score=1.0)

    success = expl is not None
    if not success:
        return HttpResponse(make_json_respond('FAIL'))
    return HttpResponse(make_json_respond('OKAY'))


