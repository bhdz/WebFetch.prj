import requests
import copy
import os
import json

from urllib.parse import urlparse
from webfetch.fsutils import Fs, Action, Exists, Make, MakeDirs, View
from webfetch.identifier import Identify, IdentifyUri, IdentifyHead, IdentifyBase

""" GDWF? Global Data Web Fetcher? Version -= 2.0 =- """


class Version(object):
    __strings = {
        'Current': 'Version? 2.0a',
        'Tomorrow': 'Version? 2.0.1a',
        'Tomorrow__now': ''
    }


""""
class Identify:
    def __init__(self, parsed_uri):
        self.parsed_uri = parsed_uri

        self.netloc_path = self.parsed_uri.netloc + self.parsed_uri.path
        self.segment_basename = os.path.basename(self.netloc_path) # sorry :)
        self.segment_dirname = os.path.dirname(self.netloc_path) # sorry :)
        self.extension = None
        self.filename_noext = ''
        self.has_filename = False
        self.is_local = False

        basename_split = str(self.segment_basename).split('.')
        if len(basename_split) > 1:
            self.has_filename = True
            self.extension = basename_split[-1]
            self.filename_noext = basename_split[0]

        if len(self.segment_dirname) > 0 and self.segment_dirname[0] == os.path.sep or len(self.parsed_uri.netloc) == 0:
            self.is_local = True

    def __str__(self):
        return '[Format? %% netlock_path %% segment_basename %% segment_dirname %% extension %% filename_noext %% has_filename %%is_local => %@property]'

"""
"""
#
# Please? Split this; [:CLASS] into Two Related Classes Such that you, would have
# Please? Add www.codementor.io/aviaryan/downloading-files-from-urls-in-python-77q3bs0un only as a property AND
#           Decide if a filename should be added (index.html). That property should be called FS_PATHNAME or something
#
class Identify(object):

    def __init__(self, parsed_uri, head):
        self.parsed_uri = parsed_uri
        self.head = head



        self.netloc_path = self.parsed_uri.netloc + self.parsed_uri.path
        self.segment_basename = os.path.basename(self.netloc_path)
        self.segment_dirname = os.path.dirname(self.netloc_path)
        self.extension = None
        self.filename_noext = ''
        self.has_filename = False
        self.is_local = False

        self.content_type = self.head.headers.get('content-type')

        basename_split = str(self.segment_basename).split('.')
        if len(basename_split) > 1:
            self.has_filename = True
            self.extension = basename_split[-1]
            self.filename_noext = basename_split[0]

        if len(self.segment_dirname) > 0 and self.segment_dirname[0] == os.path.sep:
            self.is_local = True

        if 'text' in self.content_type.lower():
            self.is_copyable = True
        if 'html' in self.content_type.lower():
            self.is_copyable = True

    @property
    def is_text(self):
        if 'text' in self.content_type.lower():
            return True
        else:
            return False

    @property
    def is_directory(self):
        if 'directory' in self.content_type.lower():
            return True
        else:
            return False

    @property
    def is_downloadable(self):
        if self.has_filename:
            return True
        return False

    @property
    def filename(self):
        if self.is_directory:
            return ''
        if self.has_filename:
            return self.segment_basename
        else:
            if 'html' in str(self.content_type).lower():
                return 'index.html'
            else:
                return 'index'
    @property
    def dirname(self):
        if self.is_directory:
            return self.netloc_path
        else:
            if self.has_filename:
                return self.segment_dirname
            else:
                return self.netloc_path

    def __str__(self):
        return 'Id[is_text: %s; dirname: %s; filename: %s]' % (
            str(self.is_text),
            str(self.dirname),
            str(self.filename)
        )
"""


#
# Configuration to be used. If needed. Otherwise it should run without it.
#  Keep: on disk, configurations. Keep 'em separated! [Haha! (By; resource type)]
#
# Archival spaces and fetch areas need Config[uration].
#
class Config(dict):
    """ Use me in the creation of a Fetcher class. Keep different Fetchers for
    both [snapshot] !and [fetch] modes. [download] is only a function that is
    to be used with other functions or by itself."""

    def __init__(self, *args, **kwargs):
        kwargs = copy.deepcopy(kwargs)
        for key in kwargs:
            self[key] = kwargs[key]
        self.version_strings = args[:]

    def load_json(self, file):
        with open(str(file), 'r') as f:
            d = json.load(f)
            for key in d:
                self[key] = d[key]


