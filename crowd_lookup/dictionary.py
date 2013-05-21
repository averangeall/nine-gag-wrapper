import browser
import models

class NineDict:
    def __init__(self):
        self._dr_eye = browser.DrEye()
        self._google_image = browser.GoogleImage()

    def get_recomm(self, gag_id, user_id):
        #recomms = models.Recomm.objects.filter(gag_id=gag_id)
        #words = [recomm.word.content for recomm in recomms]
        words = ['Cool', 'Yes']
        return words

    def delete_recomm(self, word_id, gag_id, user_id):
        return True

    def get_expls_by_word(self, word, gag_id, user_id):
        expls = []
        expls += self._get_expls_in_database(word, gag_id)
        if len(expls) == 0:
            expls += self._get_expls_from_web(word, gag_id)
        return expls

    def get_expls_by_word_id(self, word_id, gag_id, user_id):
        words = models.Word.objects.filter(id=word_id)
        if len(words) == 0:
            return None
        assert len(words) == 1
        return get_expls_by_word(words[0], gag_id, user_id)

    def get_expls_by_word_str(self, word_str, gag_id, user_id):
        word_str = self._normalize_word_str(word_str)
        if word_str == '':
            return None
        words = models.Word.objects.filter(content=word_str)
        if len(words) == 0:
            new = models.Word(content=word_str)
            new.save()
            return new
        else:
            assert len(words) == 1
            return words[0]

    def delete_expl(self, expl_id, word_id, gag_id, user_id):
        return True

    def add_expl(self, expl_str, word_id, gag_id, user_id):
        expl_str = expl_str.strip()
        if expl_str == '':
            return False
        return True

    def _normalize_word_str(self, word_str):
        return word_str.strip().lower()

    def _make_dict_expls(self, expls):
        return [expl.to_dict() for expl in expls]

    def _get_expls_in_database(self, word, gag_id, user_id):
        expls = models.Explain.objects.filter(word=word)
        return _make_dict_expls(expls)

    def _get_expls_from_web(self, word, gag_id):
        expls = []
        #expls += self._get_expls_from_browser(word, self._dr_eye)
        #expls += self._get_expls_from_browser(word, self._google_image)
        return _make_dict_expls(expls)

    def _get_expls_from_browser(self, word, br):
        expl_tuples = self._dr_eye.query(word.content)
        for expl_str, expl_url, expl_repr_type in expl_tuples:
            expl = models.Explain(word=word,
                                  repr_type=expl_repr_type,
                                  content=expl_str,
                                  source=br.get_name(),
                                  link=expl_url)
            expl.save()
        return _make_dict_expls(expls)

