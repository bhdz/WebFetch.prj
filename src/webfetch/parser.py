import requests
import copy
import os
from urllib.parse import urlparse
import queue
from bs4 import BeautifulSoup

from webfetch.fetcher import *
from webfetch.fsutils import Fs, Action, Exists, Make, MakeDirs, View
from webfetch.client import Client


class Parser(object):
    def __init__(self, *sub_parsers):
        self.parsers = []
        for parser in sub_parsers:
            self.parsers.append(parser)
        self.updated_content = None
        self.fetched = None

    def add_subparser(self, sub_parser):
        self.parsers.append(sub_parser)

    def set_updated_content(self, updated_content):
        self.updated_content = updated_content

    def parse(self, soup):
        result = {}
        for parser in self.parsers:
            parser.fetched = self.fetched
            parser_result = parser.parse(soup)
            for key in parser_result:
                result[key] = parser_result[key]
        self.set_updated_content(soup.prettify('utf-8'))
        return result


class AnchorParser(Parser):
    def parse(self, soup):
        parsed = {
            'a': [],
        }
        for a in soup.find_all('a', href=True):
            link = a.attrs['href']
            try:
                link_id = IdentifyUri(link)
                # Dobre
                aa = self.fetched.the_head_id.parsed_uri.netloc
                ab = link_id.path
                if len(aa) > 0 and aa[-1] == os.path.sep:
                    aa = aa[0:-1]
                if len(ab) > 0 and ab[0] == os.path.sep:
                    ab = ab[1:]

                fullpath = link_id.netloc + link_id.path
                if len(fullpath) > 0 and fullpath[0] == os.path.sep:
                    link = 'http://' + aa + os.path.sep + ab
                elif not ('http' in link):
                    link = 'http://' + aa + os.path.sep + ab
                else:
                    pass
                fullpath = self.fetched.origin_dir + fullpath

                parsed['a'].append(link)
                if not link_id.has_filename:
                    a.attrs['href'] = 'file://' + os.path.join(str(fullpath), 'index.html')
                else:
                    a.attrs['href'] = 'file://' + str(fullpath)

            except ValueError:
                error = True
        return parsed


class ImgParser(Parser):

    def parse(self, soup):
        parsed = {
            'img': [],
        }
        # Trawl all img tags
        for img in soup.find_all('img', src=True):
            link = img.attrs['src']
            try:
                link_parsed = urlparse(link)

                aa = self.fetched.id.parsed_uri.netloc
                ab = link_parsed.path
                if len(aa) > 0 and aa[-1] == os.path.sep:
                    aa = aa[0:-1]
                if len(ab) > 0 and ab[0] == os.path.sep:
                    ab = ab[1:]

                fullpath = link_parsed.netloc + link_parsed.path
                if len(fullpath) > 0 and fullpath[0] == os.path.sep:
                    link = 'http://' + aa + os.path.sep + ab
                elif not ('http' in link):
                    link = 'http://' + aa + os.path.sep + ab

                fullpath = self.fetched.origin_dir + fullpath

                parsed['img'].append(link)

                # Correct the HTML
                img.attrs['src'] = 'file://' + str(fullpath)

            except ValueError:
                error = True
        return parsed


class ScriptParser(Parser):

    def parse(self, soup):
        parsed = {
            'script' : [],
        }
        # Trawl all img tags
        for script in soup.find_all('script', src=True):
            #print('parse? script:', script)
            parsed['script'] = script
        return parsed

class BasicParser(Parser):
    def __init__(self, fetched):
        pass

def eye_Parser_01():
    pass


if __name__ == '__main__':
    eyes = [
        eye_Parser_01,
    ]

    ignored = [
        #eye_Parser_01,
    ]

    for eye in eyes:
        if eye not in ignored:
            eye()
