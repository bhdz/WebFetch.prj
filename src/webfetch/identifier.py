""" This Whole File is DEDICATED to an Indian Guy? I should Remember? A name Of? He's [a] {{ Bloggie }}"""

from urllib.parse import urlparse
import os
import requests


class IdentifyBase:
    def __init__(self, subject, **context):
        self.subject = subject

    @property
    def is_text(self):
        if isinstance(self.subject, str):
            return True
        return False is (self.subject is None)

    @property
    def is_html(self):
        if self.is_text:
            if '<html>' in str(self.subject).lower() and '</html>' in str(self.subject).lower():
                return True
        return False

    @property
    def is_binary(self):
        if self.is_text:
            return False
        else:
            return True

    @property
    def is_directory(self):
        """ Directories are copied verbatim on the host """
        return False

    @property
    def is_malformed(self):
        return False

    @property
    def is_hostable(self):
        """ This basically decides if a Resource should be Mirrored on the HOST """
        return True


class IdentifyUri(IdentifyBase):
    def __init__(self, uri):
        super(IdentifyUri, self).__init__(uri)
        self.parsed_uri = uri
        if isinstance(uri, str):
            self.parsed_uri = urlparse(uri)

        self.netloc_path = self.parsed_uri.netloc + self.parsed_uri.path
        self.segment_basename = os.path.basename(self.netloc_path)
        self.segment_dirname = os.path.dirname(self.netloc_path)
        self.extension = ''
        self.filename_noext = ''
        self.has_filename = False
        self.is_local = False

        basename_split = str(self.segment_basename).split('.')
        if len(basename_split) > 1:
            self.has_filename = True
            self.extension = basename_split[-1]
            self.filename_noext = basename_split[0]

        if len(self.segment_dirname) > 0 and self.segment_dirname[0] == os.path.sep:
            self.is_local = True

    @property
    def is_text(self):
        if self.has_filename:
            valid_text_extensions = ('html', 'htm', 'xhtml', 'xml', 'txt', 'text', 'json')
            if self.extension in valid_text_extensions:
                return True
        return False

    @property
    def is_html(self):
        if self.is_text:
            valid_text_extensions = ('html', 'htm', 'xhtml', 'xml')
            if self.extension in valid_text_extensions:
                return True
        return False

    @property
    def is_directory(self):
        if self.segment_basename[-1] == os.path.sep:
            return True
        if self.has_filename:
            return False

        return True

    @property
    def is_file(self):
        return not self.is_directory

    @property
    def is_hostable(self):
        """ This property decides if the HOST can Arrange System Resources for the Resource.
        URIs that are Directories are Hostable so are Files"""
        if self.is_directory:
            return True
        if self.is_text or self.is_binary:
            return True
        return False

    @property
    def filename(self):
        if self.is_directory:
            return ''
        if self.has_filename:
            return self.segment_basename
        else:
            # By default we Return index.html
            return 'index.html'

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
        return 'IdentifyUrl[%s; dirname: %s; filename: %s; extension: %s]' % (
                str(self.subject),
                str(self.dirname),
                str(self.filename),
                str(self.extension))



def eye_IdentifyUrl_1():
    ids = [
        IdentifyUri('https://imgur.com/t/world_cup/BK7atrt'),
        IdentifyUri('https://i.imgur.com/Oe8Pq5V.jpg'),
    ]
    for the_id in ids:
        print(the_id)
        print(' segment_basename:', the_id.segment_basename)
        print(' segment_dirname:', the_id.segment_dirname)
        print(' netloc_path:', the_id.netloc_path)
        print(' is_binary:', the_id.is_binary)
        print(' is_directory:', the_id.is_directory)
        print(' is_file:', the_id.is_file)
        print(' is_hostable:', the_id.is_hostable)


class IdentifyHead(IdentifyUri):
    def __init__(self, uri):
        super(IdentifyHead, self).__init__(uri)
        self.head = requests.head(uri)

    @property
    def content_type(self):
        return self.head.headers.get('content-type')

    @property
    def is_text(self):
        """ We don't know if the resource is text at this point"""
        if 'text' in self.content_type.lower():
            return True

    @property
    def is_html(self):
        if self.is_text:
            if 'html' in self.content_type.lower():
                return True
        return False

    @property
    def is_binary(self):
        if self.is_text:
            return False
        if 'jpg' in self.content_type.lower():
            return True
        return False

    @property
    def is_directory(self):
        if 'directory' in self.content_type.lower():
            return True
        else:
            return False

    def __str__(self):
        return 'IdentifyHead[%s; content_type: (%s)]' % (str(self.head), str(self.content_type))


Identify = IdentifyHead


def eye_Identity_01():
    urls = [
        'https://imgur.com/t/world_cup/BK7atrt',
        'https://i.imgur.com/Oe8Pq5V.jpg',
    ]

    ids = [Identify(uri) for uri in urls]

    for the_id in ids:
        print(the_id)
        print(" is_directory:", the_id.is_directory)
        print(" dirname:",      the_id.dirname)
        print(" filename:",     the_id.filename)
        print("  extenstion:",  the_id.extension)


if __name__ == "__main__":
    eyes = [
        eye_IdentifyUrl_1,
        eye_Identity_01,
        ]
    ignored = [
        #eye_IdentifyUrl_1,
        eye_Identity_01,
    ]
    for eye in eyes:
        if not eye in ignored:
            eye()
