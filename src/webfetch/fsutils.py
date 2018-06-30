import os
import pathlib
import glob
import copy
import shutil

class Fs(object):
    """ Fs? Represents a basic [Filesystem] object
        (file, directory, pipe, etc.) """

    def __init__(self, *segments, **keywords):
        self.path = None
        self._validity = False
        origin = keywords.get('origin', '')
        self._set(*segments, origin=origin)

    def _set(self, *segments, **keywords):
        origin = str(keywords.get('origin', ''))
        first = ''
        segment = os.path.join(str(origin), str(first))
        self.path = segment

        for segment in segments:
            self.path = os.path.join(self.path, str(segment))

        self.path = pathlib.Path(self.path)
        self._validity = True

    def __add__(self, another):
        return Fs(os.path.join(str(self), str(another)))

    def __str__(self):
        return str(self.path)

    @property
    def is_valid(self):
        returnVal = self._validity
        if not self._validity:
            returnVal = False
        else:
            if self.path.exists():
                returnVal = True
            else:
                returnVal = False
        return returnVal

    @property
    def is_file(self):
        if self.is_valid:
            return self.path.is_file()
        return False

    @property
    def is_dir(self):
        #if self.is_valid:
        return self.path.is_dir()
        #return False

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
    def __init__(self, *targets, **kwargs):
        for target in targets:
            if not isinstance(target, Fs):
                target = Fs(target)

            if '*' in str(target):
                self.extend([ Fs(globbed) for globbed in glob.glob(str(target)) ])
            else:
                self.append(target)

    def apply(self, f, *args, **kwargs):
        retF = {}
        for target in iter(self):
            retF[target] = f(target, *args, **kwargs)
            # retF.append(retF)
        return retF

    def map(self, Functor, *Arguments, **context):
        """ Sorry it HJAD to be Komplikated: Github -> ZoВ za POMOOOSHT ->> haha: -> Fail: :Glas~Shepot ->> New_Instance Instance :hInstance = Haha; :LOL -> ALLOWED! In :Hell {My Fav. Drink that contains KAFFEINE}"""
        #
        # Sorry Darlin' It has to .be {Complicated; +Darlin: [[ The katse ]] } ->> FAILS ->> ha! biatch !? I hate u but I still remember... alofit...yesIdidMaybeNowIamNotSoSureFLESHisJUSTFuckingFLESHIdeasAREINTERESting$23
        #
        Checker = context.pop('map__Checker', None)
        Checker_args = context.pop('map__Checker_args', tuple())
        Checker_kwargs = context.pop('map__Checker_kwargs', dict())
        Cache = context.pop('map__Cache', None)
        Cache_reverse = context.pop('map__Cache_reverse', None)

        RetF = []
        for Target in iter(self):
            Target_Valid = False

            def checker_default(path_target):
                if not path_target:
                    Target_Valid = False
                else:
                    Target_Valid = True

                if Target_Valid:
                    if not isinstance(path_target, Fs):
                        path_target = Fs(path_target)
                else:
                    return False
                return path_target.is_valid

            if Checker:
                Target_Valid = Checker(Target, *Checker_args, **Checker_kwargs)
            else:
                Target_Valid = checker_default(Target)

            #
            # &Later: Now I have to decide between 3 documents and 2 places in 1 place closer to where I found/lost you...
            #

            if Target_Valid:
                calculated = False
                if Cache:
                    if RetF in Cache:
                        RetF = Cache[Target]
                    else:
                        RetF = Functor(Target, *Arguments, **context)
                        calculated = True
                else:
                    RetF = Functor(Target, *Arguments, **context)
                    calculated = True
                #
                # Cache(retF)? Optional? Check the Context ((haha))
                #
                if Cache is not None and calculated:
                    Cache[Target] = RetF
                    if Cache_reverse is not None:
                        Cache_reverse[RetF] = Target
                RetF.append(RetF)
        return RetF


