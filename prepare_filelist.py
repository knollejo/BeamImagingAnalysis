from json import dump, load
from os import mkdir
from os.path import exists
from sys import argv

from lib.prepare import make_filelist

def prepare_filelist(configfile, verbose=False):
    with open(configfile) as f:
        config = load(f)
    directories = [
        '{0}/{1}'.format(config['sourcepath'], d) for d in config['sourcedirs']
    ]
    fill = config['fill']
    version = config['version']
    times = {
        '1X': (config.get('scan1XMoveBegin_Early', config['scan1XMoveBegin'])[0], \
               config.get('scan1XMoveEnd_Late', config['scan1XMoveEnd'])[-1]),
        '1Y': (config.get('scan1YMoveBegin_Early', config['scan1YMoveBegin'])[0], \
               config.get('scan1YMoveEnd_Late', config['scan1YMoveEnd'])[-1]),
        '2X': (config.get('scan2XMoveBegin_Early', config['scan2XMoveBegin'])[0], \
               config.get('scan2XMoveEnd_Late', config['scan2XMoveEnd'])[-1]),
        '2Y': (config.get('scan2YMoveBegin_Early', config['scan2YMoveBegin'])[0], \
               config.get('scan2YMoveEnd_Late', config['scan2YMoveEnd'])[-1])
    }
    filelist = make_filelist(directories, times, verbose=verbose)
    output = {
        'fill': fill,
        'version': version,
        'bcids': config['bcids'],
        'heavyion': bool('heavyion' in config and config['heavyion']),
        'scan1XMoveFiles': filelist['1X'],
        'scan1YMoveFiles': filelist['1Y'],
        'scan2XMoveFiles': filelist['2X'],
        'scan2YMoveFiles': filelist['2Y'],
        'scan1XMoveBegin': config['scan1XMoveBegin'],
        'scan1XMoveEnd': config['scan1XMoveEnd'],
        'scan1YMoveBegin': config['scan1YMoveBegin'],
        'scan1YMoveEnd': config['scan1YMoveEnd'],
        'scan2XMoveBegin': config['scan2XMoveBegin'],
        'scan2XMoveEnd': config['scan2XMoveEnd'],
        'scan2YMoveBegin': config['scan2YMoveBegin'],
        'scan2YMoveEnd': config['scan2YMoveEnd']
    }
    filename = 'res/list/Fill{0}_{1}.json'.format(fill, version)
    if not exists('res'):
        mkdir('res')
    if not exists('res/list'):
        mkdir('res/list')
    with open(filename, 'w') as f:
        dump(output, f, indent=4, separators=(',',': '))
    return filename

def main():
    if len(argv) < 2 or not argv[1]:
        raise RuntimeError('Specify a filename as command-line argument.')
    if not exists(argv[1]):
        raise RuntimeError('Specify an existing file.')
    prepare_filelist(argv[1], verbose=True)

if __name__ == '__main__':
    main()
