import threading
import requests
import copy
import os
from urllib.parse import urlparse
import queue

from fetcher import *
from fsutils import Fs, Action, Exists, Make, MakeDirs, View
from parser import *
""" BASIC BITCH BOT; TWO BUCKETS OF :SHIT FOR ::SHOVELIN' {{ HAHA! LOL }}
    I suck :at{Multithreading} but I do understand Forks()"""


def source():
    pass


input = Fs('/home/boril/Desktop/Tests/input')
output = Fs('/home/boril/Desktop/Tests/output')
fetch_dir = str(output + 'fetched')
archive_dir = str(output + 'archive')

q_pages = queue.Queue()
q_files = queue.Queue()

def error_callback(err):
    pass

#from worldsex_com import Worldsex

class Pornpic(Client):
    def valid_url(self, url):
        parsed = urlparse(url)
        full = parsed.netloc + parsed.path

        server_name = full.split("/")[0].split(".")[-1: -3: -1]

        #print('valid_url? server_name:', server_name)
        if server_name[0] == "com":
            if len(server_name) > 1:
                if server_name[1] == "pornpics":
                    return True
        return False

config = Config(fetch_dir=fetch_dir,
                archive_dir=archive_dir,
                chunk_size=4096)

uris_visited = set()


parser_a = AnchorParser()
parser_img = ImgParser()
parser_script = ScriptParser()
parser = Parser(parser_a, parser_img, parser_script)

fetcher = Fetcher(config)
client = Pornpic(fetcher, parser)


def check_uri(uri):
    if uri in uris_visited:
        return False
    uris_visited.add(uri)
    return True

def new_image(uri, client, result):
    print('new_image:', uri)

def new_page(uri, client, result):
    print('new_page:', uri)

    #print('type(result):', type(result))
    if isinstance(result, Resource):
        print('new_page? result is Resource')
    else:
        for uri_img in result['img']:
            if False == check_uri(uri_img):
                print('new_page? uri? already fetched:', uri_img)
                return False
            #q.put(url_img)
            #ret = worldsex.begin(uri_img, new_image)
            q_files.put(uri_img)
            #success = worldsex.begin(img, new_image)

        for url_a in result['a']:
            q_pages.put(url_a)

        for script in result['script']:
            print('new_page? script:', script)


def worker_pages():
    while True:
        uri = q_pages.get()
        if uri is None: break

        client.begin(uri, new_page)
        q_pages.task_done()

print("starting: page workers")

num_pageworker_threads = 4
threads = []

for i in range(num_pageworker_threads):
    t = threading.Thread(target=worker_pages)
    t.start()
    threads.append(t)

for url in source():
    q_pages.put(url)

def worker_files():
    while True:
        uri = q_files.get()
        if uri is None: break

        client.begin(uri, new_image)
        q_files.task_done()

print('starting: image workers')
num_fileworker_threads = 4
threads_file = []
for i in range(num_fileworker_threads):
    t = threading.Thread(target=worker_files)
    t.start()
    threads_file.append(t)
# block until all tasks are done
q_pages.join()
q_files.join()

"""

# stop workers
for i in range(num_pageworker_threads):
    q_pages.put(None)
for t in threads:
    t.join()

for i in range(num_fileworker_threads):
    q_files.put(None)
for t in threads_file:
    t.join()


for i in range(num_pageworker_threads):
    q_pages.put(None)

for thread in threads:
    thread.join()

for thread_file in threads_file:
    thread_file.join()
"""
