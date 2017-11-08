"""Provides classes for file input and output.

BareRootFile: Open ROOT files.
RootFile: Open ROOT files in results directory.
RootTree: Create and fill ROOT trees.
RootChain: Open ROOT trees in a chain.
NamedString: Create and write a string value.
NamedFloat: Create and write a float value.
Timestamp: Create and write a timestamp.
copy_directory: Writes all objects in directory to new directory.
"""

from array import array
from datetime import datetime
from os import listdir, mkdir
from os.path import exists
from re import IGNORECASE, match
from time import strftime, sleep

from ROOT import gROOT, TChain, TDirectory, TFile, TNamed, TParameter, TTree

if not exists('results'):
    mkdir('results')

class BareRootFile(TFile):
    """Read from and write to ROOT files.

    __init__: Initialize and open file.
    __enter__: Return file on with-opening.
    __exit__: Close file on with-end.
    close: Close file.
    get: Get object from file.
    get_val: Get value of object from file.
    """

    def __init__(self, filename, mode='READ'):
        """Initialize and open a file.

        filename: Filename to be opened.
        mode: One out of READ and RECREATE.
        get: Read object from file.
        """
        if match('^READ$', mode, IGNORECASE):
            print '<<< Open {0}'.format(filename)
        else:
            print '<<< Write to {0}'.format(filename)
        TFile.__init__(self, filename, mode)
        self.filename = filename

    def __enter__(self):
        """Returns file object on use in with-statement."""
        return self

    def __exit__(self, ex_type, ex_value, ex_traceback):
        """Closes file object on end of with-statement."""
        value = self.close()
        if ex_type is None:
            return value
        else:
            return False

    def close(self):
        """Close the file and return the filename."""
        self.Close()
        return self.filename

    def get(self, objectname):
        """Read object from file and move it to current directory."""
        obj = self.Get(objectname)
        if obj:
            try:
                obj.SetDirectory(0)
            except AttributeError:
                pass
        else:
            msg = 'BareRootFile: Failed to load object {0} from file {1}!' \
                  .format(objectname, self.filename)
            raise NameError(msg)
        return obj

    def get_val(self, objectname):
        """Read value of object from file."""
        obj = self.Get(objectname)
        if obj:
            try:
                return obj.GetVal()
            except AttributeError:
                pass
            try:
                return obj.GetTitle()
            except AttributeError:
                pass
            msg = 'BareRootFile: Object {0} in file {1} has no value!' \
                  .format(objectname, self.filename)
            raise ValueError(msg)
        else:
            msg = 'BareRootFile: Failed to read from object {0} in file {1}!' \
                  .format(objectname, self.filename)
            raise NameError(msg)

class RootFile(BareRootFile):
    """Read from and write to ROOT files in the results/ directory.

    __init__: Initialize and open file.
    generate_name: Get name for new results file.
    find_file: Get name of latest results file.
    """

    def __init__(self, name, mode='READ'):
        """Initialize and open a file.

        name: (Part of) filename to be opened.
        mode: One out of READ and RECREATE.
        """
        if match('^READ$', mode, IGNORECASE):
            filename = self.find_file(name)
        else:
            filename = self.generate_name(name)
        BareRootFile.__init__(self, filename, mode)

    @staticmethod
    def generate_name(name):
        """Generate a filename for results using the current timestamp."""
        filename = 'results/{}_{}.root'.format(name, strftime('%y%m%d_%H%M%S'))
        return filename

    @staticmethod
    def _find_file(name):
        """Find the most recent results file containing the argument."""
        results = False
        count = 0
        while not results:
            try:
                results = listdir('results')
            except OSError as e:
                count += 1
                print '<<< Error ({0}) {1}: {2}'.format(count, e.errno, e)
                if count < 1000:
                    sleep(0.1)
                    results = False
                else:
                    msg = 'RootFile: Failed to do listdir 1000-times!'
                    raise OSError(msg)
        files = [f for f in results if match('^{0}'.format(name), f)]
        files.sort(reverse=True)
        for f in files:
            if exists('results/{0}'.format(f)):
                return 'results/{0}'.format(f)
        else:
            return None

    @staticmethod
    def find_file(name):
        """Find the most recent results file containing the argument."""
        if name.startswith('results/'):
            name = name[8:]
        if name.endswith('.root'):
            if exists('results/{0}'.format(name)):
                return 'results/{0}'.format(name)
            else:
                name = name[:-5]
        result = RootFile._find_file(name)
        if result is None:
            msg = 'RootFile: File "{0}" not found!'.format(name)
            raise IOError(msg)
        else:
            return result

