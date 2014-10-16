from django.db import models

class Word(models.Model):
    content = models.TextField()

    def to_dict(self):
        res = {}
        res['id'] = self.id
        res['content'] = self.content
        return res

class Explain(models.Model):
    REPR_TEXT = 'TE'
    REPR_IMAGE = 'IM'
    REPR_VIDEO = 'VI'
    REPR_TYPE_CHOICES = (
        (REPR_TEXT, 'text'),
        (REPR_IMAGE, 'image'),
        (REPR_VIDEO, 'video'),
    )

    word = models.ForeignKey(Word)
    repr_type = models.CharField(max_length=2, choices=REPR_TYPE_CHOICES)
    content = models.TextField()
    source = models.TextField()
    link = models.TextField()
    init_score = models.FloatField()

    def to_dict(self):
        res = {}
        res['id'] = self.id;
        res['type'] = dict(self.REPR_TYPE_CHOICES)[self.repr_type]
        res['content'] = self.content
        res['source'] = self.source
        res['link'] = self.link
        return res

class User(models.Model):
    id = models.IntegerField(primary_key=True)
    key = models.TextField()
    name = models.TextField()
    score = models.IntegerField()
    coin = models.IntegerField()
    avatar = models.TextField()
    treasures = models.TextField()

class Recomm(models.Model):
    VAL_POSITIVE = 'PO'
    VAL_NEGATIVE = 'NE'
    VAL_TYPE_CHOICES = (
        (VAL_POSITIVE, 'positive'),
        (VAL_NEGATIVE, 'negative'),
    )

    user = models.ForeignKey(User)
    gag_id = models.TextField()
    word = models.ForeignKey(Word)
    val_type = models.CharField(max_length=2, choices=VAL_TYPE_CHOICES)

class Prefer(models.Model):
    VAL_POSITIVE = 'PO'
    VAL_NEGATIVE = 'NE'
    VAL_TYPE_CHOICES = (
        (VAL_POSITIVE, 'positive'),
        (VAL_NEGATIVE, 'negative'),
    )

    user = models.ForeignKey(User)
    gag_id = models.TextField()
    expl = models.ForeignKey(Explain)
    val_type = models.CharField(max_length=2, choices=VAL_TYPE_CHOICES)

class Notifi(models.Model):
    EVT_SOMEONE_AGREE_KEYWORD = 'SAKW'
    EVT_YOU_AGREE_KEYWORD = 'YAKW'
    EVT_TYPE_CHOICES = (
        (EVT_SOMEONE_AGREE_KEYWORD, 'someone-agree-keyword'),
        (EVT_YOU_AGREE_KEYWORD, 'you-agree-keyword'),
    )

    evt_type = models.CharField(max_length=4, choices=EVT_TYPE_CHOICES)
    user = models.ForeignKey(User)
    gag_id = models.TextField(null=True)
    word = models.ForeignKey(Word, null=True)
    expl = models.ForeignKey(Explain, null=True)
    num_people = models.IntegerField(null=True)
    coin_delta = models.IntegerField(null=True)
    score_delta = models.IntegerField(null=True)
    seen = models.BooleanField()
    received = models.BooleanField()

    def to_dict(self):
        res = {}
        res['id'] = self.id
        res['type'] = dict(self.EVT_TYPE_CHOICES)[self.evt_type]
        res['gag_id'] = self.gag_id
        res['word'] = self.word.content if self.word else None
        res['expl'] = self.expl.content if self.expl else None
        res['num_people'] = self.num_people
        res['coin_delta'] = self.coin_delta
        res['score_delta'] = self.score_delta
        res['seen'] = self.seen
        res['received'] = self.received
        return res

class Log(models.Model):
    event_type = models.TextField()
    event_desc = models.TextField()
    user = models.ForeignKey(User, null=True)
    user_ip = models.TextField(null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

