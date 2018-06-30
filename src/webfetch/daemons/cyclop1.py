import threading
import requests
import copy
import os
from urllib.parse import urlparse
import queue
import time
import os
import grp
import signal
import daemon
import lockfile

from webfetch.fsutils import Fs, Action, Exists, Make, MakeDirs, View
from webfetch.fetcher import Config, Resource, Fetcher, download, fetch, snapshot, forget, clear_resources
from webfetch.client import Client, ValidClient
from webfetch.parser import Parser, AnchorParser, ImgParser

class Daemon(object):
    """ This Borg holds all the necessary information for the cyclop1 daemon"""
    _props = {
        'uris_queue' : queue.Queue(),
        'context_fetcher': {
            'config': Config({}),
        },
        # Please, Set me up in your initial_program_setup
        'context': daemon.DaemonContext(
            working_directory=None,
            umask=0o002,
            pidfile=None, #lockfile.FileLock
        ),
        'worker_count': 4,
        'worker_threads': None,
        'input_thread': None,
        'quit' : False,
        'client': None,
    }
    def __init__(self):
        self.__dict__ = Daemon._props

    @property
    def config(self):
        return self.context_fetcher['config']


uri_visited = set()
def visited_uri(uri):
    global uri_visited
    if uri in uri_visited:
        return True
    else:
        uri_visited.add(uri)
        return False


def new_uri(uri, client, result):
    cyclop1 = Daemon()
    q = cyclop1.q_uris

    print('new_uri:', uri)

    if isinstance(result, Resource):
        pass # print('Resource?', result.path)
    elif isinstance(result, dict):
        for uri_img in result['img']:
            if False == visited_uri(uri_img):
                q.put(uri_img)

        for uri_a in result['a']:
            if False == visited_uri(uri_a):
                q.put(uri_a)


def worker():
    name = str(threading.get_ident())
    print("worker / %s: begin" % name)
    cyclop1 = Daemon()

    while True:
        uri = cyclop1.q_uris.get()

        if uri is None:
            print("worker / %s: recieved None!" % name)
            break

        cyclop1.client.begin(uri, new_uri)
        cyclop1.q_uris.task_done()
    print("worker / %s: end" % name)

def input_worker():
    print("input_worker: begin")
    cyclop1 = Daemon()

    cyclop1.quit = False

    while not cyclop1.quit:
        print("input_worker: cycle")
        for fs in View(cyclop1.config['input_dir']).listing():
            print("input_worker: fs:", str(fs))
            with open(str(fs), 'r') as f:

                lines = [ line.strip() for line in f.readlines() if len(line.strip()) > 0 ]
                print("lines:", lines)
                for line in lines:
                    print('url:', line)
                    cyclop1.q_uris.put(line)
            Make(str(fs)).remove()

        # Check the command file for commands and if there are
        #  present, get them, and truncate it.

        process_cmds = Fs(cyclop1.config['control_dir']) + 'process.cmd'
        with open(str(process_cmds), 'r') as cmd_f:
            print("input_worker: reading process.cmd")
            commands = [ str(cmd).strip() for cmd in cmd_f.readlines() if len(cmd.strip()) > 0 ]
            print("input_worker: commands:", commands)

            for command in commands:
                if command == ":quit":
                    cyclop1.quit = True
                elif command == ":report":
                    print("reporting!")
                elif command == ":":
                    pass

        if not cyclop1.quit:
            time.sleep(3)
            print("input_worker: slept! 3; secs")

    print("input_worker: Ending")
    cyclop1.q_uris.join()

    # stop workers
    for i in range(cyclop1.worker_count):
        cyclop1.q_uris.put(None)

    for t in cyclop1.worker_threads:
        t.join()
    print("input_worker: end")

def do_main_program():
    print("do_main_program: begin")
    print("do_main_program: end")


def program_cleanup():
    print("program_cleanup: begin")
    # block until all tasks are done
    cyclop1 = Daemon()
    cyclop1.q_uris.join()

    # stop workers
    for i in range(cyclop1.worker_count):
        cyclop1.q_uris.put(None)

    for t in cyclop1.worker_threads:
        t.join()

    # wait for input_thread
    cyclop1.input_thread.join()
    print("program_cleanup: end")

def initial_program_setup():
    config_file = Fs('/home/boril/Desktop/Tests/webfetch/config.json')
    cyclop1 = Daemon()

    cyclop1.q_uris = queue.Queue()
    cyclop1.context_fetcher['config'] = Config()
    cyclop1.config.load_json(config_file)
    process_cmd = Fs(cyclop1.config['control_dir']) + 'process.cmd'
    print("process_cmd:", process_cmd)
    Make(process_cmd).touch(exist_ok=True)
    print(View(process_cmd).exists())

    cyclop1.context = daemon.DaemonContext(
        working_directory=cyclop1.context_fetcher['config']['input_dir'],
        umask=0o002,
        pidfile=lockfile.FileLock('/var/run/webfetch_daemon_cyclop1.pid'),
        )

    cyclop1.signal_map = {
        signal.SIGTERM: program_cleanup,
        signal.SIGHUP: 'terminate',
        signal.SIGUSR1: reload_program_config,
        }

    parser_a = AnchorParser()
    parser_img = ImgParser()
    #parser_script = ScriptParser()
    parser = Parser(parser_a, parser_img)
    fetcher = Fetcher(cyclop1.config)
    cyclop1.client = Client(fetcher, parser)

    print("starting: input_thread")
    cyclop1.input_thread = threading.Thread(target=input_worker)
    cyclop1.input_thread.start()

    print("starting: workers")

    cyclop1.worker_count = 4
    cyclop1.worker_threads = []

    for i in range(cyclop1.worker_count+1):
        t = threading.Thread(target=worker)
        cyclop1.worker_threads.append(t)
        t.start()

    print("initial_program_setup: bye")


def reload_program_config():
    print("reload_program_config: hello")
    print("reload_program_config: bye")


def _step0():
    cyclop1 = Daemon()
    #mail_gid = grp.getgrnam('mail').gr_gid
    #cyclop1.context.gid = mail_gid

    #important_file = open('spam.data', 'w')
    #interesting_file = open('eggs.data', 'w')
    #cyclop1.context.files_preserve = [important_file, interesting_file]

_step0()
initial_program_setup()

with Daemon().context:
    do_main_program()
