import models
import browser
import tools
from manager import AllManagers

class NineDict:
    def __init__(self):
        self._google_translate = browser.GoogleTranslate()
        self._google_image = browser.GoogleImage()

        self._mgr = AllManagers()

    def get_recomm(self, gag_id, user):
        recomms = set()
        recomms |= set(self._mgr.recomm.query(gag_id))
        recomms |= set(self._mgr.recomm.query(gag_id, user=user, valence=models.RecommRecord.VAL_POSITIVE))
        recomms -= set(self._mgr.recomm.query(gag_id, user=user, valence=models.RecommRecord.VAL_NEGATIVE))
        return tools._make_dicts(recomms)

    def delete_recomm(self, word, gag_id, user):
        return self._mgr.recomm.going_down(word, gag_id, user)

    def get_expls(self, word, gag_id, user, excl_expl_ids):
        expls = self._mgr.prefer.query(word, gag_id, user)
        if not expls:
            self._get_expls_from_web(word, gag_id)
            expls = self._mgr.prefer.query(word, gag_id, user)
        expls = filter(lambda expl: expl.id not in excl_expl_ids, expls)[:5]
        self._mgr.recomm.going_up(word, gag_id, user)
        return tools._make_dicts(expls)

    def delete_expl(self, expl, gag_id, user):
        return self._mgr.prefer.going_down(expl, gag_id, user)

    def like_expl(self, expl, gag_id, user):
        return self._mgr.prefer.going_up(expl, gag_id, user)

    def neutral_explain(self, expl, gag_id, user):
        return self._mgr.prefer.going_plain(expl, gag_id, user)

    def provide_expl(self, expl_str, word):
        expl = self._mgr.explain.add(expl_str=expl_str, word=word, init_score=1.0)
        if not expl:
            return None
        return tools._make_dicts([expl])

    def _get_expls_from_web(self, word, gag_id):
        self._get_expls_from_browser(word, self._google_translate)
        self._get_expls_from_browser(word, self._google_image)

    def _get_expls_from_browser(self, word, br):
        expl_tuples = br.query(word.content)
        rank = 1
        for expl_str, expl_url, expl_repr_type in expl_tuples:
            init_score = 1.0 / rank ** 0.5
            self._mgr.explain.add(word=word,
                                  repr_type=expl_repr_type,
                                  expl_str=expl_str,
                                  source=br.get_name(),
                                  link=expl_url,
                                  init_score=init_score
                                 )
            rank += 1

