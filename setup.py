import os
from setuptools import setup, find_packages
import adminsortable

DESCRIPTION = 'Generic drag-and-drop ordering for objects in the Django admin interface'

CLASSIFIERS = [
    'Environment :: Web Environment',
    'Framework :: Django',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Development Status :: 4 - Beta',
]

def read(fname):
    # read the contents of a text file
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='django-admin-sortable2',
    version=adminsortable.__version__,
    author='Jacob Rief',
    author_email='jacob.rief@gmail.com',
    description=DESCRIPTION,
    long_description=read('README.rst'),
    url='https://github.com/jrief/django-admin-sortable2',
    license='MIT',
    keywords = ['django'],
    platforms=['OS Independent'],
    classifiers=CLASSIFIERS,
    install_requires=['Django>=1.4'],
    packages=find_packages(exclude=['example', 'docs']),
    include_package_data=True,
)
