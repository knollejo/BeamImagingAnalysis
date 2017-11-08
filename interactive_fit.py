from json import load
from os.path import exists
from re import match
from sys import argv

from ROOT import (
    gStyle, kLHintsExpandX, kLHintsExpandY, RooFit, TGHorizontalFrame,
    TGHorizontalLayout, TGLabel, TGLayoutHints, TGMainFrame, TGNumberEntry,
    TGTextButton, TGVerticalFrame, TRootEmbeddedCanvas, TPyDispatcher
)
from ROOT.TGNumberFormat import kNESRealThree

from lib.fit import (
    compute_chisq, data_hist, fit, model_hist_fast as model_hist, residual_hist
)
from lib.io import BareRootFile
from lib.plot.plot import ColorBase
from lib.shape.dg import DoubleGaussFit, SuperGaussFit
from lib.shape.sg import SingleGauss, SingleGaussUncorrelated
from lib.shape.tg import SuperDoubleGaussFit, TripleGaussFit

class ParameterConstWindow(TGMainFrame):

    def __init__(self, model, fitter):
        self._container = []
        self.model = model
        self.fitter = fitter

        ColorBase.kBird()
        gStyle.SetOptStat(0)

        TGMainFrame.__init__(self, 0, 300, 300)
        self.SetLayoutManager(TGHorizontalLayout(self))

        self._fitCol = TGVerticalFrame(self, 250, 500)
        self._fitPars = {}
        for par in self.model.parameters():
            if par.is_formula() or match('^[xy]0[12][12]$', par.GetName()) or (
                par.isConstant() and not par.GetName().endswith('VtxRes')
            ):
                continue
            row = TGHorizontalFrame(self._fitCol, 250, 50)
            label = TGLabel(row, par.GetName())
            entry = TGNumberEntry(row, par.val(), 10, kNESRealThree)
            row.AddFrame(label, TGLayoutHints(kLHintsExpandX, 5, 5, 5, 5))
            row.AddFrame(entry)
            self._fitCol.AddFrame(row, TGLayoutHints(kLHintsExpandX))
            self._container.append(row)
            self._container.append(label)
            self._fitPars[par.GetName()] = entry
        self.AddFrame(self._fitCol)

        self._physCol = TGVerticalFrame(self, 250, 500)
        self._physPars = {}
        for par in self.model.parameters():
            if (
                not par.is_formula() and
                not match('^[xy]0[12][12]$', par.GetName()) and
                (not par.isConstant() or par.GetName().endswith('VtxRes'))
            ):
                continue
            row = TGHorizontalFrame(self._physCol, 250, 50)
            label = TGLabel(row, par.GetName())
            entry = TGNumberEntry(row, par.val(), 10, kNESRealThree)
            entry.SetState(False)
            row.AddFrame(label, TGLayoutHints(kLHintsExpandX, 5, 5, 5, 5))
            row.AddFrame(entry)
            self._physCol.AddFrame(row, TGLayoutHints(kLHintsExpandX))
            self._container.append(row)
            self._container.append(label)
            self._physPars[par.GetName()] = entry
        self.AddFrame(self._physCol)

        self._metaCol = TGVerticalFrame(self, 250, 500)
        self._metaPars = {}
        for par in ['chi2/dof', 'nll']:
            row = TGHorizontalFrame(self._metaCol, 250, 50)
            label = TGLabel(row, par)
            entry = TGNumberEntry(row, 0.0, 10, kNESRealThree)
            entry.SetState(False)
            row.AddFrame(label, TGLayoutHints(kLHintsExpandX, 5, 5, 5, 5))
            row.AddFrame(entry)
            self._metaCol.AddFrame(row, TGLayoutHints(kLHintsExpandX))
            self._container.append(row)
            self._container.append(label)
            self._metaPars[par] = entry
        self._computeBtn = TGTextButton(self._metaCol, 'Compute', 10)
        self._fitBtn = TGTextButton(self._metaCol, 'Fit data', 10)
        self._drawBtn = TGTextButton(self._metaCol, 'Draw model', 10)
        for btn in [self._computeBtn, self._fitBtn, self._drawBtn]:
            self._metaCol.AddFrame(btn, TGLayoutHints(kLHintsExpandX, 5,5,5,5))
        self.AddFrame(self._metaCol)

        self._canvCol = [TGVerticalFrame(self, 250, 500) for i in range(2)]
        self._canvas = [TRootEmbeddedCanvas(
            'ce{0}'.format(i), self._canvCol[i%2], 250, 250
        ) for i in range(4)]
        for i in range(2):
            self.AddFrame(self._canvCol[i], TGLayoutHints(
                kLHintsExpandX | kLHintsExpandY
            ))
            self._canvCol[i].AddFrame(self._canvas[i], TGLayoutHints(
                kLHintsExpandX | kLHintsExpandY
            ))
            self._canvCol[i].AddFrame(self._canvas[i+2], TGLayoutHints(
                kLHintsExpandX | kLHintsExpandY
            ))

        self._computeBtnDisp = TPyDispatcher(self.computeBtnClicked)
        self._computeBtn.Connect(
            'Clicked()', 'TPyDispatcher', self._computeBtnDisp, 'Dispatch()'
        )
        self._fitBtnDisp = TPyDispatcher(self.fitBtnClicked)
        self._fitBtn.Connect(
            'Clicked()', 'TPyDispatcher', self._fitBtnDisp, 'Dispatch()'
        )
        self._drawBtnDisp = TPyDispatcher(self.drawBtnClicked)
        self._drawBtn.Connect(
            'Clicked()', 'TPyDispatcher', self._drawBtnDisp, 'Dispatch()'
        )

        self.SetWindowName('{0} Parameters'.format(self.model.name()))
        self.MapSubwindows()
        self.Resize(self.GetDefaultSize())
        self.MapWindow()

        for par in self.model.parameters():
            if match('^[xy]0[12][12]$', par.GetName()) or par.is_formula():
                continue
            par.setConstant()

    def __del__(self):
        self.Cleanup()

    def readParameters(self):
        def setVal(par, val):
            self.model.parameter(par).set_range(val-0.1, val+0.1)
            self.model.parameter(par).setVal(val)
        for par in self._fitPars:
            setVal(par, self._fitPars[par].GetNumber())
        for par in [p for p in self._physPars if 'VtxRes' in p]:
            setVal(par, self._physPars[par].GetNumber())

    def displayParameters(self, chi2=False, nll=False):
        for par in [p for p in self._physPars if 'VtxRes' not in p]:
            self._physPars[par].SetNumber(self.model.parameter(par).val())
        if chi2:
            self._metaPars['chi2/dof'].SetNumber(chi2)
        if nll:
            self._metaPars['nll'].SetNumber(nll)

    def computeBtnClicked(self):
        self.readParameters()
        self.displayParameters()

    def fitBtnClicked(self):
        self.readParameters()
        result, residuals, allChi2, allDof = self.fitter(self.model)
        self._residuals = residuals
        self.displayParameters(sum(allChi2)/sum(allDof), result.minNll())

        for i in range(4):
            self._canvas[i].GetCanvas().cd()
            for xbin in range(self._residuals[i].GetXaxis().GetNbins()+1):
                for ybin in range(self._residuals[i].GetYaxis().GetNbins()+1):
                    if self._residuals[i].GetBinContent(xbin, ybin) < -4.9999:
                        self._residuals[i].SetBinContent(xbin, ybin, -4.9999)
                    if self._residuals[i].GetBinContent(xbin, ybin) == 0.0:
                        self._residuals[i].SetBinContent(xbin, ybin, -10.0)
            self._residuals[i].Draw('COLZ')
            self._residuals[i].GetZaxis().SetRangeUser(-5.0, 5.0)
            self._canvas[i].GetCanvas().Update()

    def drawBtnClicked(self):
        self.readParameters()
        self.displayParameters()

        modelFunctions = self.model.model_functions()
        self._hists = []
        for i in range(4):
            self._canvas[i].GetCanvas().cd()
            hist = modelFunctions[i].createHistogram(
                'model{0}'.format(i), self.model.xvar(), RooFit.Binning(95),
                RooFit.YVar(self.model.yvar(), RooFit.Binning(95))
            )
            hist.SetTitle('')
            hist.GetXaxis().SetTitle('')
            hist.GetYaxis().SetTitle('')
            hist.GetZaxis().SetTitle('')
            hist.Draw('COLZ')
            self._hists.append(hist)
            self._canvas[i].GetCanvas().Update()

