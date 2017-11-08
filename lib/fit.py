"""Provides functions for fitting of BI data.

fit: Fit beam shapes to Beam Imaging data.
model_hist: Create model histogram (based on bin integrals).
model_hist_fast: Create model histogram (based on bin centers).
data_hist: Create data histogram.
compute_chisq: Compute chi-square value for fit result.
overlap_variations: Compute overlap integral with errors.
residual_hist: Create residual histograms.
"""

from ROOT import (
    RooAbsReal, RooArgList, RooArgSet, RooCategory, RooDataHist, RooFit,
    RooSimultaneous, TH2D, TRandom3
)

ic = [('1','X'),('1','Y'),('2','X'),('2','Y')]

def fit(model, hists, fitmethod, eps=1.0e-7):
    """Fit beam shapes to Beam Imaging data.

    model: Beam shape model (derived from BeamShapeCore).
    hists: List of four TH2F with BI data.
    fitmethod: Function(pdf, data) that fits pdf to data.
    eps: Value of convergence criteria.
    """

    RooAbsReal.defaultIntegratorConfig().setEpsAbs(eps)
    RooAbsReal.defaultIntegratorConfig().setEpsRel(eps)
    modfuncs = model.model_functions()

    datahist = [RooDataHist(
        'scan{0}Beam{1}RestDataHist'.format(c, i),
        'scan{0}Beam{1}RestDataHist'.format(c, i),
        RooArgList(model.xvar(), model.yvar()),
        hists[j]
    ) for j, (i,c) in enumerate(ic)]
    sample = RooCategory('sample', 'sample')
    for (i,c) in ic:
        sample.defineType('{0}_ScanData_Beam{1}Rest'.format(c, i))
    combdata = RooDataHist(
        'combdata', 'combined data',
        RooArgList(model.xvar(), model.yvar()),
        RooFit.Index(sample),
        RooFit.Import('X_ScanData_Beam1Rest', datahist[0]),
        RooFit.Import('Y_ScanData_Beam1Rest', datahist[1]),
        RooFit.Import('X_ScanData_Beam2Rest', datahist[2]),
        RooFit.Import('Y_ScanData_Beam2Rest', datahist[3])
    )
    simpdf = RooSimultaneous('simpdf', 'simultaneous pdf', sample)
    for j, (i,c) in enumerate(ic):
        simpdf.addPdf(modfuncs[j], '{0}_ScanData_Beam{1}Rest'.format(c, i))

    result = fitmethod(simpdf, combdata)
    return result, modfuncs, datahist

def model_hist(xvar, yvar, modfuncs, nbins=95, crange=(-10.0, 10.0)):
    """Construct histogram of model functions, based on bin integrals.

    xvar, yvar: Coordinate variables.
    modfuncs: Model functions used in fit.
    nbins: Number of bins in histograms.
    crange: Range of coordinates.
    """
    hists = [TH2D(
        'hmodel{0}{1}'.format(c, i), 'hmodel{0}{1}'.format(c, i),
        nbins, crange[0], crange[1],
        nbins, crange[0], crange[1]
    ) for (i, c) in ic]
    for xbin in range(nbins):
        xlo = hists[0].GetXaxis().GetBinLowEdge(xbin+1)
        xup = hists[0].GetXaxis().GetBinUpEdge(xbin+1)
        for ybin in range(nbins):
            ylo = hists[0].GetXaxis().GetBinLowEdge(ybin+1)
            yup = hists[0].GetXaxis().GetBinUpEdge(ybin+1)
            name = 'bin_{0}_{1}'.format(xbin, ybin)
            xvar.setRange(name, xlo, xup)
            yvar.setRange(name, ylo, yup)
            for hist, modfunc in zip(hists, modfuncs):
                integral = modfunc.createIntegral(
                    RooArgSet(xvar, yvar),
                    RooFit.NormSet(RooArgSet(xvar, yvar)),
                    RooFit.Range(name)
                ).getVal()
                hist.SetBinContent(xbin+1, ybin+1, integral)
    return hists

def model_hist_fast(xvar, yvar, modfuncs, nbins=95):
    """Construct histogram of model functions, based on bin centers.

    xvar, yvar: Coordinate variables.
    modfuncs: Model functions used in fit.
    nbins: Number of bins in histograms.
    """
    hists = [modfuncs[j].createHistogram(
        'hmodel{0}{1}'.format(c, i),
        xvar, RooFit.Binning(nbins),
        RooFit.YVar(yvar, RooFit.Binning(nbins))
    ) for j, (i, c) in enumerate(ic)]
    return hists

