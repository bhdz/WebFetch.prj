
import grp
import signal
import daemon
import lockfile

import os
import copy
import threading
import requests

from urllib.parse import urlparse
import queue

from fsutils import Fs, Action, Exists, Make, MakeDirs, View
from fetcher import Fetcher, Resource, Identify, Config
from client import Client

# Hahahahha
# THREE QUEES, THREE Additional Classes (UnknownResource >> Resource >> Page or File or ?)
# One Level For Unknown Resources
# One Level for Identified Resources
# The Last Level for Either Pages & Files or Directories...
# The Three Necked Beast... three is enough... Drako... With three Heads...
# The Three Boxxed Boxes ... The Box &within a Box with a Box with Three Optional Presents choice...
# No, ..., wait ... *yawn*
class Daemon(object):
    """ This is :a ::Structure &that &&Supports {: Daemonisation } &&As Per ::
        :: https://www.python.org/dev/peps/pep-3143/ ::
        :: Please As with `fetcher.py``, use The Functions Provided ::
        self.sources :: is :a &Collection &&Of {: yielding functions } """

    def sources_add(sel, sources_yielder):
        pass

    @property
    def sources(self):
        return self._sources

    @sources.setter
    def sources(self, value):
        self._sources = value

    @property
    def threads(self):
        pass

    @property
    def threads_count(self):
        return len(self.threads)


def eye_Daemon_01():
    def initial_program_setup():
        pass

    def do_main_program():
        pass

    def program_cleanup():
        pass

    def reload_program_config():
        pass

    context_fetcher = {
        'config': Config(fetch_dir=Fs('/home/boril/Desktop/Tests/output/fetch')),
    }

    context = daemon.DaemonContext(
        working_directory=context_fetcher['config']['fetch_dir'],
        umask=0o002,
        pidfile=lockfile.FileLock('/var/run/spam.pid'),
        )

    context.signal_map = {
        signal.SIGTERM: program_cleanup,
        signal.SIGHUP: 'terminate',
        signal.SIGUSR1: reload_program_config,
        }

    def _step0():
        mail_gid = grp.getgrnam('mail').gr_gid
        context.gid = mail_gid

        important_file = open('spam.data', 'w')
        interesting_file = open('eggs.data', 'w')
        context.files_preserve = [important_file, interesting_file]

    _step0()
    initial_program_setup()

    with context:
        do_main_program()
################################################################################
def source():
    yield 'http://random.org/'


input = Fs('/home/boril/Desktop/Tests/input')   # Let the DAEMON occupy this directory
output = Fs('/home/boril/Desktop/Tests/output') # Let the DAEMON occupy this output directory

fetch_dir = str(output + 'fetched')
archive_dir = str(output + 'archive')

for path in View(input).listing():
    content = []
    with open(str(path), 'r') as f:
        content = [ line.strip() for line in f.readlines() if len(line.strip()) > 0 ]

#
#: Triok Zwer. s Tri Opashleta ahahahah kak da stane ya... Triabwa da se pulniat edno po edno da ima propagation na :eve? no.
#
#: Trqq za Vseki Zwer, po edin Vid Client.py (klasse), 4 threads per Zwer = 12 threads (4*3 == pochti 4*4 = 16; Zwer3 << Quatro)
#
q_files = queue.Queue()
q_pages = queue.Queue()
q_uris = queue.Queue()

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

def new_web_resource(uri, client, result):
    print('new unidentified? Resource? uri:', uri)
    print('client? Client? client:', client)
    print('result? Result? result:', result)
    return False

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

def new_uri(uri, client, result):
    pass

def error_callback(err):
    pass

from worldsex_com import Worldsex

def worker1_pages():
    while True:
        uri = q_pages.get()
        if uri is None: break

        worldsex.begin(uri, new_uri)
        q_pages.task_done()

print("starting: page workers")

num_pageworker_threads = 4
threads = []

for i in range(num_pageworker_threads):
    t = threading.Thread(target=worker1_pages)
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
