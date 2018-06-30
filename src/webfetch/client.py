import requests
import copy
import os
from urllib.parse import urlparse
import queue
from bs4 import BeautifulSoup

from webfetch.fetcher import *
from webfetch.fsutils import Fs, Action, Exists, Make, MakeDirs, View
from webfetch.parser import *


def validate_url(url, *resources):
    try:
        parsed = urlparse(url)
        full = parsed.netloc + parsed.path
        if full[0:2] == "//":
            return False
        return True
    except:
        return False


class Process(object):
    def __init__(self, fetched):
        self.fetched = fetched


class ProcessFile(Process):
    pass


class ProcessDir(Process):
    pass


class ProcessPage(Process):
    pass


class Client(object):
    """ Use? This; Client; in case of {{ You want to parse some result }} """
    def __init__(self, fetcher, page_parser, error_callback=None, error_propagate=False, check_existing=False):
        self.fetcher = fetcher
        self.error_callback = error_callback
        self.error_propagate = True
        self.page_parser = page_parser
        self.page_parser.fetched = None
        self.processors = {}
        self.check_existing = check_existing

    def process_page(self, fio, fetched):
        """ Standard processing of the resulting page """
        self.page_parser.fetched = fetched

        content = fio.read()
        soup = BeautifulSoup(content, 'html.parser')

        parsed = self.page_parser.parse(soup)

        if self.page_parser.updated_content:
            with open(str(fetched.path), 'wb') as fo:
                fo.write(self.page_parser.updated_content)

        return parsed

    def process_file(self, fio, fetched):
        """ Standard processing of the resulting file """
        self.page_parser.fetched = fetched
        return fetched

    def process_resource(self, fi_resource, fetched_resource):
        """ This is a :General {Function} &that You know nothing about in the
            Beginning """
        self.page_parser.fetched = fetched_resource

    def process(self, fetched):
        if not fetched.id.is_directory and Fs(fetched.path).is_file:
            if fetched.id.is_text:
                with open(str(fetched.path), 'br+') as fio:
                    result = self.process_page(fio, fetched)
            else:
                with open(str(fetched.path), 'br+') as fio:
                    result = self.process_file(fio, fetched)
        else:
            result = fetched

        return result

    def pull(self, uri):
        """ Standard pull?er?? method """
        result = None

        try:
            fetched = fetch(uri, self.fetcher)
            result = self.process(fetched)
        except Exception as err:
            self.error(err)

        return result

    def complete(self, uri, callback, result):
        """ Overload this method if you want to change the logic of the completion process. """
        ret = callback(uri, self, result, client=self)
        if ret is False:
            _error_tuple = tuple([str(uri), id(callback), str(result)])
            return self.error(exception=Exception(
                "ERROR: uri? callback? result? uri: %s; (id? callback) = %d; result: %s" % _error_tuple))
        else:
            return True

    def begin(self, uri, callback):
        try:
            if self.check_existing and self.fetcher.is_uri_fetched(uri):
                return True

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
            return self.error_callback(exception)
        else:
            print("SUPER-ERROR? Yes ::", str(exception))
        if self.error_propagate:
            raise exception


def eye_Client_01():
    _input = Fs('/home/boril/Desktop/Tests/input')
    output = Fs('/home/boril/Desktop/Tests/output')

    fetch_dir = str(output + 'fetched')
    archive_dir = str(output + 'archive')

    config = Config(fetch_dir=fetch_dir,
                    archive_dir=archive_dir,
                    chunk_size=10*4096)

    fetcher = Fetcher(config)

    parser_a = AnchorParser()
    parser_img = ImgParser()
    parser_script = ScriptParser()
    parser = Parser(parser_a, parser_img, parser_script)

    client = Client(fetcher, parser)

    def new_uri(uri, client, result):
        print('new_uri:', uri)
        if isinstance(result, Resource):
            pass
        else:
            for uri_img in result['img']:
                print("uri_img:", uri_img)
                client.begin(uri_img, new_uri)

            for uri_a in result['a']:
                print("uri_a:", uri_a)
                client.begin(uri_a, new_uri)

    def sources():
        # yield 'https://www.iana.org/domains/reserved'
        #yield 'http://example.com/'
        yield 'https://i.imgur.com/ItxPkKe.jpg'
        for filename in View(_input).listing():
            with open(str(filename), 'r') as fio:
                lines = [line.strip() for line in fio.readlines() if len(line.strip()) > 0]
                for line in lines:
                    yield line

    for uri in sources():
        client.begin(uri, new_uri)


class ValidClient(Client):
    """ A Valid? Client: ~ is  a class that takes a Functor/function for validation Purposes ~.~ /warning? still thinking the right; :Hierarchy(object); Version 3.0 Is gewd... hehe Fuck you 2.7sz"""
    def __init__(self, *args, **kwargs):
        args2 = args
        validator_func = None
        if len(args) > 0:
            validator_func = args[0]
            args2 = args[1:-1]
        self.validator_func = validator_func

        super(ValidClient, self).__init__(*args2, **kwargs)

    def valid_url(self, url):
        if self.validator_func:
            return self.validator_func(url)
        else:
            return validate_url(url)


class UnknownResourceClient(Client):
    """ This is needed So that Each New Resource is wrapped inside of It...
    Sorry ? I will rework this section when I know what the hell I am
    talking about ?? """


class KnownResourceClient(ValidClient):
    """ A Known Resource Client simply DECIDES whether a GIVEN RESOURCE is either::
        *&1: A Common URI that Leads to a Directory
        * A Downloadable File, that is NOT Parse-able
        * A Downloadable FILE, that IS Parse-able (Say Html)
        * A Valid URI that LEADS to FILENAME creation for EITHER a FILE or a PAGE or SIMPLY A DIR... Hard...
        """

class PageClient(KnownResourceClient):
    pass

class FileClient(KnownResourceClient):
    pass

class DirClient(KnownResourceClient):
    pass

class OtherResourcesClient(KnownResourceClient):
    """ ? Other ?? is Not NothingClient """

if __name__ == '__main__':
    eyes = [
        eye_Client_01,
    ]
    ignored = [
        # eye_Client_01,
    ]
    for eye in eyes:
        if not eye in ignored:
            eye()
