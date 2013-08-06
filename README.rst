dictproxyhack
=============

Exposes the immutable ``dictproxy`` type to all (?) versions of Python.

PEP416_ asked for a ``frozendict`` type, but was rejected.  The alternative was
to publicly expose ``dictproxy``, the type used for ``obj.__dict__``, which
wraps an existing dict and provides a read-only interface to it.  The type has
existed since 2.2, but it's never had a Python-land constructor.

Until now.  But only in 3.3+.  Which is not all that helpful to some of us.

This module clumsily exposes the same type to previous versions of Python.

.. _PEP416: http://www.python.org/dev/peps/pep-0416/

Usage
-----

::

    from dictproxyhack import dictproxy

    myproxy = dictproxy(dict(foo="bar"))
    print(myproxy['foo'])
    myproxy['baz'] = "quux"  # TypeError

Since the proxy holds a reference to the underlying ``dict`` (but doesn't provide
any way to get it back), you can trivially implement ``frozendict``::

    def frozendict(*args, **kwargs):
        return dictproxy(dict(*args, **kwargs))

Might as well just inline that where you need it, really.

Dependencies
------------

Python.  Should work anywhere.  Maybe.

On **Python 3.3+**, you get the real ``mappingproxy`` type, which lives in the
``types`` module as ``MappingProxyType``.

On **CPython 2.5+**, you get a fake class that forcibly instantiates
``dictproxy`` objects via ``ctypes`` shenanigans.

On **nearly anything else**, you get a regular class that wraps a dict and
doesn't implement any mutating parts of the mapping interface.  Not a fabulous
solution, but good enough, and only applies until your favorite port catches up
with 3.3's standard library.

On **non-C Python ports that predate 2.6**, you get pretty much a ``dict``,
because the ``Mapping`` ABC doesn't even exist.  Sorry.

The shim classes also fool ``isinstance`` and ``issubclass``, so your dirty
typechecking should work equally poorly anywhere.

I've only actually tried this library on CPython 2.6, 2.7, 3.2, 3.3, and PyPy
2.1, but I'm interested in hearing whether it works elsewhere.

Gotchas
-------

Don't subclass ``dictproxy``.  Python 3.3+ won't let you, and the shims for other
versions are of extremely dubious use.

``dictproxy`` has been renamed to ``mappingproxy`` in 3.3+, so don't rely on
``repr`` to match across versions or anything.  (It seemed apropos to use the
older name for this module.)
