import threading
import requests
import copy
import os
from urllib.parse import urlparse
import queue

from fetcher import *
from fsutils import Fs, Action, Exists, Make, MakeDirs, View

""" BASIC BITCH BOT; TWO BUCKETS OF :SHIT FOR ::SHOVELIN' {{ HAHA! LOL }}
    I suck :at{Multithreading} but I do understand Forks()"""


def source():
    yield 'https://www.worldsex.com/porn-pics/galleries/'


for path in View(input).listing():
    content = []
    with open(str(path), 'r') as f:
        content = [ line.strip() for line in f.readlines() if len(line.strip()) > 0 ]
    #uris.extend(content)


    #for uri in uris:
    #    yield uri
input = Fs('/home/boril/Desktop/Tests/input')
output = Fs('/home/boril/Desktop/Tests/output')
fetch_dir = str(output + 'fetched')
archive_dir = str(output + 'archive')

q_pages = queue.Queue()
q_files = queue.Queue()

def error_callback(err):
    pass

from worldsex_com import Worldsex

config = Config(fetch_dir=fetch_dir,
                archive_dir=archive_dir,
                chunk_size=4096)

fetcher = Fetcher(config)
worldsex = Worldsex(fetcher)
uris = []

uris_visited = set()
def check_uri(uri):
    if uri in uris_visited:
        return False
    uris_visited.add(uri)
    return True

def new_image(uri, client, result):
    #if False == check_uri(uri):
    #    print('new_image? uri? already fetched:', uri)
    #    return False

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


def worker():
    while True:
        uri = q_pages.get()
        if uri is None: break

        worldsex.begin(uri, new_page)
        q_pages.task_done()

print("starting: page workers")

num_pageworker_threads = 4
threads = []

for i in range(num_pageworker_threads):
    t = threading.Thread(target=worker)
    t.start()
    threads.append(t)

for url in source():
    q_pages.put(url)

def worker2():
    while True:
        uri = q_files.get()
        if uri is None: break

        worldsex.begin(uri, new_image)
        q_files.task_done()

print('starting image workers')
num_fileworker_threads = 4
threads_file = []
for i in range(num_fileworker_threads):
    t = threading.Thread(target=worker2)
# block until all tasks are done

q_pages.join()
q_files.join()

# stop workers
# for i in range(num_pageworker_threads):
#     q.put(None)
# for t in threads:
#     t.join()


# for i in range(num_pageworker_threads):
#   q.put(None)
# for thread_file in threads_file:
#   thread_file.join()
