from json import load
from os.path import exists
from sys import argv
from re import match
from sys import argv

from ROOT import RooFit, TRandom3

from lib.closure import generate_toys
from lib.correction import compute_correction
from lib.fit import (
    compute_chisq, data_hist, fit, model_hist_fast as model_hist,
    overlap_variations, residual_hist
)
from lib.io import NamedFloat, NamedString, RootFile, RootTree, Timestamp
from lib.shape.dg import (
    DoubleGaussFit, DoubleGaussToy, SuperGaussFit, SuperGaussToy
)
from lib.shape.sg import SingleGauss
from lib.shape.tg import (
    SuperDoubleGaussFit, SuperDoubleGaussToy, TripleGaussToy
)

def do_closureTest(
    suffix, toymodel, tempmodel, fitmodel, inputfile, vtxresx, vtxresy=None
):
    toyparameters = toymodel.load_json(inputfile)
    tempparameters = tempmodel.load_json()
    fitparameters = fitmodel.load_json()

    if vtxresy is None:
        vtxresy = vtxresx
    toymodel.set_vtxres(vtxresx, vtxresy)
    tempmodel.set_vtxres(vtxresx, vtxresy)
    fitmodel.set_vtxres(vtxresx, vtxresy)

    fitmethod = lambda pdf, data: pdf.fitTo(
        data, RooFit.Save(), RooFit.PrintLevel(1), RooFit.Verbose(0)
    )

    name = 'ClosureTest_v3_{0}_{1}_{2}' \
           .format(toymodel.name(), fitmodel.name(), suffix)

    rand = TRandom3()
    rand.SetSeed(0)

    overlap = toymodel.overlap_func()
    hists, nevents = generate_toys(
        overlap, vtxresx, vtxresy=vtxresy, rand=rand, nbins=760#, verbose=True
    )

    toy_tru, toy_fit, toy_dif = \
        compute_correction(overlap, rand=rand, extended=False)
    mean = sum(toy_dif)/len(toy_dif)
    error = (sum([(d-mean)**2 for d in toy_dif])/len(toy_dif))**0.5

    tresult, tmodfuncs, tdatahist = fit(tempmodel, hists, fitmethod)
    tresult.SetName('temp_fitResult')
    tmodel = model_hist(tempmodel.xvar(), tempmodel.yvar(), tmodfuncs)
    tdata = data_hist(tempmodel.xvar(), tempmodel.yvar(), tdatahist)
    for hist in tmodel + tdata:
        hist.SetName('temp_{0}'.format(hist.GetName()))
    tchisqs, tdofs = compute_chisq(tmodel, tdata)

    for par in fitmodel.parameters():
        if par.is_formula():
            continue
        parname = par.GetName()
        if match('^[xy]0[12][12]$', parname):
            value = tempmodel.parameter(parname).val()
            par.setVal(value)
            par.setConstant(True)
            continue
        if match('^rho[MW][12]$', parname):
            value = tempmodel.parameter('rho{0}{1}'.format(
                {'M': 'N', 'W': 'M'}[parname[3]], parname[4])
            ).val()
            lo, hi = value-0.1, value+0.1
            if lo < -0.9:
                lo = -0.9
            if hi > 0.9:
                hi = 0.9
        elif match('^[xy]WidthM[12]$', parname):
            value = tempmodel.parameter('{0}WidthN{1}'.format(
                parname[0], parname[7]
            )).val()
            lo, hi = value*0.9, value*1.1
        elif match('^[xy]WidthW[12]Diff$', parname):
            value = tempmodel.parameter('{0}WidthM{1}Diff'.format(
                parname[0], parname[7]
            )).val()
            lo, hi = value*0.9, value*1.1
            if lo < 0.001:
                lo = 0.001
        elif match('^w[12]MFraction$', parname):
            value = tempmodel.parameter('w{0}N'.format(parname[1])).val()
            lo, hi = value-0.01, value+0.01
            if lo < 0.0:
                lo = 0.0
            if hi > 1.0:
                hi = 1.0
        else:
            continue
        par.setRange(lo, hi)
        par.setVal(value)
    result, modfuncs, datahist = fit(fitmodel, hists, fitmethod)
    result.SetName('fit_fitResult')
    hmodel = model_hist(fitmodel.xvar(), fitmodel.yvar(), modfuncs)
    hdata = data_hist(fitmodel.xvar(), fitmodel.yvar(), datahist)
    for hist in hmodel + hdata:
        hist.SetName('fit_{0}'.format(hist.GetName()))
    chisqs, dofs = compute_chisq(hmodel, hdata)

    ttrue, tavg, trms = overlap_variations(tempmodel)
    true, avg, rms = overlap_variations(fitmodel)

    crange = (-10.0, 10.0)
    stDat, stMod, stRes = residual_hist(tdata, tmodel, 1.0, crange=crange)
    for hist in stDat + stMod + stRes:
        hist.SetName('temp_{0}'.format(hist.GetName()))
    scDat, scMod, scRes = residual_hist(hdata, hmodel, 1.0, crange=crange)
    for hist in scDat + scMod + scRes:
        hist.SetName('fit_{0}'.format(hist.GetName()))

    tempmodel.factor = 100.0
    tempTree = compute_correction(tempmodel.overlap_func(), rand=rand)
    tempTree.SetName('temp_corrTree')

    fitmodel.factor = 100.0
    corrTree = compute_correction(fitmodel.overlap_func(), rand=rand)
    corrTree.SetName('fit_corrTree')

    with RootFile(name, 'RECREATE') as f:
        for obj in stDat + stMod + stRes + scDat + scMod + scRes + [
            tresult, result, tempTree, corrTree,
            NamedFloat('temp_overlap_true', ttrue),
            NamedFloat('temp_overlap_average', tavg),
            NamedFloat('temp_overlap_rms', trms),
            NamedFloat('fit_overlap_true', true),
            NamedFloat('fit_overlap_average', avg),
            NamedFloat('fit_overlap_rms', rms),
            Timestamp(), NamedString('name', name)
        ]:
            obj.Write()
        for i, scan in enumerate(('X1', 'Y1', 'X2', 'Y2')):
            NamedFloat('temp_chisq{0}'.format(scan), tchisqs[i]).Write()
            NamedFloat('temp_dof{0}'.format(scan), tdofs[i]).Write()
            NamedFloat('fit_chisq{0}'.format(scan), chisqs[i]).Write()
            NamedFloat('fit_dof{0}'.format(scan), dofs[i]).Write()
        f.mkdir('toyparameters').cd()
        for par in toyparameters:
            par.Write()
        f.mkdir('temp_initial').cd()
        for par in tempparameters:
            par.Write()
        f.mkdir('fit_initial').cd()
        for par in fitparameters:
            par.Write()
        f.mkdir('temp_final').cd()
        for par in tempmodel.parameters():
            NamedFloat(par.GetName(), par.val()).Write()
            NamedFloat(
                '{0}_error'.format(par.GetName()), par.err(tempmodel.parameter)
            )
        f.mkdir('fit_final').cd()
        for par in fitmodel.parameters():
            NamedFloat(par.GetName(), par.val()).Write()
            NamedFloat(
                '{0}_error'.format(par.GetName()), par.err(fitmodel.parameter)
            )

def main():
    if len(argv) < 2 or not argv[1] or not exists(argv[1]):
        raise RuntimeError('Specify argument: JSON model parameter file.')
    inputfile = argv[1]
    toymodel = SuperDoubleGaussToy()
    toymodel.factor = 100.0
    tempmodel = DoubleGaussFit()
    fitmodel = SuperDoubleGaussFit()
    vtxresx = 0.7
    suffix = inputfile[inputfile.rfind('/')+1:inputfile.find('.json')]
    do_closureTest(suffix, toymodel, tempmodel, fitmodel, inputfile, vtxresx)

if __name__ == '__main__':
    main()
