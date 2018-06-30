import os
import pathlib
import glob
import copy


class Fs(object):
    """ Fs? Represents a basic [Filesystem] object
        (file, directory, pipe, etc.) """

    def __init__(self, first, *segments, **keywords):
        self.path = None
        self._validity = False
        origin = keywords.get('origin', '')
        self._set(first, *segments, origin=origin)

    def _set(self, first, *segments, **keywords):
        origin = str(keywords.get('origin', ''))
        segment = os.path.join(str(origin), str(first))
        self.path = segment

        for segment in segments:
            self.path = os.path.join(self.path, str(segment))

        self.path = pathlib.Path(self.path)
        self._validity = True

    def __add__(self, another):
        another = str(another)
        ret = Fs(os.path.join(str(self), another))
        return ret

    def __str__(self):
        return str(self.path)

    @property
    def is_valid(self):
        if not self._validity:
            return False
        if self.path.exists():
            return True
        return False

    @property
    def is_file(self):
        if self.is_valid:
            return self.path.is_file()
        return False

    @property
    def is_dir(self):
        if self.is_valid:
            return self.path.is_dir()
        return False

    @property
    def is_absolute(self):
        return os.path.isabs(str(self.path))

    @property
    def is_relative(self):
        return not os.path.isabs(str(self.path))


def eye_Fs_2():
    import getpass
    USER = getpass.getuser()

    fss = [
        Fs('/dev/stdout'),
        Fs('{user}'.format(user=USER), 'Desktop', origin='/home'),
        Fs('home/ani', 'Desktop', 'Do'),
        Fs('Desktop', origin=Fs('/home/boril')),
    ]
    first = True
    for fs in fss:
        if not first:
            print('~')
        print('fs:', fs)
        print('fs.is_valid:', fs.is_valid)
        print('fs.is_file:', fs.is_file)
        print('fs.is_dir:', fs.is_dir)
        print('fs.is_absolute:', fs.is_absolute)
        print('fs.is_relative:', fs.is_relative)

        first = False

    print('fs? __add__:', fss[0] + fss[1])


class Selection(list):
    """ Selection? supports << targets >>. """
    def __init__(self, *targets, glob_targets=True):
        #self.targets = []
        for target in targets:
            if not isinstance(target, Fs):
                target = Fs(target)

            if glob_targets and ('*' in str(target)):
                self.extend(glob.glob(str(target)))
            else:
                self.append(target)

    def apply(self, f, *args, **kwargs):
        for target in iter(self):
            f(target, *args, **kwargs)


def eye_Selection_1():
    sel = Selection('/home/boril/Desktop/Everything/*', '/home/an*', glob_targets=True)

    def f1(target):
        print('f1? target:', target)

    sel.apply(f1)

    class Printer(object):
        def line(self, target):
            print('Printer? line:', target)

    printer = Printer()
    sel.apply(printer.line)

class Action(object):
    """ This is a functor base class for all [Actions] that
    are defined bellow in their respective classes
    """
    def __init__(self, **kwargs):
        #self.arguments = args[:]
        self.keywords = copy.deepcopy(kwargs)
        self.reversible = True

    def __call__(self, target, *args, **keywords):
        pass

    def __getitem__(self, key):
        return self.keywords[key]

    def __setitem__(self, key, value):
        self.keywords[key] = value

    def copy(self):
        """ Returns a copy of self that the User can use ahem """
        return self.__class__(*self.arguments, **self.keywords)


class Listing(Action):
    """ Use this if you want to [: yield ] paths that :are {Expanded}.
    The only Difference between Gather and Listing is that Gather returns a
    list and Listing yields the paths as a Generator."""
    def __init__(self, topdown=False, include_dirs=True):
        super(Listing, self).__init__(topdown=True, include_dirs=include_dirs)

    def __call__(self, target):
        topdown = self.keywords.get('topdown', None)
        include_dirs = self.keywords.get('include_dirs', False)

        gathered = []
        #print('Listing? __call__: topdown:', topdown, '; include_dirs:', include_dirs, '; target:', target)
        for root, dirs, files in os.walk(str(target), topdown):
            if include_dirs:
                for dir in dirs:
                    yield  os.path.join(root, dir)

            for file in files:
                yield os.path.join(root, file)


