import os
import sys
import pytest

TESTS = os.path.dirname(__file__)
ROOT = os.path.dirname(TESTS)

sys.path.insert(0, ROOT)

from nedoc.unit import Module  # noqa


@pytest.fixture()
def project1(tmpdir):
    p = tmpdir.mkdir("myproject")
    p.join("__init__.py").write('''
"""
Welcome to the testing project!

This is super nice testing project!

"""

from .mymodule1.myclass import MyClass
from myproject.mymodule1.functions import one_arg
from .mymodule1 import another
''')

    m = p.mkdir("mymodule1")
    m.join("functions.py").write('''
"""
This is main funcntion of myproject

The really nice list of functions!
"""

def mm1_main():
    """Main function of mm1"""
    pass

def mm1_main_undocumented():
    pass

def one_arg(arg1):
    pass

def two_args(arg1, next_arg=2):
    pass

def tree_args(arg1, arg2, arg3):
    pass

def many_args(myarg1,
              next_arg,
              additional_arg=call(1323),
              default_arg1=123,
              default_arg2='abc', tuple_arg=(1,2,3,4,5,6)):
    """This is super function.

    Title test
    ==========

    - *Bold text*
    - Normal text

    This is detailed describtion for super function!
    """
    pass
''')

    m.join("myclass.py").write('''
"""
Module containing a class

The really nice list of functions!
"""

from . import another
from ..mymodule1.another import AnotherClass2
from ..mymodule1.another import AnotherClass2 as Renamed
from myproject.mymodule1.another import AnotherClass3
from extern_package import ExternClass

class BaseClass:
    pass

class MyClass(BaseClass, another.AnotherClass):
    """
    Main testing class

    Overview
    ========

    This class was created for testing purposes.
    """

    def __init__(self, x, y=None):
        pass

    def __repr__(self):
        pass

    def do_something(self, x, y):
        """<h1>This is bad</h1>"""
        pass

    def overriden_method(self, x, y):
        pass

    def overriden_method2(self, x, y):
        "Have own doc"
        pass

    @staticmethod
    @functools.lru_cache(maxsize=None)
    def static_method(a):
        pass

    @classmethod
    @functools.lru_cache(maxsize=None)
    def class_method(cls, a):
        """ Class method comment """
        pass

    @abc.abstractmethod
    def abs_method(self, z):
        pass

class MyClass2(AnotherClass2):
    pass

class MyClass3(AnotherClass3):
    pass

class MyClass4(ExternClass):
    pass
''')

    m.join("another.py").write('''

class AnotherClass:
    def overriden_method(self, x, y):
        "Original method"
        pass

    def overriden_method2(self):
        "Original method2"
        pass

    def nonover(self):
        pass

    def nonover2(self, x):
        pass

class AnotherClass2:
    pass

class AnotherClass3:
    pass
''')

    m.join("garbage.txt").write('''
class ThisIsTrap:
    pass

+ and + not + parsable +
''')
    return tmpdir
