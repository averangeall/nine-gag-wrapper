# Create your views here.

import os
import re
from urllib import urlencode
from django.http import HttpResponse
from django.shortcuts import render_to_response
import models
from dictionary import NineDict
from tools import get_basic_info, make_json_respond, gen_user_info, get_client_ip
from manager import AllManagers
import treasures

dictt = NineDict()
mgr = AllManagers()

def index(request):
    user_id = 119640008
    user_key = 'AQ6h7OqByGjfSh2DraYtqcei1V6Tmgx0'

    gag_id = request.GET.get('gag_id', 'ajYbzzx').encode('utf8')
    new_name = request.GET.get('new_name', '').encode('utf8')
    treasure = request.GET.get('treasure', '').encode('utf8')
    word_str = request.GET.get('word_str', '').encode('utf8')
    word_id = request.GET.get('word_id', None)
    expl_id = request.GET.get('expl_id', None)
    expl_str = request.GET.get('expl_str', '').encode('utf8')
    excl_recomm_ids = request.GET.get('excl_recomm_ids', '').encode('utf8')
    excl_expl_ids = request.GET.get('excl_expl_ids', '').encode('utf8')
    notifi_id = request.GET.get('notifi_id', None)

    fields = []
    fields.append({'name': 'gag_id', 'value': gag_id})
    fields.append({'name': 'new_name', 'value': new_name})
    fields.append({'name': 'treasure', 'value': treasure})
    fields.append({'name': 'word_str', 'value': word_str})
    fields.append({'name': 'word_id', 'value': word_id})
    fields.append({'name': 'expl_id', 'value': expl_id})
    fields.append({'name': 'expl_str', 'value': expl_str})
    fields.append({'name': 'excl_recomm_ids', 'value': excl_recomm_ids})
    fields.append({'name': 'excl_expl_ids', 'value': excl_expl_ids})
    fields.append({'name': 'notifi_id', 'value': notifi_id})
    for field in fields:
        if field['value'] == None:
            field['value'] = ''

    default_args = {'gag_id': gag_id, 'user_id': user_id, 'valid_key': user_key}

    urls = []

    urls.append(('create user',
                 '/lookup/user/new/'))
    urls.append(('get recomm',
                 '/lookup/recomm/get/?' + urlencode(default_args)))
    urls.append(('info user',
                 '/lookup/user/info/?' + urlencode(default_args)))
    urls.append(('avatar image',
                 '/lookup/image/avatar/?' + urlencode(default_args)))
    urls.append(('count notifi',
                 '/lookup/notifi/count/?' + urlencode(default_args)))
    urls.append(('get notifi',
                 '/lookup/notifi/get/?' + urlencode(default_args)))
    urls.append(('info treasure',
                 '/lookup/treasure/info/?' + urlencode(default_args)))

    if new_name != '':
        new_name_args = dict(default_args, new_name=new_name)
        urls.append(('rename user: %s' % new_name,
                     '/lookup/user/rename/?' + urlencode(new_name_args)))

    if treasure != '':
        treasure_args = dict(default_args, treasure=treasure)
        urls.append(('treasure image: %s' % treasure,
                     '/lookup/image/treasure/?' + urlencode(treasure_args)))
        urls.append(('buy treasure: %s' % treasure,
                     '/lookup/treasure/buy/?' + urlencode(treasure_args)))
        urls.append(('use treasure: %s' % treasure,
                     '/lookup/treasure/use/?' + urlencode(treasure_args)))

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
            urls.append(('provide explain: %s, %s' % (word_id, expl_str.decode('utf8')),
                         '/lookup/explain/provide/?' + urlencode(expl_str_args)))
    if notifi_id:
        notifi_id_args = dict(default_args, notifi_id=notifi_id)
        urls.append(('enable notifi: %s' % notifi_id,
                     '/lookup/notifi/enable/?' + urlencode(notifi_id_args)))

    dictt = {}
    dictt['urls'] = urls
    dictt['fields'] = fields
    return render_to_response('index.html', dictt)

def test(request):
    import browser
    word_str = request.GET.get('word_str', '')
    youtube = browser.YouTube()
    return HttpResponse(make_json_respond('OKAY', [youtube.query(word_str)]))

