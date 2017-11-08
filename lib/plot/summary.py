"""Provides classes for creating summary plots.

SummaryPlot: Plot summary for different models and bcids.
CorrectionSummary: Plot summary of corrections for different models and bcids.
ChiSquareSummary: Plot summary of chisquares for different models and bcids.
"""

from array import array

from ROOT import TGraphErrors, TH2F, TLegend, TMultiGraph

from lib.plot.plot import SingleGraphBase

markers = lambda i: 20
colors = lambda i: i+1

class SummaryPlot(SingleGraphBase):
    """Plot a summary of values per model and bcid.

    __init__: Initialize.
    create_legend: Add a legend to the plot.
    """

    def __init__(self, models, bcids, values, fill=4954, workinprogress=False):
        """Initialize a summary plot of values per model and bcid."""
        nbcid, nmodels = len(bcids), len(models)
        order = sorted(range(nbcid), key=lambda i: bcids[i])
        mini, maxi = 1.0e99, -1.0e99
        multi = TMultiGraph('summary', '')
        for i, mod in enumerate(models):
            xval = array('d', [c+0.09*(i-0.5*nmodels) for c in range(nbcid)])
            xerr = array('d', [0.0]*nbcid)
            yval = array('d', [values[i][j][0] for j in order])
            yerr = array('d', [values[i][j][1] for j in order]) #[0.0]*nbcid)
            mini = min(mini, min([v-e for v,e in zip(yval, yerr)]))
            maxi = max(maxi, max([v+e for v,e in zip(yval, yerr)]))
            graph = TGraphErrors(nbcid, xval, yval, xerr, yerr)
            graph.SetName('summary_{0}'.format(mod))
            multi.Add(graph)
        self._multi = multi
        mini, maxi = mini-0.08*(maxi-mini), maxi+0.25*(maxi-mini)
        hist = TH2F('axishist', '', nbcid, -0.5, nbcid-0.5, 100, mini, maxi)
        for i, j in enumerate(order):
            hist.GetXaxis().SetBinLabel(i+1, str(bcids[j]))
        SingleGraphBase.__init__(self, hist, 'summary', fill, workinprogress)
        for gr in multi.GetListOfGraphs():
            self.add(gr, draw=False)
        self._xtitle = 'bcid'
        self._drawoption = 'AXIS'
        self.markers = [markers(i) for i in range(nmodels)]
        self.colors = [colors(i) for i in range(nmodels)]
        self.xrange(-0.5, nbcid-0.5)
        self.yrange(mini, maxi)

    def create_legend(self, models):
        """Add a legend with the model names to the plot."""
        l = TLegend(0.15, 0.77, 0.85, 0.83)
        l.SetNColumns(3)
        l.SetBorderSize(0)
        for mod, gr, mark, clr in zip(
            models, self._multi.GetListOfGraphs(), self.markers, self.colors
        ):
            gr.SetMarkerStyle(mark)
            gr.SetMarkerColor(clr)
            entry = l.AddEntry(gr.GetName(), mod, 'P')
            entry.SetMarkerStyle(mark)
            entry.SetMarkerColor(clr)
        self.add(l)
        return l

    def _draw_first(self):
        SingleGraphBase._draw_first(self)
        self.xaxis().SetNdivisions(self._graph.GetNbinsX(), False)
        self._multi.Draw('P')

    def _draw_second(self):
        SingleGraphBase._draw_second(self)
        self.xaxis().SetLabelSize(0.03)

class CorrectionSummary(SummaryPlot):
    """Plot a summary of corrections per model and bcid.

    __init__: Initialize.
    """

    def __init__(
        self, models, bcids, corrections, fill=4954, workinprogress=False
    ):
        """Initialize a summary plot of corrections per model and bcid."""
        SummaryPlot.__init__(
            self, models, bcids, corrections, fill=fill,
            workinprogress=workinprogress
        )
        self._ytitle = 'correction [%]'

class ChiSquareSummary(SummaryPlot):
    """Plot a summary of chisquares per model and bcid.

    __init__: Initialize.
    """

    def __init__(
        self, models, bcids, chisq, fill=4954, workinprogress=False
    ):
        """Initialize a summary plot of chisquares per model and bcid."""
        SummaryPlot.__init__(
            self, models, bcids, chisq, fill=fill, workinprogress=workinprogress
        )
        self._ytitle = '#chi^{2}/d.o.f.'
