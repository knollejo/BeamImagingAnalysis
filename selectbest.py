from os import remove
from os.path import commonprefix, exists
from sys import argv
from time import strftime

from lib.io import BareRootFile, copy_directory, RootFile, Timestamp

def selectbest(names, delete=False):
    prefix = commonprefix(names)
    if prefix[-1] == '_':
        prefix = prefix[:-1]
    morenames = [n[n.index('_', len(prefix)+1)+1:] for n in names]
    suffix = commonprefix(morenames)
    if suffix[-1] == '_':
        suffix = suffix[:-1]
    while suffix[suffix.rfind('_')+1:].isdigit():
        suffix = suffix[:suffix.rfind('_')]

    chisq, best = 1.0e9, None
    for name in names:
        with BareRootFile(name) as f:
            csq, dof = 0.0, 0
            for c in ('X1', 'Y1', 'X2', 'Y2'):
                csq += f.get_val('chisq{0}'.format(c))
                dof += f.get_val('dof{0}'.format(c))
            if csq/dof < chisq:
                chisq, best = csq/dof, name

    filename = '{0}_best_{1}_{2}.root' \
               .format(prefix, suffix, strftime('%y%m%d_%H%M%S'))
    with BareRootFile(best) as old, BareRootFile(filename, 'RECREATE') as new:
        condition = lambda key: not key.GetName().startswith('selected')
        copy_directory(new, old, condition=condition)
        new.cd()
        Timestamp('selectedTimestamp').Write()
    if delete:
        for name in names:
            remove(name)

def main():
    names = []
    delete = False
    for name in argv[1:]:
        if exists(name):
            names.append(name)
        elif name == '--delete':
            delete = True
        else:
            break
    if len(names) < 2:
        raise RuntimeError(
            'Specify arguments: at least two ROOT results files.'
        )
    selectbest(names, delete=delete)

if __name__ == '__main__':
    main()
