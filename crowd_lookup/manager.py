import re
import mimetypes
import models
import point
import tools
import treasures

class Manager:
    pass

class WordMgr(Manager):
    def get(self, **kwargs):
        if 'word_str' in kwargs:
            return self._get_by_str(kwargs['word_str'])
        elif 'word_id' in kwargs:
            return self._get_by_id(kwargs['word_id'])
        assert False

    def _get_by_str(self, word_str):
        word_str = tools.normalize_str(word_str)
        if word_str == '':
            return None
        words = models.Word.objects.filter(content=word_str)
        if not words.count():
            word = models.Word(content=word_str)
            word.save()
        else:
            assert len(words) == 1
            word = words[0]
        return word

    def _get_by_id(self, word_id):
        try:
            return models.Word.objects.get(id=word_id)
        except:
            return None

class RecommMgr(Manager):
    def query(self, gag_id, user):
        counts = self._general_query(gag_id)
        sort = sorted(counts.items(), key=lambda item: -item[1])
        
        positives = self._user_words(gag_id, user, models.Recomm.VAL_POSITIVE)
        negatives = self._user_words(gag_id, user, models.Recomm.VAL_NEGATIVE)

        words = []
        words.extend(positives)
        words.extend([item[0] for item in sort if item[0] not in negatives and item[0] not in positives])

        return words

    def _general_query(self, gag_id):
        recomms = models.Recomm.objects.filter(gag_id=gag_id)
        counts = self._count_points(recomms)
        pop_list = []
        for word in counts:
            if counts[word] < point.MIN_RECOMM_VISIBLE_POINT:
                pop_list.append(word)
        for word in pop_list:
            counts.pop(word)
        return counts

    def _user_words(self, gag_id, user, val_type):
        words = []
        recomms = models.Recomm.objects.filter(gag_id=gag_id, user=user, val_type=val_type)
        for recomm in recomms:
            words.append(recomm.word)
        return words

    def going_up(self, word, gag_id, user):
        self._going_to(word, gag_id, user, models.Recomm.VAL_POSITIVE)

    def going_down(self, word, gag_id, user):
        return self._going_to(word, gag_id, user, models.Recomm.VAL_NEGATIVE)

    def _going_to(self, word, gag_id, user, val_type):
        recomms = models.Recomm.objects.filter(word=word, gag_id=gag_id, user=user)
        if not recomms.count():
            recomm = models.Recomm(word=word, gag_id=gag_id, user=user, val_type=val_type)
        else:
            assert recomms.count() == 1
            recomm = recomms[0]
            if recomm.val_type == val_type:
                return False
            recomm.val_type = val_type
        recomm.save()
        return True

    def _count_points(self, recomms):
        counts = {}
        for recomm in recomms:
            if recomm.val_type == models.Recomm.VAL_POSITIVE:
                valence = +1.0
            elif recomm.val_type == models.Recomm.VAL_NEGATIVE:
                valence = -1.0
            else:
                assert False

            if recomm.user.id == 0:
                points = point.ADMIN_RECOMM_VAL_POINT * valence
            else:
                points = point.USER_RECOMM_VAL_POINT * valence

            if recomm.word in counts:
                counts[recomm.word] += points
            else:
                counts[recomm.word] = points

        return counts

class ExplainMgr(Manager):
    def get(self, expl_id):
        try:
            return models.Explain.objects.get(id=expl_id)
        except:
            return None

    def add(self, **kwargs):
        assert 'expl_str' in kwargs and 'word' in kwargs and 'init_score' in kwargs
        expl_str = kwargs['expl_str']
        word = kwargs['word']
        init_score = kwargs['init_score']
        #expl_str = tools.normalize_str(expl_str)
        if word == None or expl_str == '':
            return None
        expls = models.Explain.objects.filter(content=expl_str, word=word)
        if expls.count():
            assert len(expls) == 1
            expl = expls[0]
        else:
            repr_type = kwargs['repr_type'] if 'repr_type' in kwargs else self._guess_repr_type(expl_str)
            source = kwargs['source'] if 'source' in kwargs else 'Unknown'
            link = kwargs['link'] if 'link' in kwargs else ''
            expl = models.Explain(word=word,
                                  repr_type=repr_type,
                                  content=expl_str,
                                  source=source,
                                  link=link,
                                  init_score=init_score)
            expl.save()
        return expl

    def _guess_repr_type(self, expl_str):
        mime = mimetypes.guess_type(expl_str)
        if mime[0] and 'image' in mime[0]:
            return models.Explain.REPR_IMAGE
        return models.Explain.REPR_TEXT

