from json import load
from os.path import exists
from sys import argv

from ROOT import RooFit

from lib.correction import compute_correction
from lib.fit import (
    compute_chisq, data_hist, fit, model_hist_fast as model_hist,
    overlap_variations, residual_hist
)
from lib.io import BareRootFile, NamedFloat, NamedString, RootFile, Timestamp
from lib.shape.dg import DoubleGaussFit, SuperGaussFit
from lib.shape.sg import SingleGauss, SingleGaussUncorrelated
from lib.shape.tg import SuperDoubleGaussFit, TripleGaussFit

def fit_shape(
    model, bcid, datafile, name, nbins, vtxresx,
    vtxresy=None, scaling=1.0, heavyion=False
):
    if heavyion:
        parameters = model.load_json(
            parameterfile='res/shapes/{}hi.json'.format(model.name())
        )
        crange = (-20.0, 20.0)
    else:
        parameters = model.load_json()
        crange = (-10.0, 10.0)
    if vtxresy is None:
        vtxresy = vtxresx
    model.set_vtxres(vtxresx / scaling, vtxresy / scaling)

    hists = []
    with BareRootFile(datafile) as f:
        for histname in [
            'hist_Beam2MoveX_bunch{0}Add', 'hist_Beam2MoveY_bunch{0}Add',
            'hist_Beam1MoveX_bunch{0}Add', 'hist_Beam1MoveY_bunch{0}Add'
        ]:
            hist = f.Get(histname.format(bcid))
            hist.SetDirectory(0)
            hists.append(hist)

    fitmethod = lambda pdf, data: pdf.fitTo(
        data, RooFit.Save(), RooFit.PrintLevel(1), RooFit.Verbose(0)
    )

    result, modfuncs, datahist = fit(model, hists, fitmethod)

    hdata = data_hist(model.xvar(), model.yvar(), datahist)
    hmodel = model_hist(model.xvar(), model.yvar(), modfuncs)
    chisqs, dofs = compute_chisq(hmodel, hdata)

    true, avg, rms = overlap_variations(model)

    scDat, scMod, scRes = residual_hist(hdata, hmodel, scaling, crange=crange)

    model.factor = 100.0
    corrTree = compute_correction(model.overlap_func())

    outputname = 'BeamImaging_v1_{0}_{1}_bcid{2}' \
                 .format(name, model.name(), bcid)
    with RootFile(outputname, 'RECREATE') as f:
        result.Write('fitResult')
        for hist in scDat + scMod + scRes:
            hist.Write()
        corrTree.Write()
        for i, scan in enumerate(('X1', 'Y1', 'X2', 'Y2')):
            NamedFloat('chisq{0}'.format(scan), chisqs[i]).Write()
            NamedFloat('dof{0}'.format(scan), dofs[i]).Write()
        NamedFloat('overlap_true', true).Write()
        NamedFloat('overlap_average', avg).Write()
        NamedFloat('overlap_rms', rms).Write()
        NamedFloat('scaling', scaling).Write()
        Timestamp().Write()
        NamedString('name', outputname).Write()
        f.mkdir('initial').cd()
        for par in parameters:
            par.Write()
        f.mkdir('final').cd()
        for par in model.parameters():
            NamedFloat(par.GetName(), par.val()).Write()
            NamedFloat(
                '{0}_error'.format(par.GetName()), par.err(model.parameter)
            ).Write()

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
    name = config['name']
    if 'heavyion' in config and config['heavyion']:
        heavyion = True
        crange = (-20.0, 20.0)
    else:
        heavyion = False
        crange = (-10.0, 10.0)
    model = {
        'SG': SingleGauss, 'DG': DoubleGaussFit, 'TG': TripleGaussFit,
        'SupG': SuperGaussFit, 'SupDG': SuperDoubleGaussFit,
        'noCorr': SingleGaussUncorrelated
    }[argv[3]](crange=crange)
    datafile = '{0}/{1}.root'.format(config['datapath'], config['dataname'])
    nbins = config['nbins']
    vtxresx = config['vtxresx']
    vtxresy = config['vtxresy']
    scaling = config['scaling']
    fit_shape(
        model, bcid, datafile, name, nbins, vtxresx,
        vtxresy=vtxresy, scaling=scaling, heavyion=heavyion
    )

if __name__ == '__main__':
    main()
