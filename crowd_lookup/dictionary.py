import re
import models
import browser
import tools
import point
from manager import AllManagers

class NineDict:
    def __init__(self):
        self._google_translate = browser.GoogleTranslate()
        self._google_image = browser.GoogleImage()
        self._urban_dictionary = browser.UrbanDictionary()
        self._youtube = browser.YouTube()

        self._mgr = AllManagers()

    def get_recomm(self, gag_id, user, excl_recomm_ids):
        words = self._mgr.recomm.query(gag_id, user)
        words = filter(lambda word: word.id not in excl_recomm_ids, words)[:5]
        return tools._make_dicts(words)

    def delete_recomm(self, word, gag_id, user):
        return self._mgr.recomm.going_down(word, gag_id, user)

    def get_expls(self, word, gag_id, user, excl_expl_ids):
        expls = self._mgr.prefer.query(word, gag_id, user)
        if not expls:
            self._get_expls_from_web(word, gag_id)
            expls = self._mgr.prefer.query(word, gag_id, user)
        expls = filter(lambda expl: expl.id not in excl_expl_ids, expls)[:5]
        self._mgr.recomm.going_up(word, gag_id, user)
        res = tools._make_dicts(expls)
        for i, item in enumerate(res):
            expl = self._mgr.explain.get(expl_id=item['id'])
            res[i]['liked'] = self._mgr.prefer.is_liked(user, expl)
        return res

    def delete_expl(self, expl, gag_id, user):
        return self._mgr.prefer.going_down(expl, gag_id, user)

    def like_expl(self, expl, gag_id, user):
        return self._mgr.prefer.going_up(expl, gag_id, user)

    def neutral_expl(self, expl, gag_id, user):
        return self._mgr.prefer.going_plain(expl, gag_id, user)

    def provide_expl(self, expl_str, word):
        expl = self._mgr.explain.add(expl_str=expl_str, word=word, init_score=1.0)
        if not expl:
            return None
        return tools._make_dicts([expl])

    def _get_expls_from_web(self, word, gag_id):
        gt_upper_bound = point.GT_SINGLE_EXPL_INIT_POINT if re.match('^[^\s]+$', word.content) else point.GT_MULTIPLE_EXPL_INIT_POINT
        num_expls = self._get_expls_from_browser(word, self._google_translate, gt_upper_bound)

        ud_upper_bound = point.UD_NO_GT_EXPL_INIT_POINT if num_expls == 0 else point.UD_WITH_GT_EXPL_INIT_POINT
        self._get_expls_from_browser(word, self._urban_dictionary, ud_upper_bound)

        gi_upper_bound = point.GI_EXPL_INIT_POINT
        self._get_expls_from_browser(word, self._google_image, gi_upper_bound)

        yt_upper_bound = point.YT_EXPL_INIT_POINT
        self._get_expls_from_browser(word, self._youtube, yt_upper_bound)

    def _get_expls_from_browser(self, word, br, upper_bound):
        expl_tuples = br.query(word.content)
        rank = 1
        for expl_str, expl_url, expl_repr_type in expl_tuples:
            init_score = upper_bound / rank ** 0.5
            self._mgr.explain.add(word=word,
                                  repr_type=expl_repr_type,
                                  expl_str=expl_str,
                                  source=br.get_name(),
                                  link=expl_url,
                                  init_score=init_score
                                 )
            rank += 1
        return len(expl_tuples)

