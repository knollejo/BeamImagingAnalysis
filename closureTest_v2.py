from re import match
from sys import argv

from ROOT import RooFit, TRandom3

from lib.closure import generate_toys
from lib.correction import compute_correction
from lib.fit import compute_chisq, data_hist, fit, model_hist_fast as model_hist
from lib.io import RootFile, RootTree, Timestamp
from lib.shape.dg import (
    DoubleGaussFit, DoubleGaussToy, SuperGaussFit, SuperGaussToy
)
from lib.shape.sg import SingleGauss
from lib.shape.tg import SuperDoubleGaussFit, SuperDoubleGaussToy, TripleGaussToy

def do_closureTest(
    suffix, toymodel, tempmodel, fitmodel, vtxresx, vtxresy=None,
    n=1, eachtoy=None
):
    if vtxresy is None:
        vtxresy = vtxresx
    if eachtoy is None:
        eachtoy = lambda toy, r: toy.overlap_func()

    name = 'ClosureTest_v2_{0}_{1}_{2}' \
           .format(toymodel.name(), fitmodel.name(), suffix)

    rand = TRandom3()
    rand.SetSeed(0)

    fitmodel.set_vtxres(vtxresx, vtxresy)
    tempmodel.set_vtxres(vtxresx, vtxresy)
    for par in ['x011', 'x012', 'x021', 'x022', 'y011', 'y012', 'y021', 'y022']:
        fitmodel.parameter(par).setConstant()
        tempmodel.parameter(par).setConstant()
    fitmethod = lambda pdf, data: pdf.fitTo(
        data, RooFit.Save(), RooFit.PrintLevel(1), RooFit.Verbose(0)
    )

    tree = RootTree('closureTest', 'Closure Test')
    for par in toymodel.fit_parameters:
        tree.branch_f('toy_{0}'.format(par))
    for par in tempmodel.fit_parameters:
        tree.branch_f('temp_{0}'.format(par))
    for par in fitmodel.fit_parameters:
        tree.branch_f('fit_{0}'.format(par))
    tree.branch_f('toy_overlapTrue')
    tree.branch_f('toy_overlapDiff')
    tree.branch_f('toy_overlapDiff_error')
    tree.branch_f('temp_overlapTrue')
    tree.branch_f('temp_overlapDiff')
    tree.branch_f('temp_overlapDiff_error')
    tree.branch_f('temp_chisq')
    tree.branch_i('temp_dof')
    tree.branch_f('temp_minNll')
    tree.branch_f('fit_overlapTrue')
    tree.branch_f('fit_overlapDiff')
    tree.branch_f('fit_overlapDiff_error')
    tree.branch_f('fit_chisq')
    tree.branch_i('fit_dof')
    tree.branch_f('fit_minNll')
    tree.branch_f('nEntries', 4)

    for i in range(n):
        print '<<< {0}: Generate toy model ({1})'.format(i, Timestamp())
        overlap = eachtoy(toymodel, rand)
        hists, nevents = generate_toys(
            overlap, vtxresx, vtxresy=vtxresy, rand=rand, nbins=760#, verbose=True
        )
        for par in toymodel.fit_parameters:
            tree.set('toy_{0}'.format(par), toymodel.parameter(par).val())
        for j, value in enumerate(nevents):
            tree.set('nEntries', value, j)

        print '<<< {0}: Compute correction for toy model ({1})' \
              .format(i, Timestamp())
        toy_tru, toy_fit, toy_dif = \
            compute_correction(overlap, rand=rand, extended=False)
        tree.set('toy_overlapTrue', toy_tru)
        mean = sum(toy_dif)/len(toy_dif)
        error = (sum([(d-mean)**2 for d in toy_dif])/len(toy_dif))**0.5
        tree.set('toy_overlapDiff', mean)
        tree.set('toy_overlapDiff_error', error)

        print '<<< {0}: Fit temp model ({1})'.format(i, Timestamp())
        tempmodel.load_json()
        tresult, tmodfuncs, tdatahist = fit(tempmodel, hists, fitmethod)
        print '<<< {0}: Create model histogram for temp ({1})' \
              .format(i, Timestamp())
        tmodel = model_hist(tempmodel.xvar(), tempmodel.yvar(), tmodfuncs)
        print '<<< {0}: Create data histogram for temp ({1})' \
              .format(i, Timestamp())
        tdata = data_hist(tempmodel.xvar(), tempmodel.yvar(), tdatahist)
        print '<<< {0}: Compute chisquare of temp ({1})'.format(i, Timestamp())
        tchisqs, tdofs = compute_chisq(tmodel, tdata)
        for par in tempmodel.fit_parameters:
            tree.set('temp_{0}'.format(par), tempmodel.parameter(par).val())
        tree.set('temp_minNll', tresult.minNll())
        tree.set('temp_chisq', sum(tchisqs))
        tree.set('temp_dof', sum(tdofs))

        print '<<< {0}: Compute correction for temp model ({1})' \
              .format(i, Timestamp())
        toverlap = tempmodel.overlap_func()
        temp_tru, temp_fit, temp_dif = \
            compute_correction(toverlap, rand=rand, extended=False)
        tree.set('temp_overlapTrue', temp_tru)
        tmean = sum(temp_dif)/len(temp_dif)
        terror = (sum([(d-tmean)**2 for d in temp_dif])/len(temp_dif))**0.5
        tree.set('temp_overlapDiff', tmean)
        tree.set('temp_overlapDiff_error', terror)

        print '<<< {0}: Fit toy model ({1})'.format(i, Timestamp())
        fitmodel.load_json()
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
        print '<<< {0}: Create model histogram for fit ({1})' \
              .format(i, Timestamp())
        hmodel = model_hist(fitmodel.xvar(), fitmodel.yvar(), modfuncs)
        print '<<< {0}: Create data histogram for fit ({1})' \
              .format(i, Timestamp())
        hdata = data_hist(fitmodel.xvar(), fitmodel.yvar(), datahist)
        print '<<< {0}: Compute chisquare of fit ({1})'.format(i, Timestamp())
        chisqs, dofs = compute_chisq(hmodel, hdata)
        for par in fitmodel.fit_parameters:
            tree.set('fit_{0}'.format(par), fitmodel.parameter(par).val())
        tree.set('fit_minNll', result.minNll())
        tree.set('fit_chisq', sum(chisqs))
        tree.set('fit_dof', sum(dofs))

        print '<<< {0}: Compute correction for fit model ({1})' \
              .format(i, Timestamp())
        overlap = fitmodel.overlap_func()
        fit_tru, fit_fit, fit_dif = \
            compute_correction(overlap, rand=rand, extended=False)
        tree.set('fit_overlapTrue', fit_tru)
        mean = sum(fit_dif)/len(fit_dif)
        error = (sum([(d-mean)**2 for d in fit_dif])/len(fit_dif))**0.5
        tree.set('fit_overlapDiff', mean)
        tree.set('fit_overlapDiff_error', error)

        print '<<< {0}: Fill tree ({1})'.format(i, Timestamp())
        tree.Fill()

    output = RootFile(name, 'RECREATE')
    tree.Write()
    Timestamp().Write()
    output.Write()
    return output.close()

