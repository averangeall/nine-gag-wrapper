import random
import models
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
    def get(self, gag_id, word):
        recomms = models.Recomm.objects.filter(gag_id=gag_id, word=word)
        if not recomms.count():
            return None
        assert len(recomms) == 1
        recomm = recomms[0]
        return recomm

    def query(self, gag_id, **kwargs):
        if 'user' not in kwargs:
            return self._query_by_gag_id(gag_id)
        else:
            if 'valence' not in kwargs:
                return None
            return self._query_by_user(gag_id, kwargs['user'], kwargs['valence'])
        return None

    def _query_by_gag_id(self, gag_id):
        recomms = models.Recomm.objects.filter(gag_id=gag_id, score__gt=0.5)
        return recomms

    def _query_by_user(self, gag_id, user, valence):
        records = models.RecommRecord.objects.filter(user=user, val_type=valence)
        recomms = [record.recomm for record in records if record.recomm.gag_id == gag_id]
        return recomms

    def going_up(self, word, gag_id, user):
        recomm = self.get(gag_id, word)
        record = self._get_record(user, recomm)
        if self._went_to(record, models.RecommRecord.VAL_POSITIVE):
            return
        if not recomm:
            recomm = self._create(gag_id, word)
        self._change_score(recomm, +1.0)
        self._leave_record(record, recomm, user, models.RecommRecord.VAL_POSITIVE)

    def going_down(self, word, gag_id, user):
        recomm = self.get(gag_id, word)
        record = self._get_record(user, recomm)
        if self._went_to(record, models.RecommRecord.VAL_NEGATIVE):
            return False
        if not recomm:
            return False
        self._change_score(recomm, -1.0)
        self._leave_record(record, recomm, user, models.RecommRecord.VAL_NEGATIVE)
        return True

    def _get_record(self, user, recomm):
        records = models.RecommRecord.objects.filter(user=user, recomm=recomm)
        if not records.count():
            return None
        assert len(records) == 1
        record = records[0]
        return record

    def _went_to(self, record, valence):
        if record == None:
            return False
        return record.val_type == valence

    def _create(self, gag_id, word):
        recomm = models.Recomm(gag_id=gag_id, word=word, score=0.0)
        recomm.save()
        return recomm

    def _change_score(self, recomm, score_delta):
        assert recomm
        recomm.score += score_delta
        recomm.save()
        
    def _leave_record(self, record, recomm, user, valence):
        if record:
            record.val_type = valence
        else:
            assert recomm
            record = models.RecommRecord(user=user, recomm=recomm, val_type=valence)
        record.save()

class ExplainMgr(Manager):
    def get(self, expl_id):
        try:
            return models.Explain.objects.get(id=expl_id)
        except:
            return None

    def add(self, **kwargs):
        assert 'expl_str' in kwargs and 'word' in kwargs
        expl_str = kwargs['expl_str']
        word = kwargs['word']
        #expl_str = tools.normalize_str(expl_str)
        if expl_str == '':
            return None
        expls = models.Explain.objects.filter(content=expl_str, word=word)
        if not expls.count():
            repr_type = kwargs['repr_type'] if 'repr_type' in kwargs else self._guess_repr_type(expl_str)
            source = kwargs['source'] if 'source' in kwargs else 'User Provide'
            link = kwargs['link'] if 'link' in kwargs else ''
            expl = models.Explain(word=word,
                                  repr_type=repr_type,
                                  content=expl_str,
                                  source=source,
                                  link=link)
            expl.save()
        else:
            assert len(expls) == 1
            expl = expls[0]
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
        expls = models.Explain.objects.filter(word=word)
        prefers = models.Prefer.objects.filter(expl__word=word, score__lt=-1.0)
        records = models.PreferRecord.objects.filter(prefer__expl__word=word, 
                                                     user=user, 
                                                     val_type=models.PreferRecord.VAL_NEGATIVE)
        if not expls.count():
            return []
        remain = set(expls) - set([prefer.expl for prefer in prefers])
        if not remain:
            return []
        remain -= set([record.prefer.expl for record in records])
        random.seed(user.id)
        num_choose = 3
        if len(remain) < num_choose:
            return remain
        return random.sample(remain, num_choose)

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

class AllManagers:
    def __init__(self):
        self.word = WordMgr()
        self.explain = ExplainMgr()
        self.recomm = RecommMgr()
        self.prefer = PreferMgr()
        self.user = UserMgr()

