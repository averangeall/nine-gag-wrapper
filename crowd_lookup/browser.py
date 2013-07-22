# -*- coding: utf-8 -*-

import re, json
import time
import mechanize
import cookielib
from BeautifulSoup import BeautifulSoup
import models

class BaseBrowser:
    def __init__(self):
        self._br = mechanize.Browser()
        self._set_cookie_jar()
        self._set_options()
        self._cur_gag = -1

    def _set_cookie_jar(self):
        cj = cookielib.LWPCookieJar()
        self._br.set_cookiejar(cj)

    def _set_options(self):
        self._br.set_handle_equiv(True)
        self._br.set_handle_redirect(True)
        self._br.set_handle_referer(True)
        self._br.set_handle_robots(False)
        self._br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)
        self._br.addheaders = [('User-agent', 
                                '''Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) 
                                Gecko/2008071615 
                                Fedora/3.0.1-1.fc9 
                                Firefox/3.0.1''')]

    def _remove_script_tag(self, src):
        dst = ''
        while src != '':
            pos = src.find('<script')
            if pos == -1:
                dst += src
                break
            else:
                dst += src[: pos]
                pos = src.find('</script>')
                src = src[pos + len('</script>') :]
        return dst

    def _get_page_content(self, url):
        page = self._br.open(url)
        content = page.read()
        return content

    def _get_page_soup(self, url):
        page = self._br.open(url)
        content = page.read()
        content = re.sub('/ >', '/>', content) # workaround for strange BeautifulSoup...
        content = re.sub(r'onclick=[^"\s]+', '', content) # workaround for Google Image...
        content = self._remove_script_tag(content)
        soup = BeautifulSoup(content)
        return soup

    def get_name(self):
        return ''

class DrEye(BaseBrowser):
    def query(self, word):
        url = 'http://dict.dreye.com/ews/%s--01--.html' % word.lower()
        soup = self._get_page_soup(url)
        res = []
        try:
            defis = soup.find('div', {'id': 'infotab1'}) \
                        .find('div', {'class': 'dict_cont'})
            for defi in defis:
                if 'attrs' in dir(defi) and dict(defi.attrs)[u'class'] == 'default':
                    for content in defi.contents:
                        content = unicode(content)
                        if re.sub('\s', '', content) != '<br/>':
                            content = content.strip()
                            content = re.sub(r'\d+\.\s*', '', content)
                            res.append(content)
        except:
            raise
        return url, res

    def get_name(self):
        return 'Dr. Eye'

class GoogleImage(BaseBrowser):
    def query(self, word):
        word = re.sub(r'\s+', '+', word)
        url = 'https://www.google.com.tw/search?um=1&hl=zh-TW&biw=1366&bih=682&tbm=isch&q=%s&oq=%s' % (word.lower(), word.lower())
        print url
        soup = self._get_page_soup(url)
        res = []
        try:
            content = str(soup)
            imgs = re.findall(r'imgurl=(.+?)&amp', content)
            for img in imgs:
                res.append((img, url, models.Explain.REPR_IMAGE))
        except:
            raise
        return res

    def get_name(self):
        return 'Google Image'

class GoogleTranslate(BaseBrowser):
    def query(self, word):
        used_url = 'http://translate.google.com/'
        self._br.open(used_url)
        self._br.select_form(name='text_form')
        self._br['text'] = word
        self._br['sl'] = ['en']
        self._br['tl'] = ['zh-TW']
        response = self._br.submit()
        content = response.read()
        content = self._remove_script_tag(content)
        soup = BeautifulSoup(content)
        res = []
        try:
            texts = soup.find('span', {'id': 'result_box'}) \
                        .find('span')
            assert texts
            fancy_url = 'http://translate.google.com/#en/zh-TW/%s' % word
            translate = texts.string
            if translate != word:
                res.append((texts.string, fancy_url, models.Explain.REPR_TEXT))
        except:
            raise
        return res

    def get_name(self):
        return 'Google Translate'

class UrbanDictionary(BaseBrowser):
    def query(self, word):
        word = re.sub(r'\s+', '+', word)
        url = 'http://www.urbandictionary.com/define.php?term=%s' % word
        soup = self._get_page_soup(url)
        eng_defi = soup.find('div', {'class': 'definition'}).string
        google_translate = GoogleTranslate()
        trans = google_translate.query(eng_defi)
        zh_defi = trans[0][0] if trans else ''
        return [(eng_defi + '\n' + zh_defi, url, models.Explain.REPR_TEXT)]

    def get_name(self):
        return 'Urban Dictionary'

class YouTube(BaseBrowser):
    def query(self, word):
        word = re.sub(r'\s+', '+', word)
        url = 'https://gdata.youtube.com/feeds/api/videos?q=%s&max-results=10&v=2&alt=json' % word
        content = self._get_page_content(url)
        search = json.loads(content)
        res = []
        for entry in search['feed']['entry']:
            info = entry['id']['$t']
            mo = re.match('.+?video:(.+)', info)
            video_id = mo.group(1)
            link_url = 'http://www.youtube.com/watch?v=%s' % video_id
            res.append((link_url, link_url, models.Explain.REPR_VIDEO))
        return res

    def get_name(self):
        return 'YouTube'

if __name__ == '__main__':
    br = GoogleImage()
    for a in br.query('hello'):
        print a

