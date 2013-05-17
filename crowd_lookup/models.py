from django.db import models

class Word(models.Model):
    content = models.TextField()

class Recomm(models.Model):
    gag_id = models.IntegerField()
    word = models.ForeignKey(Word)
    score = models.FloatField()

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

    def to_dict(self):
        res = {}
        res['type'] = dict(self.REPR_TYPE_CHOICES)[self.repr_type]
        res['content'] = self.content
        return res

class Prefer(models.Model):
    gag_id = models.IntegerField()
    word = models.ForeignKey(Word)
    expl = models.ForeignKey(Explain)
    score = models.FloatField()

class Log(models.Model):
    LOG_ENTER_WORD = 'EN'
    LOG_FIND_EXPLAIN_ONLINE = 'FI'
    LOG_TYPE_CHOICES = (
        (LOG_ENTER_WORD, 'enter a word by user'),
        (LOG_FIND_EXPLAIN_ONLINE, 'find explanation from internet'),
    )

    log_type = models.CharField(max_length=2, choices=LOG_TYPE_CHOICES)
    timestamp = models.DateTimeField()
