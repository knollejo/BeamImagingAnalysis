from json import load
from os.path import exists
from sys import argv

from ROOT import TH1F

from lib.correction import compute_correction
from lib.io import copy_directory, NamedFloat, RootFile, Timestamp
from lib.shape.dg import DoubleGaussFit, SuperGaussFit
from lib.shape.sg import SingleGauss, SingleGaussUncorrelated
from lib.shape.tg import SuperDoubleGaussFit, TripleGaussFit

def compute_corr(model, bcid, inputfile):
    model.load_root(inputfile)
    model.factor = 100.0
    overlap = model.overlap_func()
    corrTree = compute_correction(overlap, n=1000)
    overlapFit = TH1F('overlap_fit', 'fitted overlap integral', 1000, -0.5, 0.5)
    overlapDiff = TH1F('overlap_diff', 'correction factor', 1000, -0.5, 0.5)
    corrTree.Draw('overlapFit>>overlap_fit', '', 'goff')
    corrTree.Draw('overlapDiff>>overlap_diff', '', 'goff')
    #overlapTrue, result_fit, result_dif = compute_correction(
    #    overlap, n=50, extended=False
    #)
    #overlapDiff = sum(result_dif)/len(result_dif)
    with RootFile(inputfile) as old, RootFile(inputfile, 'RECREATE') as new:
        condition = lambda key: not key.GetName().startswith('corr') and \
                    key.GetName() not in ['overlap_fit', 'overlap_diff']
        copy_directory(new, old, condition=condition)
        new.cd()
        corrTree.Write()
        overlapFit.Write()
        overlapDiff.Write()
        #NamedFloat('overlap_diff', overlapDiff).Write()
        Timestamp('corrTimestamp').Write()

def compute_corr_randomized(model, bcid, inputfile):
    model.load_root(inputfile)
    model.factor = 100.0
    overlap = model.overlap_func()
    def eachtoy(simulator, rand):
        return model.assign_overlap(simulator, random=rand)
    corrTree = compute_correction(overlap, n=1000, eachtoy=eachtoy)
    overlapFit = TH1F('rndmzd_ovfit', 'fitted overlap integral', 1000, -0.5, 0.5)
    overlapDiff = TH1F('rndmzd_ovdiff', 'correction factor', 1000, -0.5, 0.5)
    corrTree.Draw('overlapFit>>rndmzd_ovfit', '', 'goff')
    corrTree.Draw('overlapDiff>>rndmzd_ovdiff', '', 'goff')
    with RootFile(inputfile) as old, RootFile(inputfile, 'RECREATE') as new:
        condition = lambda key: not key.GetName().startswith('rndmzd')
        copy_directory(new, old, condition=condition)
        new.cd()
        corrTree.SetName('rndmzd_corrTree')
        corrTree.Write()
        overlapFit.Write()
        overlapDiff.Write()
        Timestamp('rndmzdTimestamp').Write()

fitmodels = ('noCorr', 'SG', 'DG', 'TG', 'SupG', 'SupDG')

def main():
    if len(argv) < 2 or not argv[1] or not exists(argv[1]):
        raise RuntimeError('Specify 1st argument: JSON config file.')
    with open(argv[1]) as f:
        config = load(f)
    if len(argv) < 3 or not argv[2] or int(argv[2]) not in config['bcids']:
        raise RuntimeError('Specify 2nd argument: a valid BCID.')
    bcid = int(argv[2])
    if len(argv) < 4 or not argv[3] or argv[3] not in fitmodels:
        raise RuntimeError(
            'Specify 3rd argument: Fit model ({0}).' \
            .format(', '.join(fitmodels))
        )
    if 'heavyion' in config and config['heavyion']:
        crange = (-20.0, 20.0)
    else:
        crange = (-10.0, 10.0)
    model = {
        'SG': SingleGauss, 'DG': DoubleGaussFit, 'TG': TripleGaussFit,
        'SupG': SuperGaussFit, 'SupDG': SuperDoubleGaussFit,
        'noCorr': SingleGaussUncorrelated
    }[argv[3]](crange=crange)
    if len(argv) < 5 or not argv[4] or argv[4] not in ['v2', 'v3', 'v4']:
        version = 'v1'
    else:
        version = argv[4]
    name = config['name']
    if version in ('v3', 'v4'):
        name = '{0}_best'.format(name)
    inputfile = 'BeamImaging_{0}_{1}_{2}_bcid{3}' \
                .format(version, name, model.name(), bcid)
    if (
        (len(argv) >= 5 and argv[4] and argv[4] == '-r') or
        (len(argv) >= 6 and argv[5] and argv[5] == '-r')
    ):
        compute_corr_randomized(model, bcid, inputfile)
    else:
        compute_corr(model, bcid, inputfile)

if __name__ == '__main__':
    main()