class Gather(Action):
    """ Gather(the_sheep): baaaaa! haha! Use this Functor in order to
    Gather a number of targets, glob them, and then return them as a list.
    [the_sheep] here represents a single (and expandable) path that may contain
    **stars** """
    def __init__(self, topdown=True, include_dirs=True):
        super(Gather, self).__init__(topdown=topdown, include_dirs=include_dirs)

    def __call__(self, target):
        topdown = self.keywords.get('topdown', None)
        include_dirs = self.keywords.get('include_dirs',False)

        gathered = []
        for root, dirs, files in os.walk(str(target), topdown=topdown):
            if include_dirs:
                for dir in dirs:
                    path = os.path.join(root, dir)
                    gathered.append(path)

            for file in files:
                path = os.path.join(root, file)
                gathered.append(path)

        return gathered

class Gather2(Action):
    """ Gather(the_sheep): baaaaa! haha! Use this Functor in order to
    Gather a number of targets, glob them, and then return them as a list.
    [the_sheep] here represents a single (and expandable) path that may contain
    **stars** """
    def __init__(self, topdown=False, include_dirs=False):
        super(Gather2, self).__init__(topdown=topdown, include_dirs=include_dirs)

    def __call__(self, target):
        topdown = self.keywords.get('topdown', True)
        include_dirs = self.keywords.get('include_dirs', False)
        listing = Listing(topdown=topdown, include_dirs=include_dirs)
        gathered = []
        for item in listing(target):
            gathered.append(item)
        return gathered


class Exists(Action):
    def __init__(self, topdown=False, include_dirs=True):
        super(Exists, self).__init__(topdown=topdown, include_dirs=include_dirs)

    def __call__(self, target):
        #targets = glob.glob(str(target))

        topdown = self.keywords.get('topdown', True)
        include_dirs = self.keywords.get('include_dirs', True)

        listing = Listing(topdown=topdown, include_dirs=include_dirs)

        existence = [] #True
        for target in listing(target):
            exist = os.path.exists(target)
            existence.append(exist)
        return existence


class On(object):
    """ This is a helper class that works on [a [Selection]] of targets.
    The main method is [self.do] that applies a number of [Actions] to the
    [Selection]"""
    def __init__(self, *targets, glob_targets=True):
        self.targets = Selection(*targets, glob_targets=glob_targets)
        self.results = {}
        self.total_results = []

    def do(self, actions=[]):
        """ Use this method when you want to apply a number of Actions
        on a Selection of targets"""
        self.results = {}
        self.total_results = []
        for action in actions:
            action_results = []
            for target in self.targets:
                action_results = action(target)
                self.total_results.extend(action_results)
            self.results[action] = action_results


class View(On):
    """ View? is a class that doesn't change the filesystem. """
    def gather(self, topdown=True, include_dirs=True):
        action = Gather(topdown=topdown, include_dirs=True)
        self.do(actions=[action])
        return self.total_results

    def exists(self, topdown=True, include_dirs=True):
        action = Exists(topdown=topdown, include_dirs=include_dirs)
        self.do(actions=[action])
        return self.total_results

    def listing(self, topdown=True, include_dirs=True):
        action = Listing(topdown=topdown, include_dirs=include_dirs)
        self.do(actions=[action])
        return self.total_results


def eye_View_1():
    print('View? gather:')
    results = View('/home/boril/Desktop/Tests').gather(include_dirs=False)

    for item in results:
        print('item:', item)

    print('~')
    topdown=False
    print('View? gather: topdown={topdown}:'.format(topdown=topdown))
    results = View('/home/boril/Desktop/Tests/aaa1').gather(topdown=topdown)

    for item in results:
        print('item:', item)

    print('~')
    print('View? listing:')
    for item in View('/home/boril/Desktop/Tes*').listing():
        print('item:', item)


    print('~')
    for item in View('/home/boril/Desktop/Tes*', glob_targets=True).exists():
        print('exists:', item)

    print('~')

class MakeDirs(Action):
    """ This takes some targets and makes directories out of them """
    def __init__(self):
        super(MakeDirs, self).__init__()

    def __call__(self, target):
        mode = self.keywords.get('mode', 0o777)
        exist_ok = self.keywords.get('exist_ok', True)
        # Based on: https://stackoverflow.com/questions/273192/how-can-i-create-a-directory-if-it-does-not-exist
        def _mk_dir(directory):
            import errno
            try:
                os.makedirs(directory, mode, exist_ok)
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise

        _mk_dir(str(target))


