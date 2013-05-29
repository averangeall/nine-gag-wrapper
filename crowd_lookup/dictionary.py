import models
import browser
import tools
from manager import AllManagers

class NineDict:
    def __init__(self):
        self._dr_eye = browser.DrEye()
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

    def get_expls(self, word, gag_id, user):
        expls = self._mgr.prefer.query(word, gag_id, user)
        if not expls:
            self._get_expls_from_web(word, gag_id)
            expls = self._mgr.prefer.query(word, gag_id, user)
        self._mgr.recomm.going_up(word, gag_id, user)
        return tools._make_dicts(expls)

    def delete_expl(self, expl, gag_id, user):
        self._mgr.prefer.going_down(expl, gag_id, user)
        return True

    def add_expl(self, expl, word, gag_id, user):
        return True

    def _get_expls_from_web(self, word, gag_id):
        #self._get_expls_from_browser(word, self._dr_eye)
        self._get_expls_from_browser(word, self._google_image)

    def _get_expls_from_browser(self, word, br):
        expl_tuples = br.query(word.content)
        for expl_str, expl_url, expl_repr_type in expl_tuples:
            self._mgr.explain.add(word=word,
                                  repr_type=expl_repr_type,
                                  expl_str=expl_str,
                                  source=br.get_name(),
                                  link=expl_url
                                 )

