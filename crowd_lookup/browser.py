# -*- coding: utf-8 -*-

import re, json
import time
import mechanize
import cookielib
from BeautifulSoup import BeautifulSoup

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

class GoogleImage(BaseBrowser):
    def query(self, word):
        url = 'https://www.google.com.tw/search?um=1&hl=zh-TW&biw=1366&bih=682&tbm=isch&q=%s&oq=%s' % (word.lower(), word.lower())
        soup = self._get_page_soup(url)
        res = []
        try:
            content = str(soup)
            res += re.findall(r'imgurl=(.+?)&amp', content)
        except:
            raise
        return url, res

if __name__ == '__main__':
    br = GoogleImage()
    for a in br.query('hello'):
        print a

