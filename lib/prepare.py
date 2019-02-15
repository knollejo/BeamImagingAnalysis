"""Provides function for preparation of Beam Imaging data.

make_filelist: Scan raw files for needed data.
make_trees: Create Beam Imaging trees from raw data.
make_histograms: Create Beam Imaging histograms from created trees.
"""

from os import listdir, stat
from os.path import exists

from ROOT import gDirectory, TFile, TH1F, TH2F

from lib.io import RootChain, RootTree

def make_filelist(
    directories, times, treename='lumi/tree', timestamp='timeStamp_begin',
    verbose=True
):
    """Scan raw files for data belonging to Beam Imaging scans.

    directories: List of directory paths (string) to be searched.
    times: Dictionary with scan names and 2-tuples (begin & end timestamp).
    treename: Name of the tree that contains the data.
    timestamp: Name of the tree's branch that contains the time.
    returns dictionary with scan names and filelists (list of strings).
    """
    filelist = {scan: [] for scan in times}
    for directory in directories:
        if verbose:
            print '<<< Enter directory: {0}'.format(directory)
        files = [
            f for f in listdir(directory) if f.endswith('.root')
            if stat('{0}/{1}'.format(directory, f)).st_size > 0.0
        ]
        for filename in files:
            tfile = TFile('{0}/{1}'.format(directory, filename))
            if not tfile:
                continue
            tree = tfile.Get(treename)
            if not tree:
                continue
            for scan, (begin, end) in times.iteritems():
                n = tree.GetEntries(
                    '{0}>={1} && {0}<={2}'.format(timestamp, begin, end)
                )
                if n > 0:
                    filelist[scan].append(
                        '{0}/{1}'.format(directory, filename)
                    )
    return filelist

def make_trees(
    filelist, times, bcids, mintrk=0, verbose=True, noerror=False,
    qualities=None
):
    """Run over raw data and collect Beam Imaging data in trees.

    filelist: List of files (string) to be searched.
    times: List of 2-tuples (begin & end timestamp of scan steps).
    bcids: List of bunch crossings (int).
    mintrk: Minimal number of tracks (int) for the event selection (default: 0).
    verbose: Set true to print progress to stdout.
    noerror: Set true to not compute resolutions.
    qualities: tuple of boolean fields that are required.
    returns list of ROOT trees.
    """
    chain = RootChain('lumi/tree')
    chain.add_files(filelist)
    chain.add_fields([
        ('nVtx', 'i', 1),
        ('vtx_nTrk', 'i', 200),
        ('vtx_x', 'f', 200),
        ('vtx_y', 'f', 200),
        ('timeStamp_begin', 'I', 1)
    ])
    if 0 not in bcids:
        chain.add_fields([('bunchCrossing', 'i', 1),])
    if not noerror:
        chain.add_fields([
            ('vtx_xError', 'f', 200),
            ('vtx_yError', 'f', 200),
        ])
    if qualities is None:
        qualities = ('vtx_isGood', '!vtx_isFake')
    for quality in qualities:
        chain.add_fields([(quality if quality[0]!='!' else quality[1:], 'b', 200),])
    trees = {b: RootTree('bunch{0}Add'.format(b)) for b in bcids}
    for tree in trees.itervalues():
        tree.branch_f('vtx_x')
        tree.branch_f('vtx_y')
        tree.branch_f('vtx_xError')
        tree.branch_f('vtx_yError')
        tree.branch_f('vtx_nTrk')
        tree.branch_i('scanstep')
        tree.branch_i('timestamp')
    for event in chain.events(verbose):
        if event['nVtx'] <= 0:
            continue
        if -1 not in bcids:
            bcid = event['bunchCrossing']
            if bcid not in bcids:
                continue
        else:
            bcid = -1
        for scanstep, (begin, end) in enumerate(times):
            if event['timeStamp_begin'] <= begin:
                continue
            if event['timeStamp_begin'] >= end:
                continue
            break
        else:
            continue
        trees[bcid].set('scanstep', scanstep)
        trees[bcid].set('timestamp', event['timeStamp_begin'])
        for vtx in range(event['nVtx']):
            for quality in qualities:
                if quality[0]!='!':
                    if not event[quality][vtx]:
                        continue
                else:
                    if event[quality[1:]][vtx]:
                        continue
            if event['vtx_nTrk'][vtx] < mintrk:
                continue
            trees[bcid].set('vtx_x', event['vtx_x'][vtx])
            trees[bcid].set('vtx_y', event['vtx_y'][vtx])
            trees[bcid].set('vtx_xError', 0.0 if noerror else event['vtx_xError'][vtx])
            trees[bcid].set('vtx_yError', 0.0 if noerror else event['vtx_yError'][vtx])
            trees[bcid].set('vtx_nTrk', event['vtx_nTrk'][vtx])
            trees[bcid].Fill()
    return trees

