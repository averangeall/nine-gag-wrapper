import browser
import models

class NineDict:
    def __init__(self):
        self._dr_eye = browser.DrEye()
        self._google_image = browser.GoogleImage()

    def get_recomm(self, gag_id):
        gag_id = int(gag_id)
        recomms = models.Recomm.objects.filter(gag_id=gag_id)
        words = [recomm.word.content for recomm in recomms]
        return words

    def get_defis(self, text, gag_id):
        defis = []
        defis += self._get_defis_in_database(text, gag_id)
        if len(defis) == 0:
            defis += self._get_defis_from_web(text, gag_id)
        return defis

    def _get_word(self, text):
        words = models.Word.objects.filter(content=text)
        if len(words) == 0:
            new = models.Word(content=text)
            new.save()
            return new
        else:
            assert len(words) == 1
            return words[0]

    def _get_defis_in_database(self, text, gag_id):
        word = self._get_word(text)
        expls = models.Explain.objects.filter(word=word)
        return [expl.to_dict() for expl in expls[:5]]

    def _get_defis_from_web(self, text, gag_id):
        defis = []
        defis += self._get_defis_from_dr_eye(text)
        defis += self._get_defis_from_google_image(text)
        return defis

    def _get_defis_from_dr_eye(self, text):
        url, defis = self._dr_eye.query(text)
        word = self._get_word(text)
        expls = [models.Explain(word=word, 
                                repr_type=models.Explain.REPR_TEXT, 
                                content=defi, 
                                source='Dr. Eye', 
                                link=url) for defi in defis]
        for expl in expls:
            expl.save()
        return [expl.to_dict() for expl in expls[:2]]

    def _get_defis_from_google_image(self, text):
        url, defis = self._google_image.query(text)
        word = self._get_word(text)
        expls = [models.Explain(word=word, 
                                repr_type=models.Explain.REPR_IMAGE, 
                                content=defi, 
                                source='Google Image', 
                                link=url) for defi in defis]
        for expl in expls:
            expl.save()
        return [expl.to_dict() for expl in expls[:2]]

