"""Provides functions for compilation of ROOT source files.

EXT_CXX: File extension of source files (default: .cxx).
EXT_H: File extension of header files (default: .h).
EXT_LINK: File extension of link definitions (default: _linkDef.hpp).
check: Check existence and age of compiled files.
make: Compile source files.
load: Load compiled files to ROOT.
require: Check compiled files and load them to ROOT.
"""

from datetime import datetime
from os import remove, stat
from os.path import exists
from subprocess import call

from ROOT import gROOT, gSystem

EXT_CXX = '.cxx'
EXT_H = '.h'
EXT_LINK = '_linkDef.hpp'

def check(path, filename):
    """Checks whether compiled file exists and is older than source file.

    path: Path of source files (without trailing slash).
    filename: Name of source files without file extension.
    """
    if not exists('{0}/{1}.so'.format(path, filename)):
        return False
    compiled = stat('{0}/{1}.so'.format(path, filename)).st_mtime
    source = stat('{0}/{1}{2}'.format(path, filename, EXT_CXX)).st_mtime
    return compiled > source

def make(path, filename):
    """Compile ROOT source files.

    path: Path of source files (without trailing slash).
    filename: Name of source files without file extension.
    """
    commands = [
        '#!/bin/bash',
        'cd {0}',
        'g++ -fPIC -O2 `root-config --libs --cflags` -L ${{ROOFITSYS}}/lib '
        '-L RooFitCore -l RooFit -lz -I ${{ROOFITSYS}}/include -c {1}{2}',
        'rootcint -v4 -f {1}_Dict.cc -c -fPIC `root-config --cflags` -I./ '
        '-I${{ROOFITSYS}}/include {1}{3} {1}{4}',
        'g++ -fPIC -O2 `root-config --libs --cflags` -L ${{ROOFITSYS}}/lib '
        '-L RooFitCore -l RooFit -lz -I ${{ROOFITSYS}}/include -c {1}_Dict.cc',
        'g++ -fPIC -O2 `root-config --libs --cflags` -L ${{ROOFITSYS}}/lib '
        '-L RooFitCore -l RooFit -lz --shared -o {1}.so {1}.o {1}_Dict.o'
    ]
    commands = '\n'.join(commands)
    commands = commands.format(path, filename, EXT_CXX, EXT_H, EXT_LINK)
    temp = 'temp_{0}.sh'.format(datetime.now().strftime('%H%M%S')
    with open(temp, 'w') as f:
        f.write(commands)
    call('bash {0}'.format(temp), shell=True)
    remove(temp)

def load(path, filename):
    """Import compiled files to ROOT.

    path: Path of source files (without trailing slash).
    filename: Name of source files without file extension.
    """
    gROOT.ProcessLine('.L {0}/{1}{2}'.format(path, filename, EXT_H))
    gSystem.Load('{0}/{1}.so'.format(path, filename))

def require(path, filename):
    """Check for compiled files (compile otherwise) and import them.

    path: Path of source files (without trailing slash).
    filename: Name of source files without file extension.
    """
    if not check(path, filename):
        make(path, filename)
    load(path, filename)