def new_user(request):
    user_id, user_key, user_name = gen_user_info()
    mgr.user.create(user_id, user_key, user_name)
    mgr.log.add('generate new user', 'user_id: %s' % user_id, user_ip=get_client_ip(request))
    return HttpResponse(make_json_respond('OKAY', {'id': user_id, 'key': user_key}))

def rename_user(request):
    gag_id, user, user_ip, is_valid = get_basic_info(request)
    if not is_valid:
        mgr.log.add('rename user', 'invalid', user, user_ip)
        return HttpResponse(make_json_respond('INVALID'))

    new_name = request.GET.get('new_name', '')

    mgr.user.rename(user, new_name)
    mgr.log.add('rename user', 'new_name: %s' % new_name, user, user_ip)
    return HttpResponse(make_json_respond('OKAY'))

def info_user(request):
    gag_id, user, user_ip, is_valid = get_basic_info(request)
    if not is_valid:
        mgr.log.add('info user', 'invalid', user, user_ip)
        return HttpResponse(make_json_respond('INVALID'))

    mgr.log.add('info user', 'name: %s, score: %s, coin: %s' % (user.name, user.score, user.coin), user, user_ip)
    return HttpResponse(make_json_respond('OKAY', {'name': user.name, 'score': user.score, 'coin': user.coin}))

def get_recomm(request):
    gag_id, user, user_ip, is_valid = get_basic_info(request)
    if not is_valid:
        mgr.log.add('get recomm', 'invalid', user, user_ip)
        return HttpResponse(make_json_respond('INVALID'))

    excl_recomm_ids = request.GET.get('excl_recomm_ids', '').split(',')
    excl_recomm_ids = [int(recomm_id) for recomm_id in excl_recomm_ids if re.match(r'^\d+$', recomm_id)]

    recomms = dictt.get_recomm(gag_id, user, excl_recomm_ids)
    mgr.log.add('get recomm',
                'gag_id: %s, excl_recomm_ids: %s, got %d recomms' % (gag_id, excl_recomm_ids, len(recomms)),
                user, user_ip)
    return HttpResponse(make_json_respond('OKAY', {'recomms': recomms}))

def hate_recomm(request):
    gag_id, user, user_ip, is_valid = get_basic_info(request)
    if not is_valid:
        mgr.log.add('hate recomm', 'invalid', user, user_ip)
        return HttpResponse(make_json_respond('INVALID'))

    word_id = request.GET.get('word_id', None)

    word = mgr.word.get(word_id=word_id)
    success = dictt.delete_recomm(word, gag_id, user)
    mgr.log.add('hate recomm',
                'gag_id: %s, word: %s, sucess: %s' % (gag_id, word.id if word else None, bool(success)),
                user, user_ip)
    if not success:
        return HttpResponse(make_json_respond('FAIL'))
    return HttpResponse(make_json_respond('OKAY'))

def id_recomm(request):
    gag_id, user, user_ip, is_valid = get_basic_info(request)
    if not is_valid:
        mgr.log.add('id recomm', 'invalid', user, user_ip)
        return HttpResponse(make_json_respond('INVALID'))

    word_str = request.GET.get('word_str', '')

    word = mgr.word.get(word_str=word_str)
    success = word
    mgr.log.add('id recomm',
                'gag_id: %s, word: %s, sucess: %s' % (gag_id, word.id if word else None, bool(success)),
                user, user_ip)
    if not success:
        return HttpResponse(make_json_respond('FAIL'))
    return HttpResponse(make_json_respond('OKAY', {'id': word.id}))

def query_explain(request):
    gag_id, user, user_ip, is_valid = get_basic_info(request)
    if not is_valid:
        mgr.log.add('query explain', 'invalid', user, user_ip)
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
    mgr.log.add('query explain',
                'gag_id: %s, word: %s, got %d explains' % (gag_id, word.id if word else None, len(expls)),
                user, user_ip)
    return HttpResponse(make_json_respond('OKAY', {'word_id': word.id, 'expls': expls}))

def hate_explain(request):
    gag_id, user, user_ip, is_valid = get_basic_info(request)
    if not is_valid:
        mgr.log.add('hate explain', 'invalid', user, user_ip)
        return HttpResponse(make_json_respond('INVALID'))

    expl_id = request.GET.get('expl_id', None)
    expl = mgr.explain.get(expl_id=expl_id)

    success = dictt.delete_expl(expl, gag_id, user)
    mgr.log.add('hate explain',
                'gag_id: %s, expl: %s, success: %s' % (gag_id, expl.id if expl else None, bool(success)),
                user, user_ip)
    if not success:
        return HttpResponse(make_json_respond('FAIL'))
    return HttpResponse(make_json_respond('OKAY'))

