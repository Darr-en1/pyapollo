# encoding: utf-8
"""
pyapollo 常用工具包


"""
from setuptools import setup, find_packages

SHORT = u'pyapollo'

setup(
    name='pyapollo',
    version='0.0.1',
    packages=find_packages(),
    install_requires=[
        'requests',
        'pyyaml'

    ],
    url='https://github.com/Darr-en1/pyapollo',
    author='darr_en1',
    author_email='zhouttt1995@gmail.com',
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
    ],
    include_package_data=True,
    package_data={'': ['*.py', '*.pyc']},
    zip_safe=False,
    platforms='any',

    description=SHORT,
    long_description=__doc__,
)
