import requests
import copy
import os
from urllib.parse import urlparse
import queue
from bs4 import BeautifulSoup

from fetcher import *
from fsutils import Fs, Action, Exists, Make, MakeDirs, View
from client import Client


class Parser(object):
    def __init__(self, *sub_parsers):
        self.parsers = []
        for parser in sub_parsers:
            self.parsers.append(parser)
        self.updated_content = None
        self.fetched = None

    def add_subparser(self, sub_parser):
        self.parsers.append(sub_parser)

    def parse(self, soup):
        result = {}
        for parser in self.parsers:
            parser.fetched = self.fetched
            parser_result = parser.parse(soup)
            for key in parser_result:
                result[key] = parser_result[key]
        self.updated_content = soup.prettify('utf-8')
        return result


class AnchorParser(Parser):
    def parse(self, soup):
        parsed = {
            'a' : [],
        }
        for a in soup.find_all('a', href=True):
            link = a.attrs['href']
            try:
                link_parsed = urlparse(link)

                fetched_server = str(self.fetched.parsed_uri.netloc).split('.')[-1::-1]
                link_server = str(link_parsed.netloc).split('.')[-1::-1]

                #if fetched_server[0:2] == link_server[0:2]:
                parsed['a'].append(link)

                fullpath = link_parsed.netloc + link_parsed.path
                if fullpath[0] == os.path.sep:
                    fullpath = self.fetched.origin_dir + fullpath

                # Correct the href in the anchor
                a.attrs['href'] = 'file://' + fullpath
                a.attrs['href'] = os.path.join(a.attrs['href'], str(self.fetched.filename))
            except ValueError:
                error = True
        return parsed

class ImgParser(Parser):

    def parse(self, soup):
        parsed = {
            'img' : [],
        }
        # Trawl all img tags
        for img in soup.find_all('img', src=True):
            link = img.attrs['src']
            try:
                link_parsed = urlparse(link)

                fetched_server = str(self.fetched.parsed_uri.netloc).split('.')[-1::-1]
                link_server = str(link_parsed.netloc).split('.')[-1::-1]

                #if fetched_server[0:2] == link_server[0:2]:
                # To download the image
                parsed['img'].append(link)

                fullpath = link_parsed.netloc + link_parsed.path
                if fullpath[0] == os.path.sep:
                    fullpath = self.fetched.origin_dir + fullpath

                # Correct the HTML
                img.attrs['src'] = 'file://' + fullpath
                    #img.attrs['src'] = os.path.join(img.attrs['src'], fetched.filename)
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