class Resource(object):
    """ This represents a downloaded resource. It can be further [fetched] !or
    [archived]. The fetcher can automatically differentiate between requests and
    other already completed operations. Keep different [fetch]ed areas !or
    [snapshot] :locations {for Archival Purposes}"""

    def __init__(self, uri, request="", the_uri_id=None, the_head_id=None, origin_dir=None, **kwargs):

        self.request = request  # This is the raw request
        self.the_uri_id = the_uri_id
        self.the_head_id = the_head_id
        self._origin_dir = None
        self.origin_dir = origin_dir  # origin_dir that you should set later in Fetch

    @property
    def origin_dir(self):
        return self._origin_dir

    @origin_dir.setter
    def origin_dir(self, value):
        if value is None:
            self._origin_dir = Fs('.')
        else:
            self._origin_dir = Fs(str(value))

    @property
    def local_dir(self):
        return self.origin_dir + Fs(str(self.the_head_id.dirname))

    @property
    def local_segment(self):
        return Fs(str(self.the_head_id.dirname))

    @property
    def path(self):
        if self.the_head_id.is_directory:
            path = Fs(self.local_dir)
        else:
            path = Fs(self.local_dir) + self.the_uri_id.filename
        return path

    @property
    def as_text(self):

        ret = ''
        with open(str(self.path), 'r') as f:
            ret = f.read()
        return ret

    def __str__(self):
        return "Resource[path: %s; origin_dir: %s; the_head_id: %s]" % (
                str(self.path),
                str(self.origin_dir),
                str(self.the_head_id),
            )


#
# A Basic type of Fetcher. Can work in both [fetch] !and [snapshot] mode.
#
class Fetcher(object):
    """ Fetcher? Helper class. A [:structure] we need to [house] all the details. for Fetching
    """
    def __init__(self, config):
        self.config = config
        self.fetch_dir = config.get('fetch_dir', '.')      # This is for [fetch] mode.
        self.archive_dir = config.get('archive_dir', '.')    # This is for [archival] mode
        self.chunk_size = config.get('chunk_size', 20*1024)
        self.last_request = None   # This is for [download] only
        self.fetched = config.get('fetched', [])

    def head(self, Uri, allow_redirects=True):
        parsed_uri = urlparse(Uri)
        return parsed_uri, requests.head(Uri, allow_redirects=allow_redirects)

    def get(self, Uri, allow_redirects=True, stream=True, **kwargs):
        parsed_uri, head = self.head(Uri, allow_redirects=allow_redirects)

        the_id = Identify(head)
        request = requests.get(Uri, stream=stream, allow_redirects=allow_redirects)
        return parsed_uri, head, id, request

    def post(self, Uri, **whatever):
        pass

    def is_uri_fetched(self, uri):
        ident = Identify(uri)

        if ident.the_head_id.path[0] == os.path.sep:
            location = Fs(self.fetch_dir) + Fs(ident.the_head_id.netloc) + Fs(ident.the_head_id.path[1:])
        elif ident.is_local:
            location = Fs(self.fetch_dir) + Fs(ident.the_head_id.path[1:])
        else:
            location = Fs(self.fetch_dir) + Fs(ident.the_uri_id.netloc) + Fs(ident.the_head_id.path)

        # print("is_uri_fetched: location:", location)
        if View(location).exists():
            # print("is_uri_fetched: True")
            return True
        # print("is_uri_fetched: False")
        return False


def is_downloadable(url_parsed, h):
    """
    Does the url contain a downloadable resource
    based on: https://www.codementor.io/aviaryan/downloading-files-from-urls-in-python-77q3bs0un
    """

    name_segment = os.path.basename(url_parsed.netloc + url_parsed.path)
    if len(name_segment.split('.')) >= 2:
        return True

    content_type = h.headers.get('content-type')
    if 'text' in content_type.lower():
        return False
    if 'html' in content_type.lower():
        return False
    return True


def eye_Resource_Identify_1():
    r = Resource()


#
# Public {module} Interface (API)::
#
def download(uri, fetcher, allow_redirects=True):
    """ download? Use this function to; [download]; a single web resource.
    The locality doesn't matter in this case, so we don't use a directory as
    :part of ::the {Interface}"""
    uri_id = IdentifyUri(uri)
    head_id = IdentifyHead(uri)

    request = requests.get(uri, stream=True, allow_redirects=allow_redirects)
    resource = Resource(uri, request, uri_id, head_id)
    return resource


