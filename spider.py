#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import requests
import logging
import html2text
import time
from bs4 import BeautifulSoup

_DebugLevel = logging.DEBUG
logging.basicConfig(level=logging.DEBUG)

_session = requests.session()

def login():
    """
    login to get cookies in _session
    :param user_id: your Tsinghua id "keh13" for example
    :param user_pass: your password
    :return:True if succeed
    """
    return True

def get_url(url):
    """
    _session.GET the page, handle the encoding and return the BeautifulSoup
    :param url: Page url
    :return: BeautifulSoup
    """
    r = _session.get(url)
    r.encoding = 'utf-8'
    soup = BeautifulSoup(r.content, "html.parser")
    return soup


class __BasePage(object):
    def __init__(self, root, url):
        self._root  = root
        self._url   = url
        self._soup  = get_url(root+url)

    def _get_first(self, selector, encode='utf-8'):
        return str(self._soup.select(selector)[0]).decode(encode)

    def _get_list(self, selector, encode='utf-8'):
        return self._soup.select(selector)


class index(__BasePage):
    def __init__(self, root, url):
        super(index, self).__init__(root, url)

    @property
    def pages(self):
        lines = self._get_list('.name')
        for line in lines:
            yield page(line.a['href'], '', line.text)

    @property
    def nexts(self):
        lines = self._get_list('.paging a')
        yield self
        for line in lines:
            yield index(line['href'],'')


class page(__BasePage):
    def __init__(self, root, url, name=None, title=None):
        super(page, self).__init__(root, url)
	self._html2text = html2text.HTML2Text()
	self._html2text.ignore_links = True
        self._title = None
        if name is None:
            self._name = url
        else:
            self._name = name.replace('/','_')


    @property
    def title(self):
        if self._title is None:
            self._title = self._get_first('title')
        return self._title

    @property
    def name(self):
        return self._name

    def download(self, path=''):
        filename = os.path.join(path, self.name+'.txt')
        logging.info('Download %s'%(filename))
        content = '               %s\n\n' % (self.name)
        content_html = self._get_first('.post_bd')
        content += self._html2text.handle(content_html).replace(u'\n    \n    \n','').replace(u'\r\n',u'\n').replace('&lt;','<').replace('&gt;','>')
        with open(filename, 'w') as f:
            f.write(content.encode('utf-8'))
        return True

def main():
    base_url = 'http://man.linuxde.net/par/'
    for i in '12345':
        inds = index(base_url,i)
        for ind in inds.nexts:
            for page in ind.pages:
                time.sleep(0.1)
                page.download()

if __name__=='__main__':
    main()