class Touch(Action):
    """ This takes some targets and makes directories out of them """
    def __init__(self, mode=0o777, exist_ok=False):
        super(Touch, self).__init__(mode=mode, exist_ok=exist_ok)

    def __call__(self, target):
        exist_ok = self.keywords.get('exist_ok', True)
        mode = self.keywords.get('mode', 0o777)
        return target.path.touch(mode, exist_ok)

class Touch(Action):
    def __init__(self, towards_location=None):
        super(Touch, self).__init__(mode=mode, exist_ok=exist_ok)

    def __call__(self, target):
        towards_location = self.keywords.get('towards_location', '')
        shutil.rename(os.path.join(str(towards_location), os.path.basename(target)))

class Remove(Action):
    def __call__(self,target):
        shutil.remove(target)

class Make(On):
    """ Make is a class that CHANGES the filesystem. """
    def dirs(self, mode=0o777, exist_ok=False):
        action = MakeDirs(mode, exist_ok)
        self.do(actions=[action])
        return self.results[action]

    def touch(self, mode=0o777, exist_ok=False):
        action = Touch(mode, exist_ok)
        self.do(actions=[action])
        return self.results[action]


    def move(self, towards_location):
        action = Move(towards_location=towards_location)
        self.do(actions=[action])
        return self.results[action]

    def remove(self):
        action = Remove()
        self.do(actions=[action])
        return self.results[action]

    def __init__(self, *targets):
        super(Make, self).__init__(*targets)


class Mk(object):
    """ Given a valid Fs object(s), this class represents an action that changes
     the file system. For now, dirs(), touch() are supported. In the future I
     plan to abstract actions into their own object classes that are currently
     hardcoded functions. Sorry for that I gotta hurry :)"""

    def __init__(self, *targets):
        self.targets = Selection(*targets)

    def dirs(self, mode=0o777, exist_ok=True):
        # Based on: https://stackoverflow.com/questions/273192/how-can-i-create-a-directory-if-it-does-not-exist
        def _mk_dir(directory):
            import errno
            try:
                os.makedirs(directory, mode, exist_ok)
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise

        # Please: Replace me with self.targets.apply()
        for target in self.targets:
            _mk_dir(str(target))

    def touch(self, mode=0o777, exist_ok=False):
        # Please: Replace me with self.targets.apply() and a closure.
        for target in self.targets:
            target.path.touch(mode, exist_ok)

    def move(self, towards_location):
        for target in self.targets:
            target = os.path.join(str(towards_location), os.path.basename(target))
            shutil.rename(target)

    def remove(self):
        for target in self.targets:
            shutil.remove(target)


def eye_Fs_1():
    print('Fs:')
    fs = Fs('./tests/eye_Fs_1', 'foo/bar', 'baz/buzz')
    print(fs)
    print(fs.is_valid)
    print(fs.is_dir)
    print(fs.is_file)
    print(fs.is_absolute)
    print(fs.is_relative)

    print('Fs.2:')
    fs = Fs('./tests/eye_Fs_1', 'foo/bar', 'baz/buzz', origin = '..')
    print(fs)

    print('Mk:')
    print(fs)
    Mk(fs).dirs()

    Mk(fs+'test.text').touch(exist_ok=True)

    print('View:')
    # print( '\n'.join(View('/home/boril/*').listing()) )

    print('Mk().move():')

    fs1 = Fs('/home/boril/Desktop/Tests/from')
    fs2 = Fs('/home/boril/Desktop/Tests/to')

    Mk(fs1, fs2).dirs()
    Mk(fs1 + 'mk_move.text').touch()
    Mk(fs2).dirs()

    Mk(fs1+'mk_move.text').move(fs2+'mk_move.txt')

if __name__ == "__main__":
    print('main:')
    eyes = [
        eye_Fs_1,
        eye_Fs_2,
        eye_Selection_1,
        eye_View_1,
    ]

    ignored = [
        eye_Fs_1,
        eye_Fs_2,
        eye_Selection_1,
        #eye_View_1,
    ]

    for eye in eyes:
        if eye not in ignored:
            eye()