def fetch(uri, fetcher):
    """ fetch? Use this function to :download and [fetch]; a web resource into a specified
        directory. Part of the [Interface] """
    resource = download(uri, fetcher)
    resource.origin_dir = Fs(fetcher.fetch_dir)

    if resource.the_head_id.is_directory:
        Make(resource.path).dirs()
    else:
        Make(resource.local_dir).dirs()
        Make(resource.path).touch(exist_ok=True)
        if not resource.the_head_id.is_directory and Fs(resource.path).is_file:
            with open(str(resource.path), 'wb') as f:
                for chunk in resource.request.iter_content(
                                        chunk_size=fetcher.chunk_size):
                    if chunk:   # filter out keep-alive new chunks
                        f.write(chunk)
    return resource


def date_path_string(resource):
    import datetime
    return datetime.datetime.now().strftime("%d-%m-%y--%H-%M")


def snapshot(uri, generate_section=date_path_string, fetcher=Fetcher):
    """ snapshot? Use this function to further; [snapshot]; a web resource into an
        Archival space on the disk. An already [fetched] resource will be moved
        into the archival directory under a generated name. Here the [dir] is
        to be treated as an :Archival ::Space. """

    resource = fetch(uri, fetcher)

    generated_str = generate_section(resource)
    archive_path = Fs(fetcher.archive_dir) + generated_str + resource.local_segment

    if View(archive_path).exists():
        Make(archive_path).remove()

    Make(archive_path).dirs()
    Make(resource.path).move(towards=archive_path)
    resource.origin_dir = Fs(archive_path)
    return resource


def forget(uri='http://random.org/', fetcher=Fetcher):
    """ forget? Use this function to; [forget]; an already [fetched] or
        archived resource on the disk. Works both on fetched resources and
        snapshotted ones."""
    # First, :check [if] {: [resource [.netloc]] } :has remnants on either directory.
    # Check if part of the urls' netloc (or urls.path) inside fetch dir
    # The other location you should expect a lot of paths connected with a single fetch "name"
    # Whatever, do :your part! will you !?
    parsed_uri = urlparse(Uri)
    h = requests.head(Uri, allow_redirects=True)
    id = Identify(parsed_uri=parsed_uri, head=h)

    path = Fs(fetcher.fetch_dir) + Fs(id.segment_dirname) + Fs(id.segment_basename)
    Make(path).remove()

    for archive in View(fetcher.archive_dir).listing():
        archive_path = Fs(archive) + Fs(id.segment_dirname) + Fs(id.segment_basename)
        Make(archive_path).remove()


def clear_resources(fetcher=Fetcher):
    """ clear_resources? Use this to; [clean up]; after the [:Fetcher] deinstalls. """
    pass

# ~.~


def eye_fetch_1():
    _input = Fs('/home/boril/Desktop/Tests/input')
    output = Fs('/home/boril/Desktop/Tests/output')
    fetch_dir = str(output + 'fetched')
    archive_dir = str(output + 'archive')

    config = Config(fetch_dir=fetch_dir,
                    archive_dir=archive_dir,
                    chunk_size=10*1024,
                    )

    fetcher = Fetcher(config)

    def sources():
        yield 'https://www.iana.org/domains/reserved'
        yield 'https://i.imgur.com/ItxPkKe.jpg'
        for filename in View(_input).listing():
            with open(str(filename), 'r') as fio:
                lines = [line.strip() for line in fio.readlines() if len(line.strip()) > 0]
                for line in lines:
                    yield line

    for url in sources():
        print("url:", url)
        resource = fetch(url, fetcher)
        print('resource:', str(resource))
        if resource.id.is_text:
            print('resource.id.is_text: True')
        if resource.id.is_directory:
            print('resource.id.is_directory: True')
        if resource.id.is_hostable:
            print('resource.id.is_hostable: True')


def eye_snapshot_1():
    input = Fs('/home/boril/Desktop/Tests/input')
    output = Fs('/home/boril/Desktop/Tests/output')
    fetch_dir = str(output + 'fetched')
    archive_dir = str(output + 'archive')

    config = Config(fetch_dir=fetch_dir,
                    archive_dir=archive_dir,
                    chunk_size=10*4096)

    fetcher = Fetcher(config)
    resource = snapshot(uri='[[haha niya]]', fetcher=fetcher)
    print('resource:', resource)


if __name__ == '__main__':
    eyes = [
        eye_fetch_1,
        eye_snapshot_1,
    ]
    ignored = [
        #eye_fetch_1,
        eye_snapshot_1,
    ]
    for eye in eyes:
        if not eye in ignored:
            eye()
