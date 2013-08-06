"""Exposes the immutable `dictproxy` type to all (?) versions of Python.
Should work in 2.2+, 3.0+.  Actually tried on 2.6, 2.7, 3.2, 3.3, and PyPy 2.1.

Usage is easy:

    from dictproxyhack import dictproxy
    myproxy = dictproxy(dict(foo="bar"))
    print(myproxy['foo'])
    myproxy['baz'] = "quux"  # TypeError

dictproxy is GvR's answer to the desire for a "frozendict" type; see the
PEP at http://www.python.org/dev/peps/pep-0416/#rejection-notice.  It's the
type of `__dict__` attributes, and it exposes a read-only view of an
existing dict.  Changes to the original dict are visible through the proxy,
but the proxy itself cannot be changed in any way.

dictproxy has been publicly exposed in Python 3.3 as `types.MappingProxyType`.
It already exists in earlier versions of Python, back to the dark days of 2.2,
but doesn't expose a constructor to Python-land.  This module hacks one in.
Enjoy.
"""

import unittest

__all__ = ['dictproxy']

def _get_from_types():
    # dictproxy is exposed publicly in 3.3+.  Easy.
    from types import MappingProxyType
    return MappingProxyType


realdictproxy = type(type.__dict__)

class dictproxymeta(type):
    def __instancecheck__(self, instance):
        return (
            isinstance(instance, realdictproxy)
            # This bit is for PyPy, which is failing to notice that objects are
            # in fact instances of their own classes -- probably an MRO thing
            or type.__instancecheck__(self, instance)
        )

    def __subclasscheck__(self, cls):
        return issubclass(cls, realdictproxy)

def _add_isinstance_tomfoolery(cls):
    # Given a class (presumably, a dictproxy implementation), toss in a
    # metaclass that will fool isinstance (and issubclass) into thinking that
    # real dictproxy objects are also instances of the class.

    # But first we need to agree with the metaclasses on the existing class
    # oh boy!  This is only a problem when using the super fallback of just
    # writing a class, because it ends up with ABCMeta tacked on.
    try:
        from sets import Set as set
    except NameError:
        pass

    metas = set([type(supercls) for supercls in cls.__mro__])
    metas.discard(type)
    if metas:
        metacls = type('dictproxymeta', (dictproxymeta,) + tuple(metas), {})
    else:
        metacls = dictproxymeta

    # And this bit is necessary to work under both Python 2 and 3.
    return metacls(cls.__name__, (cls,), {})


def _get_from_c_api():
    """dictproxy does exist in previous versions, but the Python constructor
    refuses to create new objects, so we must be underhanded and sneaky with
    ctypes.
    """
    from ctypes import pythonapi, py_object

    PyDictProxy_New = pythonapi.PyDictProxy_New
    PyDictProxy_New.argtypes = (py_object,)
    PyDictProxy_New.restype = py_object

    # To actually create new dictproxy instances, we need a class that calls
    # the above C API functions, but a subclass would also bring with it some
    # indirection baggage.  Let's skip all that and have the subclass's __new__
    # return an object of the real dictproxy type.
    # In other words, the `dictproxy` class being created here is never
    # instantiated and never does anything.  It's a glorified function.
    # (That's why it just inherits from `object`, too.)
    class dictproxy(object):
        """Read-only proxy for a dict, using the same mechanism Python uses for
        the __dict__ attribute on objects.

        Create with dictproxy(some_dict).  The original dict is still
        read/write, and changes to the original dict are reflected in real time
        via the proxy, but the proxy cannot be edited in any way.
        """

        def __new__(cls, d):
            if not isinstance(d, dict):
                # I suspect bad things would happen if this were not true.
                raise TypeError("dictproxy can only proxy to a real dict")

            return PyDictProxy_New(d)

    # Try this once to make sure it actually works.  Because PyPy has all the
    # parts and then crashes when trying to actually use them.
    # See also: https://bugs.pypy.org/issue1233
    dictproxy(dict())

    # And slap on a metaclass that fools isinstance() while we're at it.
    return _add_isinstance_tomfoolery(dictproxy)

def _get_from_the_hard_way():
    # Okay, so ctypes didn't work.  Maybe this is PyPy or something.  The only
    # choice left is to just write the damn class.
    try:
        from collections.abc import Mapping
    except ImportError:
        try:
            from collections import Mapping
        except ImportError:
            # OK this one is actually mutable, but this will only fire on a
            # non-C pre-2.6 Python implementation, so whatever.  You can
            # already swap out the `d` attribute below so it's not like this is
            # a perfect solution.
            from UserDict import DictMixin as Mapping

    class dictproxy(Mapping):
        def __init__(self, d):
            self.d = d

        def __getitem__(self, key):
            return self.d[key]

        def __len__(self):
            return len(self.d)

        def __iter__(self):
            return iter(self.d)

        def __contains__(self, key):
            return key in self.d

    return _add_isinstance_tomfoolery(dictproxy)


try:
    dictproxy = _get_from_types()
except ImportError:
    try:
        dictproxy = _get_from_c_api()
    except Exception:
        dictproxy = _get_from_the_hard_way()


class UselessWrapperClassTestCase(unittest.TestCase):
    def test_dict_interface(self):
        d = dict(a=1, b=2, c=3)
        dp = dictproxy(d)

        self.assertEqual(dp['a'], 1)
        self.assertEqual(dp['b'], 2)
        self.assertEqual(dp['c'], 3)

        def try_bad_key():
            dp['e']

        self.assertRaises(KeyError, try_bad_key)

    def test_readonly(self):
        dp = dictproxy({})

        def try_assignment():
            dp['foo'] = 'bar'

        self.assertRaises(TypeError, try_assignment)

        def try_clear():
            dp.clear()

        self.assertRaises(AttributeError, try_clear)

    def test_live_update(self):
        d = dict()
        dp = dictproxy(d)

        d['a'] = 1

        self.assertEqual(dp['a'], 1)


    def test_isinstance(self):
        dp = dictproxy({})

        self.assertTrue(isinstance(dp, dictproxy))
        self.assertTrue(isinstance(type.__dict__, dictproxy))

if __name__ == '__main__':
    unittest.main()