def eye_Selection_1():
    sel = Selection('/home/boril/Desktop/Everything/*', '/home/an*')

    def f1(target):
        print('f1? target:', target)

    def f2(target):
        print('f2? target = ', target)
        return str(target) + ' :: ' + str(hash(str(target)))

    result = sel.apply(f1)
    print('result:', result)

    cache = dict()
    cache_reverse=dict()
    result = sel.map(f2, map__Cache=cache, map__Cache_reverse=cache_reverse)
    print('result:', str(result))
    print('Cache:', cache)
    print('Cache_reverse:', cache_reverse)

    class Printer(object):
        def line(self, target):
            print('Printer? line:', target)

    printer = Printer()
    sel.apply(printer.line)


class Action(object):
    """ This is A Functor Base class for all [Actions]; that
    are defined bellow in their respective classes; Thank you . Cheer Cheer . The DOORS ~was Her idea right? right.; Because of a Movie idiot Char. right? right. gewd... HE's stupid now... haha...
    """
    def __init__(self, **kwargs):
        self.keywords = copy.deepcopy(kwargs)
        self.reversible = False

    def __call__(self, target, *args, **keywords):
        return object()

    def __getitem__(self, key):
        return self.keywords[key]

    def __setitem__(self, key, value):
        self.keywords[key] = value

    def copy(self):
        """ Returns {:a ~ copy ~ of :: self} """
        return self.__class__(**self.keywords)


class Listing(Action):
    """ Use this if you want to [: yield ] paths that :are {Expanded}.
    The only Difference between Gather and Listing is that Gather returns a
    list and Listing yields the paths as a Generator."""
    def __init__(self, topdown=False, include_dirs=True):
        super(Listing, self).__init__(topdown=True, include_dirs=include_dirs)

    def __call__(self, target):
        topdown = self.keywords.pop('topdown', None)
        include_dirs = self.keywords.pop('include_dirs', False)

        for root, dirs, files in os.walk(str(target), topdown):
            if include_dirs:
                for dir in dirs:
                    yield Fs(os.path.join(root, dir))

            for file in files:
                yield Fs(os.path.join(root, file))


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
                    path = Fs(os.path.join(root, dir))
                    gathered.append(path)

            for file in files:
                path = Fs(os.path.join(root, file))
                gathered.append(path)

        return gathered

class Gather2(Action):
    """ Gather2(the_sheep): baaaaa! haha! Use this Functor in order to
    Gather a number of targets, glob them, and then return them as a list.
    [the_sheep] here represents a single (and expandable) path that may contain
    **stars** """
    def __init__(self, topdown=False, include_dirs=False):
        super(Gather2, self).__init__(topdown=topdown, include_dirs=include_dirs)

    def __call__(self, target):
        topdown = self.keywords.get('topdown', True)
        include_dirs = self.keywords.get('include_dirs', False)
        listing = Listing(topdown=topdown, include_dirs=include_dirs)
        paths_gathered = []
        for path in listing(target):
            paths_gathered.append(path)
        return paths_gathered


class Exists(Action):
    def __init__(self, topdown=False, include_dirs=True):
        super(Exists, self).__init__(topdown=topdown, include_dirs=include_dirs)

    def __call__(self, target):
        topdown = self.keywords.get('topdown', True)
        include_dirs = self.keywords.get('include_dirs', True)
        exists = os.path.exists(str(target))
        return exists


class On(object):
    """ This is a helper class that works on [a [Selection]] of targets.
    The main method is [self.do] that applies a number of [Actions] to the
    [Selection]"""
    def __init__(self, *targets):
        self.targets = Selection(*targets)
        self.results = {}
        self.total_results = []

    def do_yield(self, actions=[]):
        for action in actions:
            for target in self.targets:
                action_ret = action(target)
                try:
                    for action_result in iter(action_ret):
                        yield action_result
                except:
                    raise

    def do(self, actions=[]):
        """ Use this method when you want to apply a number of Actions
        on a Selection of targets"""
        self.results = {}
        self.total_results = []
        for action in actions:
            action_results = []
            for target in self.targets:
                action_results = action(target)
                try:
                    self.total_results.extend(iter(action_results))
                except:
                    self.total_results.append(action_results)
            self.results[action] = action_results