def make_histograms(
    trees, nbins, mintrk, scaling=1.0, verbose=False, extracond=None
):
    """Run over created trees and select Beam Imaging data for histograms.

    trees: Dictionary of trees to be used for histogram creation (key unused).
    nbins: Number of bins in each dimension.
    mintrk: Minimal number of tracks (int) for the event selection.
    scaling: Float by which the histograms are rescaled (x=xraw/scaling).
    extracond: Additional condition to be applied to selected data.
    returns dictionary with histograms.
    """
    if extracond is None:
        extracond = ''
    else:
        extracond = ' && ({0})'.format(extracond)
    hists = {}
    for i, tree in enumerate(trees.itervalues()):
        name = 'hist_{0}'.format(tree.GetName())
        condition = 'vtx_nTrk>={0}{1}'.format(mintrk, extracond)

        draw1 = 'vtx_y/{0}:vtx_x/{0}>>hnew{1}'.format(scaling, i)
        n = tree.Draw(draw1, condition, 'goff')
        hist1 = gDirectory.Get('hnew{0}'.format(i))

        offx = round(hist1.GetMean(1), 2)
        offy = round(hist1.GetMean(2), 2)
        if verbose:
            print '<<< {0} entries with offset {1}, {2}'.format(n, offx, offy)

        draw2 = 'vtx_y/{0}-{1}:vtx_x/{0}-{2}>>{3}' \
                .format(scaling, offy, offx, name)
        hist2 = TH2F(name, name, nbins, -10.0, 10.0, nbins, -10.0, 10.0)
        tree.Draw(draw2, condition, 'goff')

        hists[name] = hist2
    return hists

def make_vdmhistos(
    trees, nbins, mintrk, stepsize,
    scaling=1.0, crange=(-10.0, 10.0), verbose=False
):
    """Run over created trees, select VdM data and use it for BI histograms.

    trees: Dictionary of trees to be used for histogram creation (key unused).
    nbins: Number of bins in each dimension.
    mintrk: Minimal number of tracks (int) for the event selection.
    stepsize: 2-tuple of step sizes of beam that is supposed to rest.
    scaling: Float by which the histograms are rescaled (x=xraw/scaling).
    crange: 2-tuple of limits of the coordinates.
    returns dictionary with histograms.
    """
    hists = {}
    for i, tree in enumerate(trees.itervalues()):
        name = 'hist_{0}'.format(tree.GetName())
        condition = 'vtx_nTrk>={0}'.format(mintrk)#' && scanstep>=2'

        if 'MoveX' in name:
            draw1 = '(vtx_y{2:+f}*scanstep)/{0}:(vtx_x{1:+f}*scanstep)/{0}>>hnew{3}' \
                    .format(scaling, -1.0*stepsize[0], -1.0*stepsize[1], i)
        else:
            draw1 = '(vtx_y{2:+f}*scanstep)/{0}:(vtx_x{1:+f}*scanstep)/{0}>>hnew{3}' \
                    .format(scaling, -1.0*stepsize[0], -1.0*stepsize[1], i)
        n = tree.Draw(draw1, condition, 'goff')
        hist1 = gDirectory.Get('hnew{0}'.format(i))

        offx = round(hist1.GetMean(1), 2)
        offy = round(hist1.GetMean(2), 2)
        if verbose:
            print '<<< {0} entries with offset {1}, {2}'.format(n, offx, offy)

        if 'MoveX' in name:
            draw2 = '(vtx_y)/{0}{1:+f}:(vtx_x{2:+f}*scanstep)/{0}{3:+f}>>{4}' \
                    .format(scaling, -1.0*offy, -1.0*stepsize[0], -1.0*offx, name)
        else:
            draw2 = '(vtx_y{0:+f}*scanstep)/{1}{2:+f}:(vtx_x)/{1}{3:+f}>>{4}' \
                    .format(-1.0*stepsize[1], scaling, -1.0*offy, -1.0*offx, name)
        hist2 = TH2F(
            name, name, nbins, crange[0], crange[1], nbins, crange[0], crange[1]
        )
        tree.Draw(draw2, condition, 'goff')

        hists[name] = hist2
    return hists
