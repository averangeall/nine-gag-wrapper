import models
import point
#import tools

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
        #word_str = tools.normalize_str(word_str)
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
    def query(self, gag_id, **kwargs):
        words = []
        if 'user' not in kwargs:
            recomms = models.Recomm.objects.filter(gag_id=gag_id)
            counts = self._count_points(recomms)
            for word in counts:
                if counts[word] > point.MIN_RECOMM_VISIBLE_POINT:
                    words.append(word)
        else:
            if 'valence' not in kwargs:
                return None
            recomms = models.Recomm.objects.filter(gag_id=gag_id, user=kwargs['user'], val_type=kwargs['valence'])
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
            source = kwargs['source'] if 'source' in kwargs else 'User Provide'
            link = kwargs['link'] if 'link' in kwargs else ''
            expl = models.Explain(word=word,
                                  repr_type=repr_type,
                                  content=expl_str,
                                  source=source,
                                  link=link)
            expl.save()
            prefer = models.Prefer(expl=expl, score=init_score)
            prefer.save()
        return expl

    def _guess_repr_type(self, expl_str):
        # TODO: guess the representation type of the user given explain
        return models.Explain.REPR_TEXT

class PreferMgr(Manager):
    def get(self, expl):
        try:
            return models.Prefer.objects.get(expl=expl)
        except:
            return None

    def query(self, word, gag_id, user):
        all_prefers = models.Prefer.objects.filter(expl__word=word, score__gt=0.0).order_by('-score')
        positive_records = models.PreferRecord.objects.filter(prefer__expl__word=word, user=user, val_type=models.PreferRecord.VAL_POSITIVE)
        negative_records = models.PreferRecord.objects.filter(prefer__expl__word=word, user=user, val_type=models.PreferRecord.VAL_NEGATIVE)
        positive_prefers = [record.prefer for record in positive_records]
        negative_prefers = [record.prefer for record in negative_records]
        good_prefers = set()
        good_prefers |= set(positive_prefers)
        for prefer in all_prefers:
            if prefer not in negative_records:
                good_prefers.add(prefer)
        good_prefers = sorted(good_prefers, key=lambda prefer: -prefer.score)
        return [prefer.expl for prefer in good_prefers]

    def going_up(self, expl, gag_id, user):
        prefer = self.get(expl)
        record = self._get_record(prefer, gag_id, user)
        if self._went_to(record, models.PreferRecord.VAL_POSITIVE):
            return False
        if not prefer:
            prefer = self._create(expl)
        self._change_score(prefer, +1.0)
        self._leave_record(record, prefer, gag_id, user, models.PreferRecord.VAL_POSITIVE)
        return True

    def going_down(self, expl, gag_id, user):
        prefer = self.get(expl)
        record = self._get_record(prefer, gag_id, user)
        if self._went_to(record, models.PreferRecord.VAL_NEGATIVE):
            return False
        if not prefer:
            prefer = self._create(expl)
        self._change_score(prefer, -1.0)
        self._leave_record(record, prefer, gag_id, user, models.PreferRecord.VAL_NEGATIVE)
        return True

    def going_plain(self, expl, gag_id, user):
        prefer = self.get(expl)
        record = self._get_record(prefer, gag_id, user)
        if self._went_to(record, models.PreferRecord.VAL_POSITIVE):
            return False
        if not prefer:
            prefer = self._create(expl)
        self._change_score(prefer, 0.0)
        self._leave_record(record, prefer, gag_id, user, models.PreferRecord.VAL_PLAIN)
        return True

    def _get_record(self, prefer, gag_id, user):
        records = models.PreferRecord.objects.filter(prefer=prefer, gag_id=gag_id, user=user)
        if not records.count():
            return None
        assert len(records) == 1
        record = records[0]
        return record

    def _went_to(self, record, valence):
        if record == None:
            return False
        return record.val_type == valence

    def _create(self, expl):
        prefer = models.Prefer(expl=expl, score=0.0)
        prefer.save()
        return prefer

    def _change_score(self, prefer, score_delta):
        assert prefer
        prefer.score += score_delta
        prefer.save()
        
    def _leave_record(self, record, prefer, gag_id, user, valence):
        if record:
            record.val_type = valence
        else:
            assert prefer
            record = models.PreferRecord(user=user, gag_id=gag_id, prefer=prefer, val_type=valence)
        record.save()

class UserMgr(Manager):
    def get(self, user_id):
        try:
            return models.User.objects.get(id=user_id)
        except:
            return None

    def create(self, user_id, user_key):
        user = models.User(id=user_id, key=user_key, name=None)
        user.save()

class AllManagers:
    def __init__(self):
        self.word = WordMgr()
        self.explain = ExplainMgr()
        self.recomm = RecommMgr()
        self.prefer = PreferMgr()
        self.user = UserMgr()

