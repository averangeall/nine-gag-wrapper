# Create your views here.

import re
from urllib import urlencode
from django.http import HttpResponse
from django.shortcuts import render_to_response
import models
from dictionary import NineDict
from logger import Logger
from tools import get_basic_info, make_json_respond, gen_user_info, get_client_ip
from manager import AllManagers

dictt = NineDict()
log = Logger()
mgr = AllManagers()

def index(request):
    user_id = 907954370
    user_key = 'lsopa7KtFmsJWv6UlZ78ZJ0z0Gsk5Qq3'
    gag_id = request.GET.get('gag_id', 'ajYbzzx')
    word_str = request.GET.get('word_str', '')
    word_id = request.GET.get('word_id', None)
    expl_id = request.GET.get('expl_id', None)
    expl_str = request.GET.get('expl_str', '')
    excl_recomm_ids = request.GET.get('excl_recomm_ids', '')
    excl_expl_ids = request.GET.get('excl_expl_ids', '')
    default_args = {'gag_id': gag_id, 'user_id': user_id, 'valid_key': user_key}
    urls = []

    urls.append(('create user',
                 '/lookup/user/new/'))
    urls.append(('get recomm',
                 '/lookup/recomm/get/?' + urlencode(default_args)))

    if excl_recomm_ids != '':
        excl_recomm_ids_args = dict(default_args, excl_recomm_ids=excl_recomm_ids)
        urls.append(('get recomm, excludes: %s' % excl_recomm_ids,
                     '/lookup/recomm/get/?' + urlencode(excl_recomm_ids_args)))

    if word_str != '':
        word_str_args = dict(default_args, word_str=word_str)
        urls.append(('query explain: %s' % word_str,
                     '/lookup/explain/query/?' + urlencode(word_str_args)))
        urls.append(('id recomm: %s' % word_str,
                     '/lookup/recomm/id/?' + urlencode(word_str_args)))

    if word_id:
        word_id_args = dict(default_args, word_id=word_id)
        urls.append(('query explain: %s' % word_id,
                     '/lookup/explain/query/?' + urlencode(word_id_args)))
        urls.append(('hate recomm: %s' % word_id,
                     '/lookup/recomm/hate/?' + urlencode(word_id_args)))
        if excl_expl_ids != '':
            excl_expl_ids_args = dict(word_id_args, excl_expl_ids=excl_expl_ids)
            urls.append(('query explain: %s, excludes: %s' % (word_id, excl_expl_ids),
                         '/lookup/explain/query/?' + urlencode(excl_expl_ids_args)))
        if expl_id:
            expl_id_args = dict(default_args, expl_id=expl_id)
            urls.append(('hate explain: %s' % expl_id,
                         '/lookup/explain/hate/?' + urlencode(expl_id_args)))
            urls.append(('like explain: %s' % expl_id,
                         '/lookup/explain/like/?' + urlencode(expl_id_args)))
            urls.append(('neutral explain: %s' % expl_id,
                         '/lookup/explain/neutral/?' + urlencode(expl_id_args)))
        if expl_str != '':
            expl_str_args = dict(word_id_args, expl_str=expl_str)
            urls.append(('provide explain: %s, %s' % (word_id, expl_str),
                         '/lookup/explain/provide/?' + urlencode(expl_str_args)))
    dictt = {}
    dictt['gag_id'] = gag_id
    dictt['urls'] = urls
    dictt['word_str'] = word_str
    dictt['word_id'] = word_id if word_id is not None else ''
    dictt['expl_id'] = expl_id if expl_id is not None else ''
    dictt['expl_str'] = expl_str
    dictt['excl_recomm_ids'] = excl_recomm_ids
    dictt['excl_expl_ids'] = excl_expl_ids
    return render_to_response('index.html', dictt)

def test(request):
    import browser
    word_str = request.GET.get('word_str', '')
    youtube = browser.YouTube()
    return HttpResponse(make_json_respond('OKAY', [youtube.query(word_str)]))

