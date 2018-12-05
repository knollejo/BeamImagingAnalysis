from json import dump, load
from os import mkdir
from os.path import exists
from sys import argv

from lib.io import BareRootFile, NamedString, Timestamp
from lib.prepare import make_trees

# qualities = ('vtx_isGood', '!vtx_isFake')
qualities = ('goodVertex', 'vtx_isValid', '!vtx_isFake')

def prepare_trees(
    configfile, outputpath, mintrk=0, verbose=False, scans=None,
    noerror=False
):
    if scans is None:
        scans = ('1X', '1Y', '2X', '2Y')
    with open(configfile) as f:
        config = load(f)
    fill = config['fill']
    version = config['version']
    bcids = config['bcids']
    name = 'Fill{0}_{1}'.format(fill, version)
    for scan in scans:
        print '<<< Prepare scan files: {0}'.format(scan)
        filelist = config['scan{0}MoveFiles'.format(scan)]
        begin = config['scan{0}MoveBegin'.format(scan)]
        end = config['scan{0}MoveEnd'.format(scan)]
        times = zip(begin, end)
        trees = make_trees(filelist, times, bcids, mintrk, verbose, noerror, qualities)
        filename = '{0}/{1}_{2}.root'.format(outputpath, name, scan)
        with BareRootFile(filename, 'RECREATE') as f:
            for tree in trees.itervalues():
                nam = tree.GetName()
                treename = 'Beam{0}Move{1}_{2}'.format(scan[0], scan[1], nam)
                tree.SetName(treename)
                tree.Write(treename)
            Timestamp().Write()
            NamedString('name', name).Write()
            NamedString('scan', scan).Write()

def main():
    if len(argv) < 2 or not argv[1] or not exists(argv[1]):
        raise RuntimeError('Specify 1st argument: JSON config file.')
    configfile = argv[1]
    if len(argv) < 3 or not argv[2] or not exists(argv[2]):
        raise RuntimeError('Specify 2nd argument: Output directory.')
    outputpath = argv[2]
    if outputpath.endswith('/'):
        outputpath = outputpath[:-1]
    if len(argv) < 4 or not argv[3] or argv[3] not in ('1X', '1Y', '2X', '2Y'):
        scans = None
        noerror = len(argv)>3 and argv[3] and argv[3].upper() == 'NOERROR'
    else:
        scans = [scan for scan in argv[3:] if scan in ('1X', '1Y', '2X', '2Y')]
        noerror = 'NOERROR' in map(str.upper, argv[3:])
    prepare_trees(
        configfile, outputpath, mintrk=6, verbose=True, scans=scans,
        noerror=noerror
    )

if __name__ == '__main__':
    main()