class View(On):
    """ View? is a class that doesn't change the filesystem. In the :future {: this could be implemented by monads, ? or then() stuff as per Promises(js) ?? but not now } """
    def gather(self, topdown=True, include_dirs=True):
                                                            # _state=Monad(self, targets=self.targets, total_results=[])
        action = Gather(topdown=topdown, include_dirs=True) # _state.shove(action=Gather(...))
                                                            # _state.shove(action=...)
                                                            # ...
        self.do(actions=[action])                           # return _state.do(actions=_state.actions).total_results
        return self.total_results

    def exists(self, topdown=True, include_dirs=True):
        action = Exists(topdown=topdown, include_dirs=include_dirs)
        self.do(actions=[action])
        if len(self.total_results) <= 1:
            return self.results[action]
        else:
            return self.total_results

    def listing(self, topdown=True, include_dirs=True):
        action = Listing(topdown=topdown, include_dirs=include_dirs)
        for path in self.do_yield(actions=[action]):
            yield path

    def __str__(self):
        return '(' + "; ".join([str(t) for t in self.targets]) + ')'

    def __iter__(self):
        return iter(self.targets)

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
    items = View('/home/boril/Desktop/Tes*').exists()
    try:
        for item in iter(items):
            print('exists:', item)
    except:
        print('exist:', items)

    print('~')
    view1 = View('/home/boril/Desktop1')
    view2 = View('/home/boril/Desktop')
    print(str(view1), '; exists? ', view1.exists())
    print(str(view2), '; exists? ', view2.exists())

class MakeDirs(Action):
    """ This takes some targets and makes directories out of them """
    def __init__(self, mode=0o777, exist_ok=False):
        super(MakeDirs, self).__init__(mode=mode, exist_ok=exist_ok)

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


class Remove(Action):
    def __call__(self,target):
        if target.is_dir:
            return shutil.rmtree(str(target))
        elif target.is_file:
            os.remove(str(target))
        else:
            raise Exception("Bad target")

class Moveback(Action):
    def __init__(self, towards):
        self.towards = towards

    def __call__(self, source):

        shutil.move(str(source), str(self.towards))
        return Fs(self.towards)

class Make(On):
    """ Make is a class that CHANGES the filesystem. In the :future {This would be Realized with Monads}"""
    def dirs(self, mode=0o777, exist_ok=False):
        action = MakeDirs(mode, exist_ok)
        self.do(actions=[action])
        return self.results[action]

    def touch(self, mode=0o777, exist_ok=False):
        action = Touch(mode=mode, exist_ok=exist_ok)
        self.do(actions=[action])
        return self.results[action]

    def move(self, towards):
        action=Moveback(towards=towards)
        #for target in self.targets:
        #    actions.append(Move(source=target))
        self.do(actions=[action])
        return self.results[action]

    def remove(self):
        action = Remove()
        self.do(actions=[action])
        return self.results[action]

    def __init__(self, *targets):
        super(Make, self).__init__(*targets)


def eye_Make_1():
    origin = Fs(origin='/home/boril/Desktop/Tests')
    print("origin?", origin)
    Make(origin + '1.text', origin+'2.text').touch(exist_ok=True)
    Make(origin+'dir.1', origin+'dir.2').dirs()
    Make(origin+'dir.1', origin+'dir.2').remove()

    print("View(origin).gather():", [str(t) for t in View(origin).gather()])
    for node in iter(View(origin, origin + '*.text', '/dev/*' )):
        print('node:', node)


if __name__ == "__main__":
    print('main:')
    eyes = [
        eye_Fs_2,
        eye_Selection_1,
        eye_View_1,
        eye_Make_1,
    ]

    ignored = [
        eye_Fs_2,
        eye_Selection_1,
        # eye_View_1,
        # eye_Make_1,
    ]

    for eye in eyes:
        if eye not in ignored:
            eye()