def new_user(request):
    user_id, user_key = gen_user_info()
    mgr.user.create(user_id, user_key)
    mgr.log.add('generate new user', 'user_id: %d' % user_id, user_ip=get_client_ip(request))
    return HttpResponse(make_json_respond('OKAY', {'id': user_id, 'key': user_key}))

def rename_user(request):
    gag_id, user, user_ip, is_valid = get_basic_info(request)
    if not is_valid:
        log.put(gag_id, user, user_ip, 'GET_RECOMM', False, 'key invalid')
        return HttpResponse(make_json_respond('INVALID'))

    new_name = request.GET.get('new_name', '')

    mgr.user.rename(user, new_name)
    return HttpResponse(make_json_respond('OKAY'))

def get_recomm(request):
    gag_id, user, user_ip, is_valid = get_basic_info(request)
    if not is_valid:
        log.put(gag_id, user, user_ip, 'GET_RECOMM', False, 'key invalid')
        return HttpResponse(make_json_respond('INVALID'))

    excl_recomm_ids = request.GET.get('excl_recomm_ids', '').split(',')
    excl_recomm_ids = [int(recomm_id) for recomm_id in excl_recomm_ids if re.match(r'^\d+$', recomm_id)]

    recomms = dictt.get_recomm(gag_id, user, excl_recomm_ids)
    if recomms == None:
        log.put(gag_id, user, user_ip, 'GET_RECOMM', True, 'something went wrong')
        return HttpResponse(make_json_respond('FAIL'))
    log.put(gag_id, user, user_ip, 'GET_RECOMM', True, 'got %d recomms' % len(recomms))
    return HttpResponse(make_json_respond('OKAY', recomms))

def hate_recomm(request):
    gag_id, user, user_ip, is_valid = get_basic_info(request)
    if not is_valid:
        return HttpResponse(make_json_respond('INVALID'))

    word_id = request.GET.get('word_id', None)

    word = mgr.word.get(word_id=word_id)
    success = dictt.delete_recomm(word, gag_id, user)
    if not success:
        return HttpResponse(make_json_respond('FAIL'))
    return HttpResponse(make_json_respond('OKAY'))

def id_recomm(request):
    gag_id, user, user_ip, is_valid = get_basic_info(request)
    if not is_valid:
        return HttpResponse(make_json_respond('INVALID'))

    word_str = request.GET.get('word_str', '')

    word = mgr.word.get(word_str=word_str)
    success = word
    if not success:
        return HttpResponse(make_json_respond('FAIL'))
    return HttpResponse(make_json_respond('OKAY', {'id': word.id}))

def query_explain(request):
    gag_id, user, user_ip, is_valid = get_basic_info(request)
    if not is_valid:
        return HttpResponse(make_json_respond('INVALID'))

    word_id = request.GET.get('word_id', None)
    word_str = request.GET.get('word_str', '')
    excl_expl_ids = request.GET.get('excl_expl_ids', '').split(',')
    excl_expl_ids = [int(expl_id) for expl_id in excl_expl_ids if re.match(r'^\d+$', expl_id)]

    if word_id is not None:
        word = mgr.word.get(word_id=word_id)
    else:
        word = mgr.word.get(word_str=word_str)

    expls = dictt.get_expls(word, gag_id, user, excl_expl_ids)
    if expls == None:
        return HttpResponse(make_json_respond('FAIL'))
    return HttpResponse(make_json_respond('OKAY', expls))

def hate_explain(request):
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

def neutral_explain(request):
    gag_id, user, user_ip, is_valid = get_basic_info(request)
    if not is_valid:
        return HttpResponse(make_json_respond('INVALID'))

    expl_id = request.GET.get('expl_id', None)
    expl = mgr.explain.get(expl_id=expl_id)

    success = dictt.neutral_expl(expl, gag_id, user)
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
    expl = dictt.provide_expl(expl_str, word)

    success = expl is not None
    if not success:
        return HttpResponse(make_json_respond('FAIL'))
    return HttpResponse(make_json_respond('OKAY', expl))

