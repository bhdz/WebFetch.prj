from parser import Parser, AnchorParser, ImgParser, ScriptParser
from client import Client

import threading
import requests
import copy
import os
from urllib.parse import urlparse
import queue

from webfetch.fetcher import *
from webfetch.fsutils import Fs, Action, Exists, Make, MakeDirs, View


class WorldsexParser(Parser):
    def __init__(self, fetched):
        #
        sub_parsers = [
            AnchorParser(fetched),
            ImgParser(fetched),
            ScriptParser(fetched),
        ]
        super(WorldsexParser, self).__init__(*sub_parsers)
        self.fetched = fetched


class Worldsex(Client):
    def __init__(self, fetcher):
        super(Worldsex, self).__init__(fetcher)

    def process_page(self, fio, fetched):
        """ Standard processing of the resulting file """
        parser = WorldsexParser(fetched)
        return super(Worldsex, self).process_page(fio, fetched, parser)

    def process_file(self, fio, fetched):
        return super(Worldsex, self).process_file(fio, fetched)

    def valid_url(self, url):
        parsed = urlparse(url)
        full = (parsed.netloc + parsed.path).split("/")[0].split(".") # Well, it is a bit complex but tis niice ah ah fuck fucki fucki 5 dolla aahahahahah I am big in japan pobably dude aikido ukio no fucking spellsz
        full = full[-1::-1]
        if full[0] == 'com' and full[1] == 'worldsex':
            return True
        else:
            pass

        return False


def eye_Worldsex_01():
    def source():
        yield 'https://www.worldsex.com/porn-pics/'

    input = Fs('/home/boril/Desktop/Tests/input')
    output = Fs('/home/boril/Desktop/Tests/output')
    fetch_dir = str(output + 'fetched')
    archive_dir = str(output + 'archive')

    config = Config(fetch_dir=fetch_dir,
                archive_dir=archive_dir,
                chunk_size=4096)

    fetcher = Fetcher(config)
    worldsex = Worldsex(fetcher)

    visited = []

    collected_urls = []
    forbidden_urls = [
    ]

    def new_image(uri, client, result):
        print('new_image:', uri)

    def new_page(uri, client, result):
        for img in result['img']:
            #if img[0:2] == '//':
            #    img = 'http:' + img
            #if not img in collected_urls:
            print('new_page[img]:', img)
            collected_urls.append(img)
            success = worldsex.begin(img, new_image)
            if not success:
                print('unsuccessful:', img)
            else:
                print('success:', img)

        for a in result['a']:
            #if worldsex.valid_page(a):
                #print('new_page[a]:', a)
            collected_urls.append(a)
            success = worldsex.begin(a, new_page)
            if not success:
                print('unsuccessful:', a)
            else:
                print('success:', img)

    for url in source():
        worldsex.begin(url, new_page)

if __name__ == '__main__':
    eyes = [
        eye_Worldsex_01,
    ]
    ignored = [
        eye_Worldsex_01,
    ]

    for eye in eyes:
        if not eye in ignored:
            eye()
