""" URI Identity? This - is """


class Identity(object):
    @property
    def is_live(self):
        return False # We Asume it S?HALL?? not be LIVE by Default
    
    @property
    def is_downloadable(self):
        self._downloadable = False
        return self._downloadable # We asume there IS some state there... hmmm... and the third?
        
    @property
    def is_text(self):
        self._is_text = False
        return self._is_text        # We ASUME this is The minimum INFORMAtion there iS for a Single URI
    
    def __init__(self, uri_pr, **context):
        self._is_text = None
        self._is_downloadable = None
        
        if uri_pr:
            self.uri_parsed = uri_pr
        else:
            self.uri = uri_pr
        
        
# Main Class that should be Used... 
class UriIdentity(Identity):
    def __init__(self, uri, *whatever, **keys):
        keys2 = {}
        super(UriIdentity, self).__init__(uri, **keys2)
        
        
class HeadIdentity(Identity):
    def __init__(self, uri, head, **keys):
        pass
        
class DoubleCheckIdentity(Identity):
    """See? The Original Version; Keep this KLEAN as possible, please . /dev/stdout"""
    def __init__(self, uri, head, **keys):
        pass
