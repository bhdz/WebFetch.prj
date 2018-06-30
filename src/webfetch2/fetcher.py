import requests
import copy
import os

from urllib.parse import urlparse
from fsutils import Fs, Action, Exists, Make, MakeDirs, View

""" GDWF? Global Data Web Fetcher """


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


class Resource(object):
    """ This represents a downloaded resource. It can be further [fetched] !or
    [archived]. The fetcher can automatically differentiate between requests and
    other already completed operations. Keep different [fetch]ed areas !or
    [snapshot] :locations {for Archival Purposes}"""

    def __init__(self, request, head, *args, **kwargs):
        self.request = request
        self.head = head
        self.downloadable_file = False

        #
        # Beware of :The Identity {_Class:object}
        #: Move to LA : {Illegal Substabces -> Nadushwam hahahhaahaha POT :)}
        #

        self.path = None
        self.filename = None
        self.local_dir = None
        self.origin_dir = None
        self.parsed_uri = None

        # :Robin Hood {:Class:object} ->> After :FETCH {BALL ->> It }
        self.locality_id = None

    @property
    def is_text(self):
        """ Represent :the HTTP ::Resource as Text? Yes | No | May be """
        textual = False
        content_type = self.head.headers.get('content-type')
        if 'text' in content_type.lower():
            textual = True
        return textual

    @property
    def as_text(self):
        """ UNFORTUNATELLY? Fetcher and WebFetch? :Extension ::over {:Requests:Py} """
        ret = ''
        with open(str(self.path), 'r') as f:
            ret = f.read()
        return ret

    def __str__(self):
        return "Resource[head: %s; downloadable_file: %s; path: %s; filename: %s; local_dir: %s; origin_dir: %s; parsed_uri: %s]" % (
                self.head,
                self.downloadable_file,
                self.path,
                self.filename,
                self.local_dir,
                self.origin_dir,
                self.parsed_uri,
            )

class UrlDirectoryMatcher(object):
    """ This class should decide if a directory on the disk, MATCHES a given URL
        It is needed so that `forget()` and clear_resource :perhaps would
        work properly. Thank you for your attention.
    """
    pass

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
        self.last_request = None   # This is for [download] only
        self.chunk_size = config.get('chunk_size', 20*1024)

    @property
    def fetched(self):
        return self._fetched

    @fetched.setter
    def fetched(self, values):
        if not '_fetched' in self.__dict__():
            self._fetched = []
        self._fetched.extend(values)

    @property
    def archived(self):
        return self._archived

    @archived.setter
    def archived(self, value):
        self._archived = value