def main():
    if len(argv) < 2 or not argv[1] or argv[1] not in [
        'SupG', 'SupDG'
    ]:
        raise RuntimeError(
            'Specify 1st arugment: Toy model (SG, DG, TG, SupG, SupDG).'
        )
    toymodel = {
        'SG': SingleGauss, 'DG': DoubleGaussToy, 'TG': TripleGaussToy,
        'SupG': SuperGaussToy, 'SupDG': SuperDoubleGaussToy
    }[argv[1]]()
    toymodel.factor = 100.0
    if len(argv) < 3 or not argv[2] or argv[2] not in ['SupG', 'SupDG']:
        raise RuntimeError('Specify 2nd argument: Fit model (SupG, SupDG).')
    fitmodel, tempmodel = {
        'SupG': (SuperGaussFit, SingleGauss),
        'SupDG': (SuperDoubleGaussFit, DoubleGaussFit)
    }[argv[2]]
    fitmodel, tempmodel = fitmodel(), tempmodel()
    tempmodel.factor = 100.0
    fitmodel.factor = 100.0
    if len(argv) < 4 or not argv[3]:
        raise RuntimeError('Specify 3rd argument: Output name.')
    name = argv[3]
    if len(argv) < 5 or not argv[4]:
        raise RuntimeError('Specify 4th argument: Vertex resolution.')
    try:
        vtxres = float(argv[4])
    except ValueError:
        raise RuntimeError('Specify 4th argument: Vertex resolution.')
    if len(argv) >= 6 and argv[5]:
        try:
            n = int(argv[5])
        except ValueError:
            raise RuntimeError('Optional 5th argument: Number of iterations.')
    else:
        n = 1

    def ateachtoy(toymodel, rand, jsonfile):
        toymodel.load_json('res/shapes/{0}.json'.format(jsonfile), rand)
        return toymodel.overlap_func()
    eachtoy = (lambda json: lambda toy, rand: ateachtoy(toy, rand, json))({
        'SG': 'toySG', 'DG': 'toyDG', 'TG': 'toyTG', 'SupG': 'toySupG',
        'SupDG': 'toySupDG'
    }[argv[1]])

    do_closureTest(
        name, toymodel, tempmodel, fitmodel, vtxres, n=n, eachtoy=eachtoy
    )

if __name__ == '__main__':
    main()
