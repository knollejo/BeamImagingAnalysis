from json import load
from os.path import exists
from sys import argv

from ROOT import RooArgList, RooDataHist

from lib.fit import compute_chisq, data_hist, model_hist, residual_hist
from lib.io import BareRootFile, copy_directory, NamedFloat, RootFile, Timestamp
from lib.shape.dg import DoubleGaussFit, SuperGaussFit
from lib.shape.sg import SingleGauss, SingleGaussUncorrelated
from lib.shape.tg import SuperDoubleGaussFit, TripleGaussFit

ic = [('1','X'),('1','Y'),('2','X'),('2','Y')]

def integrate_residuals(
    model, bcid, datafile, outputname, nbins, scaling=1.0, crange=None
):
    model.load_root(outputname)
    hists = []
    with BareRootFile(datafile) as f:
        for histname in [
            'hist_Beam2MoveX_bunch{0}Add', 'hist_Beam2MoveY_bunch{0}Add',
            'hist_Beam1MoveX_bunch{0}Add', 'hist_Beam1MoveY_bunch{0}Add'
        ]:
            hist = f.Get(histname.format(bcid))
            hist.SetDirectory(0)
            hists.append(hist)

    modfuncs = model.model_functions()
    datahist = [RooDataHist(
        'scan{0}Beam{1}RestDataHist'.format(c, i),
        'scan{0}Beam{1}RestDataHist'.format(c, i),
        RooArgList(model.xvar(), model.yvar()),
        hists[j]
    ) for j, (i,c) in enumerate(ic)]

    hdata = data_hist(model.xvar(), model.yvar(), datahist, nbins=nbins)
    hmodel = model_hist(
        model.xvar(), model.yvar(), modfuncs, nbins=nbins, crange=crange
    )
    chisqs, dofs = compute_chisq(hmodel, hdata, nbins=nbins)
    scDat, scMod, scRes = residual_hist(hdata, hmodel, scaling, crange=crange)

    with RootFile(outputname) as old, RootFile(outputname, 'RECREATE') as new:
        condition = lambda key: key.GetName() not in [
            'dataHistX1', 'dataHistY1', 'dataHistX2', 'dataHistY2',
            'modelHistX1', 'modelHistY1', 'modelHistX2', 'modelHistY2',
            'residualHistX1', 'residualHistY1', 'residualHistX2',
            'residualHistY2', 'chisqX1', 'chisqY1', 'chisqX2', 'chisqY2',
            'dofX1', 'dofY1', 'dofX2', 'dofY2',
        ]
        copy_directory(new, old, condition=condition)
        new.cd()
        for hist in scDat + scMod + scRes:
            hist.Write()
        for i, scan in enumerate(('X1', 'Y1', 'X2', 'Y2')):
            NamedFloat('chisq{0}'.format(scan), chisqs[i]).Write()
            NamedFloat('dof{0}'.format(scan), dofs[i]).Write()
        Timestamp('resTimestamp').Write()

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
    datafile = '{0}/{1}.root'.format(config['datapath'], config['dataname'])
    name = config['name']
    if version in ('v3', 'v4'):
        name = '{0}_best'.format(name)
    outputname = 'BeamImaging_{0}_{1}_{2}_bcid{3}' \
                 .format(version, name, model.name(), bcid)
    scaling = config['scaling']
    integrate_residuals(
        model, bcid, datafile, outputname, 95, scaling=scaling, crange=crange
    )

if __name__ == '__main__':
    main()
