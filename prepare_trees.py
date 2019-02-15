from json import dump, load
from os import mkdir
from os.path import exists
from sys import argv

from lib.io import BareRootFile, NamedString, Timestamp
from lib.prepare import make_trees

qualities = ('vtx_isGood', '!vtx_isFake')
# qualities = ('goodVertex', 'vtx_isValid', '!vtx_isFake')

def prepare_trees(
    configfile, outputpath, mintrk=0, verbose=False, scans=None,
    noerror=False, start=None
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
        basefilelist = config['scan{0}MoveFiles'.format(scan)]
        begin = config['scan{0}MoveBegin'.format(scan)]
        end = config['scan{0}MoveEnd'.format(scan)]
        times = zip(begin, end)
        if start is None:
            filelists = (('{0}/{1}_{2}.root'.format(outputpath, name, scan), basefilelist),)
        else:
            filelists = map(lambda (i, f): (
                '{0}/{1}_{2}_file{3}.root'.format(outputpath, name, scan, i), (f,)
            ), enumerate(basefilelist[start:], start=start))
        for i, (filename, filelist) in enumerate(filelists):
            print '<<< Now at filelist {0} of {1}'.format((0 if start is None else start)+i, len(filelists))
            trees = make_trees(filelist, times, bcids, mintrk, verbose, noerror, qualities)
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
    args = filter(lambda a: not a.startswith('-'), argv[3:])
    opts = map(lambda o: str.upper(o[1:]), filter(lambda a: a.startswith('-'), argv[3:]))
    if len(args)==0 or not args[0] or args[0] not in ('1X', '1Y', '2X', '2Y'):
        scans = None
    else:
        scans = filter(lambda scan: scan in ('1X', '1Y', '2X', '2Y'), args)
    noerror = 'NOERROR' in opts
    if filter(lambda o: o.startswith('S'), opts):
        try:
            start = int(filter(lambda o: o.startswith('S'), opts)[0][1:])
        except ValueError:
            raise RuntimeError('Usage: -s3 to start at 4th file.')
    else:
        start = None
    prepare_trees(
        configfile, outputpath, mintrk=6, verbose=True, scans=scans,
        noerror=noerror, start=start
    )

if __name__ == '__main__':
    main()