def like_explain(request):
    gag_id, user, user_ip, is_valid = get_basic_info(request)
    if not is_valid:
        mgr.log.add('like explain', 'invalid', user, user_ip)
        return HttpResponse(make_json_respond('INVALID'))

    expl_id = request.GET.get('expl_id', None)
    expl = mgr.explain.get(expl_id=expl_id)

    success = dictt.like_expl(expl, gag_id, user)
    mgr.log.add('like explain',
                'gag_id: %s, expl: %s, success: %s' % (gag_id, expl.id if expl else None, bool(success)),
                user, user_ip)
    if not success:
        return HttpResponse(make_json_respond('FAIL'))
    return HttpResponse(make_json_respond('OKAY'))

def neutral_explain(request):
    gag_id, user, user_ip, is_valid = get_basic_info(request)
    if not is_valid:
        mgr.log.add('neutral explain', 'invalid', user, user_ip)
        return HttpResponse(make_json_respond('INVALID'))

    expl_id = request.GET.get('expl_id', None)
    expl = mgr.explain.get(expl_id=expl_id)

    success = dictt.neutral_expl(expl, gag_id, user)
    mgr.log.add('neutral explain',
                'gag_id: %s, expl: %s, success: %s' % (gag_id, expl.id if expl else None, bool(success)),
                user, user_ip)
    if not success:
        return HttpResponse(make_json_respond('FAIL'))
    return HttpResponse(make_json_respond('OKAY'))

def provide_explain(request):
    gag_id, user, user_ip, is_valid = get_basic_info(request)
    if not is_valid:
        mgr.log.add('provide explain', 'invalid', user, user_ip)
        return HttpResponse(make_json_respond('INVALID'))

    word_id = request.GET.get('word_id', None)
    expl_str = request.GET.get('expl_str', '')

    word = mgr.word.get(word_id=word_id)
    expls = dictt.provide_expl(expl_str, word, user)

    success = expls
    mgr.log.add('provide explain',
                'gag_id: %s, expls: %s, success: %s' % (gag_id, [expl['id'] if expl else None for expl in expls], bool(success)),
                user, user_ip)
    if not success:
        return HttpResponse(make_json_respond('FAIL'))
    return HttpResponse(make_json_respond('OKAY'))

def avatar_image(request):
    gag_id, user, user_ip, is_valid = get_basic_info(request)
    if not is_valid:
        mgr.log.add('avatar image', 'invalid', user, user_ip)
        return HttpResponse(make_json_respond('INVALID'))

    avatar = user.avatar if user.avatar else 'mario-big'
    fname = 'crowd_lookup/images/avatars/' + avatar + '-man.png'
    fr = open(fname)

    mgr.log.add('avatar image', 'avatar: %s' % user.avatar, user, user_ip)
    return HttpResponse(fr.read(), mimetype='image/png')

def treasure_image(request):
    gag_id, user, user_ip, is_valid = get_basic_info(request)
    if not is_valid:
        mgr.log.add('treasure image', 'invalid', user, user_ip)
        return HttpResponse(make_json_respond('INVALID'))

    treasure = request.GET.get('treasure', None)

    availables = [item['id'] for item in treasures.info]

    if treasure not in availables:
        mgr.log.add('avatar image', 'no such treasure: %s' % treasure, user, user_ip)
        blank = 'R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw=='
        return HttpResponse(blank.decode('base64'), mimetype='image/gif')

    enableds = mgr.user.enabled_treasures(user)
    suffix = 'enabled' if treasure in enableds else 'disabled'

    fname = 'crowd_lookup/images/treasures/' + treasure + '-treasure-' + suffix + '.png'
    fr = open(fname)
    mgr.log.add('treasure image', 'treasure: %s' % treasure, user, user_ip)
    return HttpResponse(fr.read(), mimetype='image/png')

