#!/usr/bin/env python
import io
from setuptools import setup, find_namespace_packages
from adminsortable2 import __version__


def readfile(filename):
    with io.open(filename, encoding='utf-8') as fd:
        return fd.read()


DESCRIPTION = 'Generic drag-and-drop sorting for the List, the Stacked- and the Tabular-Inlines Views in the Django Admin'

CLASSIFIERS = [
    'Environment :: Web Environment',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    'Topic :: Software Development :: Libraries :: Application Frameworks',
    'Development Status :: 5 - Production/Stable',
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3.10',
    'Programming Language :: Python :: 3.11',
    'Programming Language :: Python :: 3.12',
    'Framework :: Django',
    'Framework :: Django :: 4.2',
    'Framework :: Django :: 5.0',
    'Framework :: Django :: 5.1',
    'Framework :: Django :: 5.2',
]


setup(
    name='django-admin-sortable2',
    version=__version__,
    author='Jacob Rief',
    author_email='jacob.rief@gmail.com',
    description=DESCRIPTION,
    long_description=readfile('README.md'),
    long_description_content_type='text/markdown',
    url='https://github.com/jrief/django-admin-sortable2',
    license='MIT',
    keywords=['django'],
    platforms=['OS Independent'],
    classifiers=CLASSIFIERS,
    install_requires=[
        'Django>=4.2',
    ],
    packages=find_namespace_packages(exclude=['client', 'testapp', 'testapp*', 'docs']),
    include_package_data=True,
    zip_safe=False,
)
