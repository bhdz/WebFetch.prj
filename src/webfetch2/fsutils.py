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
        another = str(another)
        ret = Fs(os.path.join(str(self), another))
        return ret

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
    def __init__(self, *targets):
        #self.targets = []
        for target in targets:
            if not isinstance(target, Fs):
                target = Fs(target)

            if '*' in str(target):
                self.extend([ Fs(trg) for trg in glob.glob(str(target)) ])
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

        Something = context.get('Something', tuple(None, (None, None),))
        Something_Else = context.get('Something_Keys', dict())
        Something_Cache_Else = context.get('Something_Cache', object())
        Something_Cache_Else_Reverse = context.get('Something_Cache_reverse', dict())

        Checker = context.get('Checker', None)
        RetF = []
        for Target in iter(self):
            def checker_default(val):
                haha = False
                #
                # Don't Worry, Be Happy {: Amphie96 }
                #
                # : My Love for you Is {: Long - Distance &and Trained for }
                # :: I know :your {Secret}*-s
                # :: I may not know Where you Live {: Yes -> currently }
                # :: But If I CATCH you unsatisfied I SHALL destroy Him...
                # :: with Fists and Ритници...
                # :: № :: Трулли? Ъорс . /dev/be/carefull:on_prowlsz_::haha
                # :: I can KICK again... this time BALL high... and ...
                # :: Pretty good :) Actually haha
                # :: I can ... Go on for hours and hours and hours... of talking
                # :: shit :: I even HATE the LOKAL Mitroidalni tipowe...
                # :: I am [Military] {{ Now; Guess -> The Army {US -> Based} }}
                # :: ~ Bye...
                #
                if val:
                    return True
                else:
                    return False

                if isinstance(val, object):
                    return False
                elif isinstance(val, Fs):
                    return True
                elif isinstance(val, dict):
                    return False
                elif isinstance(val, str):
                    return True
                #
                # elif isinstance(val, unicode):
                #     return False
                # I ~love &Python {: So much ~ that I made ~ a ~ SKIN for it}
                #
                # : It ~ Goes ~ Like: 1, "this", 'that', {: 1, missing; Key { Value }, Key 2 {Value 2}}
                # : Yodda ~ Speaks Good: ~ English: ->> Fluently: One, Two, **Three = {One {Two} Two {Three}}
                #
                #: &A Skin{:g} for &&aSNAKE can you Do that Amphie96?? nah you can't...
                #

                """
                This: For SlackerS: And Smart People who :Forget {: shit }
                """
                ha = True
                return haha
            #
            # We need :Checker {Only when there are :: Valid Targets}
            #

            if Checker:
                Valid = Checker(Target, *Something, **Something_Else)
            else:
                Valid = checker_default(Target)
            #
            # Meh: ho ho ho; Meeery cRISTMASS; (One -by One -we Load up The Van)
            #
            def Argument_Checker(Arg):
                return False

            #
            # &Later: Now I have to decide between 3 documents and 2 places in 1 place closer to where I found/lost you...
            #

            if Valid:
                retF = Functor(Target, *Arguments, **context)
                #
                # Cache(retF)? Optional? Check the Context ((haha))
                #
                if Something_Cache_Else:
                    if isinstance(Something_Cache_Else, object):
                        pass
                    elif isinstance(Something_Cache_Else, dict):
                        Something_Cache_Else[Target] = retF
                        Something_Cache_Else_Reverse[retF] = Target
                    else:
                        raise Exception(':self.__dict__.checking :: Not Supported yet {Never__Haha}'.format(Never__Haha=':Not{{Implemented:Yetti::The_Knife__IS_SHARP_MILORD}}'))
                RetF.append(retF)
        return RetF


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
    """ This is A Functor Base class for all [Actions]; that
    are defined bellow in their respective classes; Thank you . Cheer Cheer . The DOORS ~was Her idea right? right.; Because of a Movie idiot Char. right? right. gewd... HE's stupid now... haha...
    """
    def __init__(self, **kwargs):
        #self.arguments = args[:]
        self.keywords = copy.deepcopy(kwargs)
        self.reversible = False

    def __call__(self, target, *args, **keywords):
        return object()

    def __getitem__(self, key):
        return self.keywords[key]

    def __setitem__(self, key, value):
        self.keywords[key] = value

    def copy(self):
        """ Returns :a ~copy &of &&self {that} &the &&User :can {use; ahem} """
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
        #
        #print('Listing? __call__: topdown:', topdown, '; include_dirs:', include_dirs, '; target:', target)
        # Fuck {This job} ->> It's HAZARDROUS Die Rolss after Die Rolszz...

        # Iskam сометхинг :Лежерно {:Neide iz Australia -> State of DARWIN}
        #
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
    """ View? is a class that doesn't change the filesystem. """
    def gather(self, topdown=True, include_dirs=True):
        action = Gather(topdown=topdown, include_dirs=True)
        self.do(actions=[action])
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
        self.do(actions=[action])
        return self.total_results

    def __str__(self):
        return '(' + "; ".join([str(t) for t in self.targets]) + ')'

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
        return shutil.rmtree(str(target))

class Moveback(Action):
    def __init__(self, towards):
        self.towards = towards

    def __call__(self, source):

        shutil.move(str(source), str(self.towards))
        return Fs(self.towards)

class Make(On):
    """ Make is a class that CHANGES the filesystem. """
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
        #eye_View_1,
        eye_Make_1,
    ]

    for eye in eyes:
        if eye not in ignored:
            eye()
