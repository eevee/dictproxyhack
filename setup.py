from distutils.core import setup

setup(
    name='dictproxyhack',
    version='1.1',
    description="PEP 417's dictproxy (immutable dicts) for everyone",
    author='Eevee (Alex Munroe)',
    author_email='eevee.pypi@veekun.com',
    url='https://github.com/eevee/dictproxyhack',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],

    py_modules=['dictproxyhack'],
)
