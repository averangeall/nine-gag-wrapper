import browser
import models

class NineDict:
    def __init__(self):
        self._dr_eye = browser.DrEye()
        self._google_image = browser.GoogleImage()

    def get_recomm(self, gag_id, user_id):
        recomms = models.Recomm.objects.filter(gag_id=gag_id, score__gt=0.5)
        return self._make_dicts(recomms)

    def delete_recomm(self, word_id, gag_id, user_id):
        return True

    def get_expls_by_word_id(self, word_id, gag_id, user_id):
        try:
            word = models.Word.objects.get(id=word_id)
        except:
            return []
        return self._get_expls_by_word(word, gag_id, user_id)

    def get_expls_by_word_str(self, word_str, gag_id, user_id):
        word = self._get_word_from_word_str(word_str)
        user = models.User.objects.get(id=user_id)
        querieds = models.Queried.objects.filter(user_id=user_id, gag_id=gag_id, word=word)
        if not querieds:
            self._recomm_going_up(gag_id, word)
            queried = models.Queried(user_id=user_id, gag_id=gag_id, word=word)
            queried.save()
        return self._get_expls_by_word(word, gag_id, user_id)

    def delete_expl(self, expl_id, word_id, gag_id, user_id):
        return True

    def add_expl(self, expl_str, word_id, gag_id, user_id):
        expl_str = expl_str.strip()
        if expl_str == '':
            return False
        return True

    def _get_word_from_word_str(self, word_str):
        word_str = self._normalize_word_str(word_str)
        if word_str == '':
            return None
        words = models.Word.objects.filter(content=word_str)
        if not words:
            word = models.Word(content=word_str)
            word.save()
        else:
            assert len(words) == 1
            word = words[0]
        return word

    def _recomm_going_up(self, gag_id, word):
        recomms = models.Recomm.objects.filter(gag_id=gag_id, word=word)
        if not recomms:
            recomm = models.Recomm(gag_id=gag_id, word=word, score=0.0)
            recomm.save()
        else:
            assert len(recomms) == 1
            recomm = recomms[0]
            recomm.score += 1.0
            recomm.save()

    def _get_expls_by_word(self, word, gag_id, user_id):
        expls = []
        expls += self._get_expls_in_database(word, gag_id, user_id)
        if not expls:
            expls += self._get_expls_from_web(word, gag_id)
        return expls

    def _normalize_word_str(self, word_str):
        return word_str.strip().lower()

    def _make_dicts(self, objs):
        return [obj.to_dict() for obj in objs]

    def _get_expls_in_database(self, word, gag_id, user_id):
        expls = models.Explain.objects.filter(word=word)
        return self._make_dicts(expls)

    def _get_expls_from_web(self, word, gag_id):
        expls = []
        #expls += self._get_expls_from_browser(word, self._dr_eye)
        expls += self._get_expls_from_browser(word, self._google_image)
        return self._make_dicts(expls)

    def _get_expls_from_browser(self, word, br):
        expl_tuples = br.query(word.content)
        expls = []
        for expl_str, expl_url, expl_repr_type in expl_tuples:
            expl = models.Explain(word=word,
                                  repr_type=expl_repr_type,
                                  content=expl_str,
                                  source=br.get_name(),
                                  link=expl_url)
            expl.save()
            expls.append(expl)
        return expls

