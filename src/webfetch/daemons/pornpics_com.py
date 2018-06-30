import threading
import requests
import copy
import os
from urllib.parse import urlparse
import queue

from webfetch.fetcher import *
from webfetch.fsutils import Fs, Action, Exists, Make, MakeDirs, View
from webfetch.parser import *


q = queue.Queue()


class MirrorOnlySite(Client):
    def __init__(self, except_url):
        self.except_url = except_url

    def valid_url(self, url):
        if 'image/gif;base64' in str(url):
            return False

        parsed = urlparse(url)
        full = parsed.netloc + parsed.path

        server_name = full.split("/")[0].split(".")[-1: -3: -1]

        if len(server_name) > 1:
            if server_name[1] == self.except_url:
                return True
        return False


_input = Fs('/home/boril/Desktop/Tests/input')
output = Fs('/home/boril/Desktop/Tests/output')
fetch_dir = str(output + 'fetched')
archive_dir = str(output + 'archive')

config = Config(fetch_dir=fetch_dir,
                archive_dir=archive_dir,
                chunk_size=4096)

uris_visited = set()


class AnchorParser2(AnchorParser):
    def parse(self, soup):
        return super(AnchorParser2, self).parse(soup)
        anchors_list = parsed.get('a', {})
        filtered_anchors = []
        for anchor in anchors_list:
            if not (len(anchor.split(";")) >= 2):
                filtered_anchors.append(anchor)

        for anchor in filtered_anchors:
            parsed['a'].remove(anchor)

        return parsed


def sources():
    # yield 'https://www.iana.org/domains/reserved'
    # yield 'http://example.com/'
    # yield 'https://i.imgur.com/ItxPkKe.jpg'
    for filename in View(_input).listing():
        with open(str(filename), 'r') as fio:
            lines = [line.strip() for line in fio.readlines() if len(line.strip()) > 0]
            for line in lines:
                yield line


parser_a = AnchorParser2()
parser_img = ImgParser()
parser_script = ScriptParser()
parser = Parser(parser_a, parser_img, parser_script)

fetcher = Fetcher(config)
client = Pornpic(fetcher, parser)


def check_uri(uri):
    if 'image/gif' in str(uri):
        return False
    if uri in uris_visited:
        return False

    uris_visited.add(uri)
    return True


def new_uri(uri, result, client=Client()):
    if isinstance(result, Resource):
        print('new_uri:', uri)
        print("resource.path:", result.path)

    else:
        print('new_uri:', uri)
        for uri_img in result['img']:
            if True is check_uri(uri_img):
                q.put(uri_img)

        for url_a in result['a']:
            if True is check_uri(url_a):
                q.put(url_a)

        for script in result['script']:
            pass #print('new_page? script:', script)


def worker_uri():
    while True:
        uri = q.get()
        q.task_done()

        if uri is None:
            print("thread -> task: `done")
            break
        client.begin(uri, new_uri, client)
    print("thread -> shutdown:")


print("starting: workers")

num_worker_threads = 8
threads = []

for i in range(num_worker_threads):
    t = threading.Thread(target=worker_uri)
    t.start()
    threads.append(t)


def input_watch():
    while True:
        x = input("")
        if x == 'q':
            print("QUITTING!")
            break

    for n in range(num_worker_threads):
        q.put(None)


ti = threading.Thread(target=input_watch)
ti.start()

for url in sources():
    q.put(url)


q.join()
ti.join()
# block until all tasks are done
for thread in threads:
    thread.join()


