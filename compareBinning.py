from json import load
from os.path import exists
from sys import argv

from ROOT import RooArgList, RooDataHist

from lib.fit import compute_chisq, residual_hist
from lib.io import BareRootFile
from lib.shape.dg import DoubleGaussFit
from lib.shape.sg import SingleGauss
from lib.shape.tg import TripleGaussFit

def compare_binning(filename):
    scans = ('X1', 'Y1', 'X2', 'Y2')

    with BareRootFile(filename) as f:
        oldres = [f.get('residualHist{0}'.format(scan)) for scan in scans]
        oldchi = [f.get_val('chisq{0}'.format(scan)) for scan in scans]
        olddof = [f.get_val('dof{0}'.format(scan)) for scan in scans]
        name = f.get_val('name')
    bcidpos = name.find('bcid')
    dataname = name[16:name.rfind('_', 0, bcidpos-1)]
    fitname = name[name.rfind('_', 0, bcidpos-1)+1:bcidpos-1]
    bcid = int(name[bcidpos+4:])

    model = {
        'SG': SingleGauss, 'DG': DoubleGaussFit, 'TG': TripleGaussFit
    }[fitname]()
    model.load_root(filename)
    modfuncs = model.model_functions()

    with open('res/hist/{0}.json'.format(dataname)) as f:
        json = load(f)
    nbins = json['nbins']
    scaling = json['scaling']
    datafile = '{0}/{1}.root'.format(json['datapath'], json['name'])

    hists = []
    with BareRootFile(datafile) as f:
        for histname in [
            'hist_Beam2MoveX_bunch{0}Add', 'hist_Beam2MoveY_bunch{0}Add',
            'hist_Beam1MoveX_bunch{0}Add', 'hist_Beam1MoveY_bunch{0}Add'
        ]:
            hist = f.get(histname.format(bcid))
            hists.append(hist)
    datahist = [RooDataHist(
        'scan{0}Beam{1}RestDataHist'.format(c, i),
        'scan{0}Beam{1}RestDataHist'.format(c, i),
        RooArgList(model.xvar(), model.yvar()),
        hists[j]
    ) for j, (i,c) in enumerate([('1','X'),('1','Y'),('2','X'),('2','Y')])]

    chisq, dof, hdata, hmodel = compute_chisq(model, modfuncs, datahist, nbins)
    scDat, scMod, scRes = residual_hist(hdata, hmodel, scaling)

    for i, scan in enumerate(scans):
        oldval = oldchi[i] / olddof[i]
        newval = chisq[i] / dof[i]
        print '{0}: {1:.4f} {2:.4f}'.format(scan, oldval, newval)

    return scRes, oldres

def main():
    if len(argv) < 2 or not argv[1] or not exists(argv[1]):
        raise RuntimeError('Specify 1st argument: ROOT results file.')
    return compare_binning(argv[1])

if __name__ == '__main__':
    main()