def is_downloadable(url_parsed, h):
    """
    Does the url contain a downloadable resource
    based on: ? Sorry for that I will tell you later ?? Search:<The Google :Sea>
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


class Identify(object):
    """ Note? To-Self? Don't touch it. It's perfection. """
    def __init__(self, url_parsed, head):
        self.content_type = head.headers.get('content-type')
        self.has_filename = False
        self.is_downloadable = False
        self.basename_segment = os.path.basename(url_parsed.netloc + url_parsed.path)
        self.dirname_segment = os.path.dirname(url_parsed.netloc + url_parsed.path)

        if len(self.basename_segment.split('.')) >= 2:
            self.has_filename = True

        if 'text' in self.content_type.lower():
            self.is_downloadable = False
            self.is_copyable = True
        if 'html' in self.content_type.lower():
            self.is_downloadable = False
            self.is_copyable = True
        #
        # more ifs are needed here, but don't touch it, please ...
        # For &instance, :youtube ::videos {: are non-copyable by default }
        #  `fetch()`` doesn't understand [:youtube videos]
        #
#
# Public {module} Interface (API)::
#
def download(Uri, fetcher, allow_redirects=True):
    """ download? Use this function to; [download]; a single web resource.
    The locality doesn't matter in this case, so we don't use a directory as
    :part of ::the {Interface}"""
    parsed_uri = urlparse(Uri)

    h = requests.head(Uri, allow_redirects=True)

    request = requests.get(Uri, stream=True, allow_redirects=allow_redirects)
    resource = Resource(request=request, head=h)
    #
    # Please use the New Identify class to mark a resource as Identified
    # (that is, all the details of the download should be held in that
    #  object class and a resource instance should be marked  by it
    # Further down, the fetch() and the snapshot() functions would use
    # :that instance {For Good}
    #
    resource.parsed_uri = parsed_uri
    resource.downloadable_file = is_downloadable(parsed_uri, h)

    #
    #: Re-Write this section, please.
    #   Use Identify class to Aggregate the Locality Details into It. Thanx!
    #   Let resource.identity Live in it. Do NOT choose Id or id for the :Name
    #   Please, let it be a whole word please, it is IMPORTANT.
    #   DO NOT Change the Name please, IT is IDENTITY of the LINK/URI/URL so the
    #    Name is Chosen Carefully and After A Serious Work and So on...
    #   Be Normal from time to time, please... What do We Want? An interface that speaks for Itself and Less MANNNINNGGGGGъепаГотенЕеМанингМаЩоСтанаТраверсБНалимумаматанезнамбрать.
    if resource.downloadable_file:
        resource.filename = Fs(os.path.basename(parsed_uri.path))
        resource.local_dir =  Fs(os.path.dirname(str(parsed_uri.netloc + parsed_uri.path)))
        resource.origin_dir = Fs(fetcher.fetch_dir)
    else:
        resource.filename = Fs('index.html')
        resource.local_dir =  Fs(parsed_uri.netloc + parsed_uri.path)
        resource.origin_dir = Fs(fetcher.fetch_dir)

    resource.path = Fs(os.path.join(str(resource.origin_dir), str(resource.local_dir),
            str(resource.filename)))

    #print('resource:', resource)
    return resource


def fetch(uri='http://random.org/', fetcher=Fetcher):
    """ fetch? Use this function to :download and [fetch]; a web resource into a specified
        directory. Part of the [Interface] """
    resource = download(uri, fetcher)
    #resource.path = os.path.join(str(fetcher.fetch_dir), str(resource.path))

    Make(os.path.dirname(str(resource.path))).dirs()
    Make(resource.path).touch(exist_ok=True)

    if not Fs(str(resource.path)).is_dir:
        with open(str(resource.path), 'wb') as f:
            for chunk in resource.request.iter_content(
                                    chunk_size=fetcher.chunk_size):
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)
    return resource


def date_path_string(resource):
    import datetime
    return datetime.datetime.now().strftime("%d-%m-%y--%H-%M")


def snapshot(uri='http://random.org/', generate_section=date_path_string, fetcher=Fetcher):
    """ snapshot? Use this function to further; [snapshot]; a web resource into an
        Archival space on the disk. An already [fetched] resource will be moved
        into the archival directory under a generated name. Here the [dir] is
        to be treated as an :Archival ::Space. """

    resource = fetch(uri, fetcher)
    generated_str = generate_section(resource)
    archive_path = Fs(fetcher.archive_dir) + generated_str + resource.local_dir

    if View(archive_path).exists():
        Make(archive_path).remove()

    Make(archive_path).dirs()
    Make(resource.path).move(towards=archive_path)
    resource.path = Fs(archive_path) + resource.filename
    return resource


def forget(uri='http://random.org/', intermediate_path='.', fetcher=Fetcher):
    """ forget? Use this function to; [forget]; an already [fetched] or
        archived resource on the disk. Works both on fetched resources and
        snapshotted ones."""
    # First, :check [if] {: [resource [.netloc]] } :has remnants on either directory.
    # Check if part of the urls' netloc (or urls.path) inside fetch dir
    # The other location you should expect a lot of paths connected with a single fetch "name"
    # Whatever, do :your part! will you !?
    path = os.path.join(fetcher)


def clear_resources(fetcher=Fetcher):
    """ clear_resources? Use this to; [clean up]; after the [:Fetcher] deinstalls. """
    pass

# ~.~

def eye_fetch_1():
    urls = [
        'https://www.iana.org/domains/reserved',
        'https://cdn.pornpics.com/pics1/2018-03-29/512309_05big.jpg',
        'https://cdn.pornpics.com/pics1/2018-03-29/512309_06big.jpg',
        'https://cdn.pornpics.com/pics1/2018-03-29/512309_11big.jpg',
        'https://cdn.pornpics.com/pics1/2018-03-29/512309_10big.jpg',
        'https://cdn.pornpics.com/pics1/2018-03-29/512309_12big.jpg',
        'https://cdn.pornpics.com/pics1/2018-03-29/512309_13big.jpg',
        'https://cdn.pornpics.com/pics1/2017-01-12/393496_01big.jpg',
        'https://www.pornpics.com/galleries/asian-solo-girl-saya-song-pulls-down-her-jean-shorts-on-her-way-to-posing-nude/',
    ]
    input = Fs('/home/boril/Desktop/Tests/input')
    output = Fs('/home/boril/Desktop/Tests/output')
    fetch_dir = str(output + 'fetched')
    archive_dir = str(output + 'archive')

    config = Config(fetch_dir=fetch_dir,
                archive_dir=archive_dir,
                chunk_size=4096)

    fetcher = Fetcher(config)

    for url in urls:
        resource = fetch(url, fetcher)
        print('resource:', str(resource))
        if resource.is_text:
            print('resource.as_text:', resource.as_text)
        else:
            print('resource.is_text:', False)

def eye_snapshot_1():
    input = Fs('/home/boril/Desktop/Tests/input')
    output = Fs('/home/boril/Desktop/Tests/output')
    fetch_dir = str(output + 'fetched')
    archive_dir = str(output + 'archive')

    config = Config(fetch_dir=fetch_dir,
                archive_dir=archive_dir,
                chunk_size=4096)

    fetcher = Fetcher(config)
    resource = snapshot(uri='https://api.random.org/json-rpc/1/invoke', fetcher=fetcher)
    print('resource:', resource.as_text)

if __name__ == '__main__':
    eyes = [
        eye_fetch_1,
        eye_snapshot_1,
    ]
    ignored = [
        # eye_fetch_1,
        eye_snapshot_1,
    ]
    for eye in eyes:
        if not eye in ignored:
            eye()
# ~.~ The interface is [:completed] and deemed [perfect], by? katakatana