def fit_shape(
    model, bcid, hists, name, crange
):
    fitmethod = lambda pdf, data: pdf.fitTo(
        data, RooFit.Save(), RooFit.PrintLevel(1), RooFit.Verbose(0)
    )
    result, modfuncs, datahist = fit(model, hists, fitmethod)
    hdata = data_hist(model.xvar(), model.yvar(), datahist)
    hmodel = model_hist(model.xvar(), model.yvar(), modfuncs)
    chisqs, dofs = compute_chisq(hmodel, hdata)
    __, __, scRes = residual_hist(hdata, hmodel, 1.0, crange=crange)
    return result, scRes, chisqs, dofs

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
        crange = (-20.0, 20.0)
    else:
        crange = (-10.0, 10.0)
    model = {
        'SG': SingleGauss, 'DG': DoubleGaussFit, 'TG': TripleGaussFit,
        'SupG': SuperGaussFit, 'SupDG': SuperDoubleGaussFit,
        'noCorr': SingleGaussUncorrelated
    }[argv[3]](crange=crange)
    datafile = '{0}/{1}.root'.format(config['datapath'], config['dataname'])
    hists = []
    with BareRootFile(datafile) as f:
        for histname in [
            'hist_Beam2MoveX_bunch{0}Add', 'hist_Beam2MoveY_bunch{0}Add',
            'hist_Beam1MoveX_bunch{0}Add', 'hist_Beam1MoveY_bunch{0}Add'
        ]:
            hist = f.Get(histname.format(bcid))
            hist.SetDirectory(0)
            hists.append(hist)
    vtxresx = config['vtxresx']
    vtxresy = config['vtxresy']
    scaling = config['scaling']
    model.set_vtxres(vtxresx / scaling, vtxresy / scaling)
    fitter = (lambda c, h, n, r: lambda m: fit_shape(m, c, h, n, r))(
        bcid, hists, name, crange
    )
    window = ParameterConstWindow(model, fitter)

if __name__ == '__main__':
    main()
