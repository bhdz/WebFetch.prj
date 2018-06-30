
class Function(object):
    def __init__(self, first, *rest, **context):
        pass

    def Map_Over(self, Iterable, *whatever, **context):
        pass

    def Compose(self, Function, *Arguments, **Keywords):
        pass

    def Accumulate(self, *args, **keywords):
        pass

    def __call__(self, first, *rest, **keywords):
        pass

def eye_Function_01():
    def fib(n):
         # k'wo beshe bee

    def facturiel(n):
        pass

    f0 = Function(name="f0", body='yes').Compose(
            Function(name='facturiel', implementation=facturiel)
        ).Compose(
            Function(name='abs', implementation=abs)
        ).Compose(
            Function(name='fib', implementation=fib)
        ).Pack(end='yes')

    result = f0.Map_Over([1, 2, 3, 4, 5])
    print('result:', result)
