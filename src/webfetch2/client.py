import requests
import copy
import os
from urllib.parse import urlparse
import queue
from bs4 import BeautifulSoup

from fetcher import *
from fsutils import Fs, Action, Exists, Make, MakeDirs, View

class UriValidator(object):
    pass

def validate_url(url, *resources):
    try:
        parsed = urlparse(url)
        full = parsed.netloc + parsed.path
        if full[0:2] == "//":
            return False
        return True
    except:
        return False


class Client(object):
    """ Use? This; Client; in case of {{ You want to parse some result }} """
    def __init__(self, fetcher, page_parser, error_callback=None, error_propagate=False):
        self.fetcher = fetcher
        self.error_callback = error_callback
        self.error_propagate = True
        self.page_parser = page_parser
        self.page_parser.fetched = None

    def process_page(self, fio, fetched):
        """ Standard processing of the resulting file """
        """ Please define This method. you must read {{ finput }} and parse :the {finput}, returning a parsed result (some structure you created with the fetcher).
        If you want you can save the file when using BeautifulSoup. """
        self.page_parser.fetched = fetched

        content = fio.read()
        soup = BeautifulSoup(content, 'html.parser')

        parsed = self.page_parser.parse(soup)

        if self.page_parser.updated_content:
            with open(str(fetched.path), 'wb') as fo:
                fo.write(self.page_parser.updated_content)

        return parsed

    def process_file(self, fio, fetched):
        #print('process_file:', fetched.path)
        """ Standard processing of the resulting file """
        self.page_parser.fetched = fetched
        return fetched

    def process_resource(self, fi_resource, fetched_resource):
        """ This is a :General {Function} &that You know nothing about in the
            Beginning """
        self.page_parser.fetched = fetched_resource

    def pull(self, uri='http://random.org/'):
        """ Standard puller """
        result = None

        try:
            fetched = fetch(uri, self.fetcher)
        except Exception as err:
            self.error(err)

        if not fetched.downloadable_file:
            with open(str(fetched.path), 'br+') as fio:
                result = self.process_page(fio, fetched)
        else:

            with open(str(fetched.path), 'br+') as fio:
                result = self.process_file(fio, fetched)
        return result

    def complete(self, uri, callback, result):
        """ Overload this method if you want to change the logic of the completion process. """
        return callback(uri, self, result)

    def begin(self, uri, callback):
        try:
            if not self.valid_url(uri):
                return False
            result = self.pull(uri)
            return self.complete(uri, callback, result)
        except Exception as err:
            self.error(err)
            return False
        return True

    def valid_url(self, url):
        """ This method should answer whether an URL is a valid one to fetch """
        return True

    def error(self, exception):
        if self.error_callback:
            self.error_callback(exception)
        else:
            print("ERROR:", str(exception))
        if self.error_propagate:
            raise exception

def eye_Client_01():
    pass