def data_hist(xvar, yvar, datahist, nbins=95):
    """Construct histogram of data.

    xvar, yvar: Coordinate variables.
    datahist: Histogram of data used in fit.
    nbins: Number of bins in histograms.
    """
    hists = [datahist[j].createHistogram(
        'hdata{0}{1}'.format(c, i),
        xvar, RooFit.Binning(nbins),
        RooFit.YVar(yvar, RooFit.Binning(nbins))
    ) for j, (i, c) in enumerate(ic)]
    return hists

def compute_chisq(hmodel, hdata, nbins=95):
    """Compute chi-square for agreement of fit and data.

    hmodel: List of four model histograms used in fit.
    hdata: List of four data histograms used in fit.
    nbins: Number of bins in histograms.
    """
    chisqs = [0.0]*4
    dofs = [0]*4
    for i in range(4):
        hmodel[i].Scale(hdata[i].Integral())
        for j in range(nbins):
            for k in range(nbins):
                valDat = hdata[i].GetBinContent(j+1, k+1)
                if valDat == 0.0:
                    continue
                valMod = hmodel[i].GetBinContent(j+1, k+1)
                if valMod < valDat:
                    errDat = hdata[i].GetBinErrorLow(j+1, k+1)
                else:
                    errDat = hdata[i].GetBinErrorUp(j+1, k+1)
                dofs[i] += 1
                chisqs[i] += ((valDat-valMod)/errDat)**2
    return chisqs, dofs

def overlap_variations(model, rand=None, n=100, verbose=False):
    """Compute overlap integral with uncertainty from parameter variations.

    model: Beam shape model (derived from BeamShapeCore).
    rand: TRandom random number generator (optional).
    n: Number of variations (default: 100).
    verbose: Set True for output at every step.
    """

    if rand is None:
        rand = TRandom3()
        rand.SetSeed(0)
    overlap = model.overlap_func()
    true = overlap.Integral(-30.0, 30.0, -30.0, 30.0)
    print '<<< True overlap: {0}'.format(true)
    values = []
    for i in range(n):
        overlap = model.assign_overlap(overlap, random=rand)
        value = overlap.Integral(-30.0, 30.0, -30.0, 30.0)
        if value <= 0.0:
            continue
        values.append(value)
        if verbose:
            print '<<< Variation {0}: {1}'.format(i, value)
    if len(values) == 0:
        return -1.0, -1.0, -1.0
    avg = sum(values) / len(values)
    rms = (sum([(v-avg)**2 for v in values])/len(values)) ** 0.5
    diff = abs(true-avg)/true
    if diff < 0.01 or diff > 100.0:
        overlap = model.assign_overlap(overlap)
        true = overlap.Integral(-30.0, 30.0, -30.0, 30.0, 1.0e-12)
    return true, avg, rms

def residual_hist(hdata, hmodel, scaling, crange=(-10.0, 10.0)):
    """Create residual, data and model histograms in real coordinates.

    hdata: List of four data histograms.
    hmodel: List of four model histograms.
    scaling: Scaling factor of old to new coordinates.
    crange: 2-tuple of limits of the coordinates.
    """
    nbins = hdata[0].GetNbinsX()
    scDat = []
    scMod = []
    scRes = []
    for j, (i,c) in enumerate(ic):
        dat = TH2D(
            'dataHist{0}{1}'.format(c, i), 'dataHist{0}{1}'.format(c, i),
            nbins, crange[0]*scaling, crange[1]*scaling,
            nbins, crange[0]*scaling, crange[1]*scaling
        )
        mod = TH2D(
            'modelHist{0}{1}'.format(c, i), 'modelHist{0}{1}'.format(c, i),
            nbins, crange[0]*scaling, crange[1]*scaling,
            nbins, crange[0]*scaling, crange[1]*scaling
        )
        res = TH2D(
            'residualHist{0}{1}'.format(c, i), 'residualHist{0}{1}'.format(c, i),
            nbins, crange[0]*scaling, crange[1]*scaling,
            nbins, crange[0]*scaling, crange[1]*scaling
        )
        for xbin in range(nbins):
            for ybin in range(nbins):
                m = hmodel[j].GetBinContent(xbin, ybin)
                mod.SetBinContent(xbin, ybin, m)
                d = hdata[j].GetBinContent(xbin, ybin)
                if d <= 0.0:
                    continue
                dat.SetBinContent(xbin, ybin, d)
                if m < d:
                    e = hdata[j].GetBinErrorLow(xbin, ybin)
                else:
                    e = hdata[j].GetBinErrorUp(xbin, ybin)
                res.SetBinContent(xbin, ybin, (d-m)/e)
        scDat.append(dat)
        scMod.append(mod)
        scRes.append(res)
    return scDat, scMod, scRes
