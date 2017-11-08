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
from lib.shape.tg import (
    TripleGaussFit, TripleGaussToy, SuperDoubleGaussFit, SuperDoubleGaussToy
)

def do_closureTest(
    suffix, toymodel, fitmodel, vtxresx, vtxresy=None,
    n=1, eachtoy=None, eachfit=None
):
    if vtxresy is None:
        vtxresy = vtxresx
    if eachtoy is None:
        eachtoy = lambda toy, r: toy.overlap_func()
    if eachfit is None:
        eachfit = lambda fit: fit

    name = 'ClosureTest_v1_{0}_{1}_{2}' \
           .format(toymodel.name(), fitmodel.name(), suffix)

    rand = TRandom3()
    rand.SetSeed(0)

    fitmodel.set_vtxres(vtxresx, vtxresy)
    for par in ['x011', 'x012', 'x021', 'x022', 'y011', 'y012', 'y021', 'y022']:
        fitmodel.parameter(par).setConstant()
    fitmethod = lambda pdf, data: pdf.fitTo(
        data, RooFit.Save(), RooFit.PrintLevel(1), RooFit.Verbose(0)
    )

    tree = RootTree('closureTest', 'Closure Test')
    for par in toymodel.fit_parameters:
        tree.branch_f('toy_{0}'.format(par))
    for par in fitmodel.fit_parameters:
        tree.branch_f('fit_{0}'.format(par))
    tree.branch_f('toy_overlapTrue')
    tree.branch_f('toy_overlapDiff')
    tree.branch_f('toy_overlapDiff_error')
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

        print '<<< {0}: Fit toy model ({1})'.format(i, Timestamp())
        fitmodel = eachfit(fitmodel)
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
        'SG', 'DG', 'TG', 'SupG', 'SupDG'
    ]:
        raise RuntimeError(
            'Specify 1st arugment: Toy model (SG, DG, TG, SupG, SupDG).'
        )
    toymodel = {
        'SG': SingleGauss, 'DG': DoubleGaussToy, 'TG': TripleGaussToy,
        'SupG': SuperGaussToy, 'SupDG': SuperDoubleGaussToy
    }[argv[1]]()
    toymodel.factor = 100.0
    if len(argv) < 3 or not argv[2] or argv[2] not in [
        'SG', 'DG', 'TG', 'SupG', 'SupDG'
    ]:
        raise RuntimeError(
            'Specify 2nd argument: Fit model (SG, DG, TG, SupG, SupDG).'
        )
    fitmodel = {
        'SG': SingleGauss, 'DG': DoubleGaussFit, 'TG': TripleGaussFit,
        'SupG': SuperGaussFit, 'SupDG': SuperDoubleGaussFit
    }[argv[2]]()
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
    def eachfit(fitmodel):
        fitmodel.load_json()
        return fitmodel

    do_closureTest(
        name, toymodel, fitmodel, vtxres, n=n, eachtoy=eachtoy, eachfit=eachfit
    )

if __name__ == '__main__':
    main()
