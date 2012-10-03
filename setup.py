import os
from distutils.core import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(name='django-aweber',
    version='0.3',
    description = "An Aweber based user-signup application for Django",
    long_description = read('README'),
    author='Val Neekman',
    author_email='val@neekware.com',
    url='http://github.com/un33k/django-aweber',
    packages=['aweber'],
    install_requires = ['python-emailahoy',],
    classifiers=['Development Status :: 4 - Beta',
                 'Environment :: Web Environment',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: BSD License',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python',
                 'Topic :: Utilities'],
    )