class PreferMgr(Manager):
    def query(self, word, gag_id, user):
        counts = self._general_query(word, gag_id)
        sort = sorted(counts.items(), key=lambda item: -item[1])

        positives = self._user_expls(word, gag_id, user, models.Recomm.VAL_POSITIVE)
        negatives = self._user_expls(word, gag_id, user, models.Recomm.VAL_NEGATIVE)

        res = []
        res.extend(positives)
        res.extend([item[0] for item in sort if item[0] not in negatives and item[0] not in positives])

        return res

    def going_up(self, expl, gag_id, user):
        return self._going_to(expl, gag_id, user, models.Prefer.VAL_POSITIVE)

    def going_down(self, expl, gag_id, user):
        return self._going_to(expl, gag_id, user, models.Prefer.VAL_NEGATIVE)

    def going_plain(self, expl, gag_id, user):
        return self._going_to(expl, gag_id, user, None)

    def is_liked(self, user, expl):
        prefers = models.Prefer.objects.filter(expl=expl, user=user)
        if not prefers.count():
            return False
        assert prefers.count() == 1
        prefer = prefers[0]
        return prefer.val_type == models.Prefer.VAL_POSITIVE

    def _going_to(self, expl, gag_id, user, val_type):
        prefers = models.Prefer.objects.filter(expl=expl, user=user)
        if not prefers.count():
            if not val_type:
                return False
            prefer = models.Prefer(expl=expl, user=user, val_type=val_type)
        else:
            assert prefers.count() == 1
            prefer = prefers[0]
            if not val_type:
                prefer.delete()
                return True
            if prefer.val_type == val_type:
                return False
            prefer.val_type = val_type
        prefer.save()
        return True

    def _general_query(self, word, gag_id):
        expls = models.Explain.objects.filter(word=word)
        prefers = models.Prefer.objects.filter(expl__word=word)
        counts = self._count_points(expls, prefers)
        pop_list = []
        for expl in counts:
            if counts[expl] < point.MIN_EXPL_VISIBLE_POINT:
                pop_list.append(expl)
        for expl in pop_list:
            counts.pop(expl)
        return counts

    def _user_expls(self, word, gag_id, user, val_type):
        expls = []
        prefers = models.Prefer.objects.filter(expl__word=word, user=user, val_type=val_type)
        for prefer in prefers:
            expls.append(prefer.expl)
        return expls

    def _count_points(self, expls, prefers):
        counts = {}

        for expl in expls:
            counts[expl] = expl.init_score

        for prefer in prefers:
            if prefer.val_type == models.Prefer.VAL_POSITIVE:
                valence = +1.0
            elif prefer.val_type == models.Prefer.VAL_NEGATIVE:
                valence = -1.0
            else:
                assert False

            mo = re.match(r'^U(\d+)$', prefer.expl.source)
            if mo and int(mo.group(1)) == prefer.user.id:
                if prefer.val_type == models.Prefer.VAL_NEGATIVE:
                    points = -point.SELF_HATE_EXPL_POINT
                else:
                    points = 0.0
            elif prefer.user.id == 0:
                points = point.ADMIN_EXPL_VAL_POINT * valence
            else:
                points = point.USER_EXPL_VAL_POINT * valence

            if prefer.expl in counts:
                counts[prefer.expl] += points
            else:
                counts[prefer.expl] = points

        return counts

class UserMgr(Manager):
    def get(self, user_id):
        try:
            return models.User.objects.get(id=user_id)
        except:
            return None

    def create(self, user_id, user_key, user_name):
        user = models.User(id=user_id, key=user_key, name=user_name, score=0, coin=0, avatar=None, treasures='')
        user.save()

    def rename(self, user, new_name):
        user.name = new_name
        user.save()

    def enabled_treasures(self, user):
        enableds = filter(lambda x: x != '', user.treasures.split(','))
        return enableds

    def buy_treasure(self, user, treasure):
        enableds = self.enabled_treasures(user)
        assert treasure not in enableds
        enableds.append(treasure)
        user.treasures = ','.join(enableds)
        assert user.coin >= treasures.each[treasure]['price']
        user.coin -= treasures.each[treasure]['price']
        user.avatar = treasure
        user.save()

    def use_treasure(self, user, treasure):
        enableds = self.enabled_treasures(user)
        assert treasure in enableds
        user.avatar = treasure
        user.save()

class NotifiMgr(Manager):
    def get(self, notifi_id):
        try:
            return models.Notifi.objects.get(id=notifi_id)
        except:
            return None

    def like_word(self, word, gag_id, user):
        recomms = models.Recomm.objects.filter(gag_id=gag_id, word=word)
        if not recomms.count() or recomms.count() > 1:
            return

        assert recomms.count() == 1
        recomm = recomms[0]
        if recomm.user == user:
            return
        if recomm.val_type != models.Recomm.VAL_POSITIVE:
            return

        former = models.Notifi(evt_type=models.Notifi.EVT_SOMEONE_AGREE_KEYWORD,
                               user=recomm.user,
                               gag_id=gag_id,
                               word=word,
                               num_people=1,
                               coin_delta=3)

        latter = models.Notifi(evt_type=models.Notifi.EVT_YOU_AGREE_KEYWORD,
                               user=user,
                               gag_id=gag_id,
                               word=word,
                               num_people=1,
                               coin_delta=3)

        former.save()
        latter.save()

    def get_count(self, user):
        notifis = models.Notifi.objects.filter(user=user, seen=False)
        return notifis.count()

    def get_by_user(self, user, see=False):
        notifis = models.Notifi.objects.filter(user=user).order_by('-id')
        dicts = tools._make_dicts(notifis)
        if see:
            for notifi in notifis:
                notifi.seen = True
                notifi.save()
        return dicts

    def enable(self, notifi, user):
        if not notifi or notifi.user != user or notifi.received:
            return False
        if notifi.coin_delta:
            user.coin += notifi.coin_delta
        if notifi.score_delta:
            user.score += notifi.score_delta
        notifi.received = True
        notifi.save()
        user.save()
        return True

class LogMgr(Manager):
    def add(self, event_type, event_desc, user=None, user_ip=None):
        log = models.Log(event_type=event_type,
                         event_desc=event_desc,
                         user=user,
                         user_ip=user_ip)
        log.save()

class AllManagers:
    def __init__(self):
        self.word = WordMgr()
        self.explain = ExplainMgr()
        self.recomm = RecommMgr()
        self.prefer = PreferMgr()
        self.user = UserMgr()
        self.notifi = NotifiMgr()
        self.log = LogMgr()

