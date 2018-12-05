from json import load
from os.path import exists
from re import match
from sys import argv

from ROOT import RooFit, TRandom3

from lib.correction import compute_correction
from lib.fit import (
    compute_chisq, data_hist, fit, model_hist_fast as model_hist,
    overlap_variations, residual_hist
)
from lib.io import BareRootFile, NamedFloat, NamedString, RootFile, Timestamp
from lib.shape.tg import SuperDoubleGaussFit

def fit_shape(
    model, bcid, datafile, inputfile, name, nbins, vtxresx,
    vtxresy=None, scaling=1.0, heavyion=False
):
    rand = TRandom3()
    rand.SetSeed(0)

    if heavyion:
        parameters = model.load_json(
            parameterfile='res/shapes/{}hi.json'.format(model.name()),
            random=rand
        )
        crange = (-20.0, 20.0)
    else:
        parameters = model.load_json(random=rand)
        crange = (-10.0, 10.0)
    with RootFile(inputfile) as f:
        for par in model.parameters():
            if par.is_formula():
                continue
            parname = par.GetName()
            if match('^[xy]0[12][12]$', parname):
                value = f.get_val('final/{0}'.format(parname))
                par.setVal(value)
                par.setConstant(True)
                parameters.append(
                    NamedFloat('{0}_const'.format(parname), value)
                )
                continue
            if match('^omega[12]$', parname):
                value = f.get_val('final/{0}'.format(parname))
                value = rand.Uniform(max(value*0.9, 0.0), min((
                    value*1.1, 0.99, f.get_val('final/{0}Max'.format(parname)),
                )))
                par.setVal(value)
                parameters.append(
                    NamedFloat('{0}_ini'.format(parname), value)
                )
                continue
            if match('^rho[NM][12]$', parname):
                value = f.get_val('final/{0}'.format(parname))
                value = rand.Uniform(max(value-0.1, -0.9), min(value+0.1, 0.9))
                lo, hi = max(value-0.1, -0.9), min(value+0.1, 0.9)
            elif match('^[xy]WidthM[12]$', parname):
                value = f.get_val('final/{0}'.format(parname))
                value = rand.Uniform(value*0.9, value*1.1)
                lo, hi = value*0.9, value*1.1
            elif match('^[xy]WidthN[12]Ratio$', parname):
                value = f.get_val('final/{0}'.format(parname))
                value = rand.Uniform(max(value*0.9, 0.1), min(value*1.1, 0.99))
                lo, hi = max(value*0.9, 0.1), min(value*1.1, 0.99)
            else:
                continue
            par.setRange(lo, hi)
            par.setVal(value)
            for p in parameters:
                if p.GetName() == '{0}_min'.format(parname):
                    p.SetVal(lo)
                if p.GetName() == '{0}_max'.format(parname):
                    p.SetVal(hi)
                if p.GetName() == '{0}_ini'.format(parname):
                    p.SetVal(value)
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

    outputname = 'BeamImaging_v4_{0}_{1}_bcid{2}' \
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

def main():
    if len(argv) < 2 or not argv[1] or not exists(argv[1]):
        raise RuntimeError('Specify 1st argument: JSON config file.')
    with open(argv[1]) as f:
        config = load(f)
    if len(argv) < 3 or not argv[2] or int(argv[2]) not in config['bcids']:
        raise RuntimeError('Specify 2nd argument: a valid BCID.')
    bcid = int(argv[2])
    if len(argv) < 4 or not argv[3] or argv[3] not in ('SupDG',):
        raise RuntimeError('Specify 3rd argument: Fit model (SupDG).')
    if 'heavyion' in config and config['heavyion']:
        heavyion = True
        crange = (-20.0, 20.0)
    else:
        heavyion = False
        crange = (-10.0, 10.0)
    model = {
        'SupDG': SuperDoubleGaussFit
    }[argv[3]](crange=crange)
    if len(argv) < 5 or not argv[4]:
        raise RuntimeError('Specify 4th argument: Unique name.')
    namepart = argv[4]
    name = config['name']
    datafile = '{0}/{1}.root'.format(config['datapath'], config['dataname'])
    inputfile = 'BeamImaging_v2_{0}_{1}_bcid{2}'.format(
        name, {'SupDG': 'SupG'}[argv[3]], bcid
    )
    nbins = config['nbins']
    vtxresx = config['vtxresx']
    vtxresy = config['vtxresy']
    scaling = config['scaling']
    name = '{0}_{1}'.format(name, namepart)
    fit_shape(
        model, bcid, datafile, inputfile, name, nbins, vtxresx,
        vtxresy=vtxresy, scaling=scaling, heavyion=heavyion
    )

if __name__ == '__main__':
    main()
