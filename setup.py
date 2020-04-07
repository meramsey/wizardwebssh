import codecs
from setuptools import setup
from wizardwebssh._version import __version__ as version


with codecs.open('README.rst', encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='wizardwebssh',
    version=version,
    description='Web based ssh client',
    long_description=long_description,
    long_description_content_type='text/x-rst',
    author='Michael Ramsey',
    author_email='mike@hackerdise.me',
    url='https://gitlab.com/mikeramsey/wizardwebssh',
    packages=['wizardwebssh'],
    entry_points='''
    [console_scripts]
    wssh = wizardwebssh.main:main
    ''',
    license='MIT',
    include_package_data=True,
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    install_requires=[
        'tornado>=4.5.0',
        'paramiko>=2.3.1',
    ],
)