def buy_treasure(request):
    gag_id, user, user_ip, is_valid = get_basic_info(request)
    if not is_valid:
        mgr.log.add('buy treasure', 'invalid', user, user_ip)
        return HttpResponse(make_json_respond('INVALID'))

    treasure = request.GET.get('treasure', None)

    availables = [item['id'] for item in treasures.info]
    if treasure not in availables:
        mgr.log.add('buy treasure', 'no such treasure: %s' % treasure, user, user_ip)
        return HttpResponse(make_json_respond('FAIL'))

    if user.coin < treasures.each[treasure]['price']:
        mgr.log.add('buy treasure', 'treasure: %s, not enough coins: %s' % (treasure, user.coin), user, user_ip)
        return HttpResponse(make_json_respond('FAIL'))

    enableds = mgr.user.enabled_treasures(user)
    if treasure in enableds:
        mgr.log.add('buy treasure', 'treasure: %s, already bought' % treasure, user, user_ip)
        return HttpResponse(make_json_respond('FAIL'))

    mgr.user.buy_treasure(user, treasure)

    mgr.log.add('buy treasure', 'treasure: %s, remaining coins: %s' % (treasure, user.coin), user, user_ip)
    return HttpResponse(make_json_respond('OKAY'), {'coins': user.coin})

def use_treasure(request):
    gag_id, user, user_ip, is_valid = get_basic_info(request)
    if not is_valid:
        mgr.log.add('use treasure', 'invalid', user, user_ip)
        return HttpResponse(make_json_respond('INVALID'))

    treasure = request.GET.get('treasure', None)

    if not treasure:
        mgr.log.add('use treasure', 'no treasure selected', user, user_ip)
        return HttpResponse(make_json_respond('FAIL'))

    enableds = mgr.user.enabled_treasures(user)
    if treasure not in enableds:
        mgr.log.add('use treasure', 'treasure: %s, not in enabled list' % treasure, user, user_ip)
        return HttpResponse(make_json_respond('FAIL'))

    mgr.user.use_treasure(user, treasure)

    mgr.log.add('use treasure', 'treasure: %s' % treasure, user, user_ip)
    return HttpResponse(make_json_respond('OKAY'))

def count_notifi(request):
    gag_id, user, user_ip, is_valid = get_basic_info(request)
    if not is_valid:
        mgr.log.add('count notifi', 'invalid', user, user_ip)
        return HttpResponse(make_json_respond('INVALID'))

    cnt = mgr.notifi.get_count(user)

    return HttpResponse(make_json_respond('OKAY', {'count': cnt}))

def get_notifi(request):
    gag_id, user, user_ip, is_valid = get_basic_info(request)
    if not is_valid:
        mgr.log.add('get notifi', 'invalid', user, user_ip)
        return HttpResponse(make_json_respond('INVALID'))

    notifis = mgr.notifi.get_by_user(user, True)

    mgr.log.add('get notifi', 'got %s notifis' % len(notifis), user, user_ip)
    return HttpResponse(make_json_respond('OKAY', {'notifis': notifis}))

def enable_notifi(request):
    gag_id, user, user_ip, is_valid = get_basic_info(request)
    if not is_valid:
        mgr.log.add('enable notifi', 'invalid', user, user_ip)
        return HttpResponse(make_json_respond('INVALID'))

    notifi_id = request.GET.get('notifi_id', None)
    notifi = mgr.notifi.get(notifi_id)
    success = mgr.notifi.enable(notifi, user)

    if not success:
        mgr.log.add('enable notifi', 'failed to enable notifi %s' % notifi_id, user, user_ip)
        return HttpResponse(make_json_respond('FAIL'))

    mgr.log.add('enable notifi', 'enabled notifi %s' % notifi_id, user, user_ip)
    return HttpResponse(make_json_respond('OKAY'))

def info_treasure(request):
    gag_id, user, user_ip, is_valid = get_basic_info(request)
    if not is_valid:
        mgr.log.add('info treasure', 'invalid', user, user_ip)
        return HttpResponse(make_json_respond('INVALID'))

    enableds = user.treasures.split(',')

    info = []
    for item in treasures.info:
        info.append({
            'id': item['id'],
            'name': item['name'],
            'price': item['price'],
            'enabled': item['id'] in enableds,
        })

    mgr.log.add('info treasure', '#treasures: %s, enableds: %s' % (len(info), user.treasures), user, user_ip)
    return HttpResponse(make_json_respond('OKAY', {'info': info}))

