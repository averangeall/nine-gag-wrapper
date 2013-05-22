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
        recomms = self._mgr.recomm.query(gag_id, user)
        return tools._make_dicts(recomms)

    def delete_recomm(self, word, gag_id, user):
        return self._mgr.recomm.going_down(word, gag_id, user)

    def get_expls(self, word, gag_id, user):
        self._mgr.recomm.going_up(word, gag_id, user)
        expls = []
        expls += self._get_expls_in_database(word, gag_id, user)
        if not expls:
            expls += self._get_expls_from_web(word, gag_id)
        return expls

    def delete_expl(self, expl, word, gag_id, user):
        return True

    def add_expl(self, expl, word, gag_id, user):
        return True

    def _get_expls_in_database(self, word, gag_id, user):
        expls = self._mgr.explain.query(word, gag_id, user)
        return tools._make_dicts(expls)

    def _get_expls_from_web(self, word, gag_id):
        expls = []
        #expls += self._get_expls_from_browser(word, self._dr_eye)
        expls += self._get_expls_from_browser(word, self._google_image)
        return tools._make_dicts(expls)

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