class RootTree(TTree):
    """Create and fill ROOT trees.

    __init__: Initialize a tree.
    branch_f: Add a branch containing a float.
    branch_i: Add a branch containing an integer.
    set: Set the value of a branch.
    """

    def __init__(self, name, title=None):
        """Initialize the tree."""
        if title is None:
            title = name
        TTree.__init__(self, name, title)
        self._fields = {}

    def _branch(self, name, type1, type2, ini, dim):
        """Add a new branch.

        name: Name of the branch.
        type1: Data type of the array object that stores the values.
        type2: Data type of the TTree branch.
        ini: Initial value.
        dim: Number of entries in the branch.
        """
        self._fields[name] = array(type1, [ini]*dim)
        if dim > 1:
            form = '{0}[{1}]/{2}'.format(name, dim, type2)
        else:
            form = '{0}/{1}'.format(name, type2)
        self.Branch(name, self._fields[name], form)

    def branch_f(self, name, dim=1):
        """Add a branch of data type float."""
        self._branch(name, 'f', 'F', 0.0, dim)

    def branch_i(self, name, dim=1):
        """Add a branch of data type int."""
        self._branch(name, 'i', 'I', 0, dim)

    def set(self, name, value, index=0):
        """Set the value of a branch."""
        self._fields[name][index] = value

class RootChain(TChain):
    """Open ROOT trees in a chain.

    __init__: Initialize chain.
    add_files: Add list of files to chain.
    add_fields: Add list of fields to event output.
    events: Iterator over events.
    """
    def __init__(self, treename):
        """Initialize chain for specific tree."""
        TChain.__init__(self, treename)
        self._fields = {}

    def add_files(self, files):
        """Add list of files to chain."""
        for filename in files:
            self.Add(filename)

    def add_fields(self, fields):
        """Add list of fields to event output.

        fields: list of 3-tuples (name, type, multiplicity).
        """
        for (name, form, n) in fields:
            if form in ['i', 'I', 'b']:
                ini = 0
            else:
                ini = 0.0
            self._fields[name] = array(form, [ini]*n)
            self.SetBranchAddress(name, self._fields[name])

    def events(self, verbose=False):
        """Iterate over all events in the chain.

        verbose: Set true to print progress to stdout.
        Returns list of fields at each iteration.
        """
        nentries = self.GetEntries()
        ndisplay = nentries/100+1
        if verbose:
            print '<<< Start to process {0} events'.format(nentries)
        for i in range(nentries):
            if verbose and i%ndisplay == 0:
                print '<<< Now at event {0} of {1} ({2:.0f}%)' \
                      .format(i, nentries, i*100.0/nentries)
            self.GetEntry(i)
            event = {}
            for field, pointer in self._fields.iteritems():
                if len(pointer) == 1:
                    event[field] = pointer[0]
                else:
                    event[field] = [v for v in pointer]
            yield event

class NamedString(TNamed):
    """Create and write a string value."""

    def __init__(self, key, value):
        """Initialize a string value."""
        TNamed.__init__(self, key, value)

class NamedFloat(TParameter(float)):
    """Create and write a float value."""

    def __init__(self, key, value):
        """Initialize a float value."""
        TParameter(float).__init__(self, key, value)

class Timestamp(NamedString):
    """Create and write a timestamp."""

    def __init__(self, key=None):
        """Initialize a timestamp."""
        if key is None:
            key = 'timestamp'
        timestamp = datetime.now().strftime('%d.%m.%Y, %H:%M:%S')
        NamedString.__init__(self, key, timestamp)

    def __str__(self):
        return self.GetTitle()

def copy_directory(newdir, olddir, condition=None):
    """Reads all objects from olddir and writes them to newdir.

    newdir, olddir: Directories (inheriting from TDirectory).
    condition: Function that takes key name and returns whether the file should
        be kept or not (optional).
    """
    for key in olddir.GetListOfKeys():
        if condition is not None and (
            not condition(key) or key.GetName().startswith('ProcessID')
        ):
            continue
        cl = gROOT.GetClass(key.GetClassName())
        if not cl:
            continue
        if cl.InheritsFrom(TDirectory.Class()):
            newsub = newdir.mkdir(key.GetName())
            oldsub = olddir.GetDirectory(key.GetName())
            copy_directory(newsub, oldsub)
        elif cl.InheritsFrom(TTree.Class()):
            oldtree = olddir.Get(key.GetName())
            newdir.cd()
            newtree = oldtree.CloneTree(-1, 'fast')
            newtree.Write()
        else:
            olddir.cd()
            obj = key.ReadObj()
            newdir.cd()
            obj.Write(key.GetName())
            del obj
