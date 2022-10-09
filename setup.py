# encoding: utf-8
from setuptools import setup, find_packages

__version__ = "1.0.2"
__author__ = 'darr_en1'
__email__ = 'zhouttt1995@gmail.com'
readme_path = 'README.md'
SHORT = 'Python version client based on Apollo'

setup(
    name='strengthen-apollo-client',
    version=__version__,
    packages=find_packages(),
    install_requires=[
        'requests',
        'pyyaml'

    ],
    url='https://github.com/Darr-en1/pyapollo',
    author=__author__,
    author_email=__email__,
    classifiers=[
        'Programming Language :: Python :: 3.6',
    ],
    include_package_data=True,
    package_data={'': ['*.py', '*.pyc']},
    zip_safe=False,
    platforms='any',

    description='Python version client based on Apollo',
    long_description=open(readme_path, encoding='utf-8').read(),
    long_description_content_type='text/markdown',
)
