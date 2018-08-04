"""Provides base class for plots.

PlotBase: Base class (abstract).
SingleGraphBase: Base class for single graphs.
SingleHistBase: Base class for single histograms.
ColorBase: Base class for color plots.
"""

from array import array
from os import mkdir
from os.path import exists

from ROOT import gStyle, TCanvas, TColor, TF1, TLatex, TPaveText

class PlotBase(TCanvas):
    """Core functionality for plots (abstract).

    __init__: Initialize.
    xaxis: Return x-axis of main element (abstract).
    yaxis: Return y-axis of main element (abstract).
    zaxis: Return z-axis of main element (abstract).
    xrange: Set x-range of main element.
    yrange: Set y-range of main element.
    zrange: Set y-range of main element.
    draw_cms: Write name and data information.
    draw: Draw the plot.
    add: Add object to the plot.
    add_pave: Add a pave to the plot.
    add_line: Add a constant line.
    save: Save plot to file.
    save_pdf: Save plot as PDF.
    save_png: Save plot as PNG.
    save_C: Save plot as C macro.
    """

    def __init__(self, name='Plot', fill=4954, workinprogress=False):
        """Initialize core functionality of a plot."""
        self._xrange = None
        self._xtitle = None
        self._xlog = False
        self._yrange = None
        self._ytitle = None
        self._ylog = False
        self._zrange = None
        self._ztitle = None
        self._zlog = False
        self._title = None
        self._above = False
        self._simulation = False
        self._drawCMS = True
        TCanvas.__init__(self, name, '', 600, 600)
        gStyle.SetOptStat(0)
        self.fill = fill
        if fill is None:
            self._simulation = True
        self.workinprogress = workinprogress
        self._container_draw = []
        self._container_store = []

    def xaxis(self):
        """Return x-axis of main element."""
        msg = 'PlotBase: Called xaxis() of abstract class!'
        raise NotImplementedError(msg)

    def yaxis(self):
        """Return y-axis of main element."""
        msg = 'PlotBase: Called yaxis() of abstract class!'
        raise NotImplementedError(msg)

    def zaxis(self):
        """Return z-axis of main element."""
        msg = 'PlotBase: Called zaxis() of abstract class!'
        raise NotImplementedError(msg)

    def xrange(self, lo=None, hi=None):
        """Set x-range of main element."""
        if lo is None or hi is None:
            self._xrange = None
        else:
            self._xrange = (lo, hi)

    def yrange(self, lo=None, hi=None):
        """Set y-range of main element."""
        if lo is None or hi is None:
            self._yrange = None
        else:
            self._yrange = (lo, hi)

    def zrange(self, lo=None, hi=None):
        """Set z-range of main element."""
        if lo is None or hi is None:
            self._zrange = None
        else:
            self._zrange = (lo, hi)

    def draw_cms(self, textsize=0.0375):
        """Write CMS name and data information."""
        if self._above:
            y = 0.92
            align = (31, 11)
        else:
            y = 0.88
            align = (33, 13)
        text = TLatex()
        text.SetNDC()
        text.SetTextFont(62)
        text.SetTextSize(textsize)
        text.SetTextAlign(align[0])
        if not self._simulation:
            if self.fill <= 4720:
                theyear = 2015
            elif self.fill < 5600:
                theyear = 2016
            else:
                theyear = 2017
            if self.fill <= 4647 and self.fill >=4634:
                theenergy = '5.02 TeV'
            elif self.fill < 5563 and self.fill >= 5505:
                theenergy = 'Pbp, 8.16 TeV'
            elif self.fill <= 5575 and self.fill >=5563:
                theenergy = 'pPb, 8.16 TeV'
            else:
                theenergy = '13 TeV'
            thetext = 'Fill {} ({}, {})'.format(self.fill, theyear, theenergy)
            text.DrawLatex(0.88, y, thetext)
        text.SetTextAlign(align[1])
        if self.workinprogress and self._simulation:
            thetext = '#bf{#scale[0.75]{#it{Simulation, Work in Progress}}}'
        elif self.workinprogress and not self._simulation:
            thetext = '#bf{#scale[0.75]{#it{Work in Progress}}}'
        elif not self.workinprogress and self._simulation:
            thetext = 'CMS #bf{#scale[0.75]{#it{Simulation Preliminary}}}'
        else:
            thetext = 'CMS #bf{#scale[0.75]{#it{Preliminary}}}'
        text.DrawLatex(0.15, y, thetext)

    def _draw_first(self): pass
    def _draw_second(self): pass

    def draw(self, canvas=None):
        if canvas is None:
            canvas = self
        canvas.cd()
        self._draw_first()
        for obj in self._container_draw:
            obj.Draw('SAME')
        canvas.Update()
        for c, axis in [
            ('x', self.xaxis), ('y', self.yaxis), ('z', self.zaxis)
        ]:
            try:
                axis = axis()
            except NotImplementedError:
                continue
            axis.SetLabelSize(0.025)
            rng = getattr(self, '_{0}range'.format(c))
            if rng is not None:
                axis.SetRangeUser(rng[0], rng[1])
            ttl = getattr(self, '_{0}title'.format(c))
            if ttl is not None:
                axis.SetTitle(ttl)
            log_f = getattr(self, 'SetLog{0}'.format(c))
            log_v = getattr(self, '_{0}log'.format(c))
            log_f(log_v)
        self.yaxis().SetTitleOffset(1.3)
        self._draw_second()
        if self._drawCMS:
            self.draw_cms()
        if self._title is not None:
            text = TLatex()
            text.SetNDC()
            text.SetTextFont(62)
            text.SetTextSize(0.04)
            text.SetTextAlign(21)
            text.DrawLatex(0.5, 0.93, self._title)
        canvas.Modified()
        canvas.Update()

    def add(self, obj, draw=True):
        """Adds an object to the ownership of the plot."""
        if draw:
            self._container_draw.append(obj)
        else:
            self._container_store.append(obj)

    def add_pave(self, x1, y1, x2, y2, border=False):
        """Creates a pave and adds it to the plot."""
        pave = TPaveText(x1, y1, x2, y2, 'NDC')
        n = len(self._container_draw)
        pave.SetTextFont(42)
        pave.SetTextSize(0.025)
        if border:
            pave.SetBorderSize(1)
            pave.SetFillColor(0)
        self.add(pave)
        return (lambda n: lambda s: self._container_draw[n].AddText(s))(n)

    def add_line(self, y, lc=None, lw=None, ls=None):
        """Add a line marking a constant value to the plot."""
        line = TF1(
            'line{0}'.format(y), '{0}'.format(y), self.xaxis().GetXmin(),
            self.xaxis().GetXmax()
        )
        for function, param, default in (
            (line.SetLineColor, lc, 1), (line.SetLineWidth, lw, 1),
            (line.SetLineStyle, ls, 3)
        ):
            if param is None:
                function(default)
            else:
                function(param)
        self.add(line)
        return line

    def save(self, name):
        """Save the plot to a file."""
        if name.startswith('.'):
            if not exists('out'):
                mkdir('out')
            name = 'out/{0}{1}'.format(self.GetName(), name)
        self.SaveAs(name)

    def save_pdf(self):
        """Save the plot as PDF."""
        self.save('.pdf')

    def save_png(self):
        """Save the plot as PNG."""
        self.save('.png')

    def save_c(self):
        """Save the plot as C macro."""
        self.save('.C')

class SingleGraphBase(PlotBase):
    """Core functionality for plots of one graph.

    __init__: Initialize.
    xaxis: Return x-axis of graph.
    yaxis: Return y-axis of histogram.
    """

    def __init__(self, graph, name='Plot', fill=4954, workinprogress=False):
        """Initialize core functionality of a graph."""
        PlotBase.__init__(self, name, fill, workinprogress)
        self._graph = graph
        self._graph.SetName('{0}_graph'.format(name))
        self._graph.SetTitle('')
        self._drawoption = ''

    def xaxis(self):
        """Return x-axis of histogram."""
        return self._graph.GetXaxis()

    def yaxis(self):
        """Return y-axis of histogram."""
        return self._graph.GetYaxis()

    def _draw_first(self):
        self._graph.Draw(self._drawoption)

class SingleHistBase(SingleGraphBase):
    """Core functionalitiy for plots of one histogram.

    __init__: Initialize.
    get_bin: Return bin value.
    set_bin: Set bin value.
    """

    def __init__(self, hist, name='Plot', fill=4954, workinprogress=False):
        """Initialize core functionality of a histogram."""
        SingleGraphBase.__init__(self, hist, name, fill, workinprogress)
        self._graph.SetName('{0}_hist'.format(name))

    def get_bin(self, xbin, ybin=None):
        """Return value of single bin."""
        if ybin is None:
            return self._graph.GetBinContent(xbin)
        else:
            return self._graph.GetBinContent(xbin, ybin)

    def set_bin(self, val, xbin, ybin=None):
        """Set value of single bin."""
        if ybin is None:
            self._graph.SetBinContent(xbin, val)
        else:
            self._graph.SetBinContent(xbin, ybin, val)

class ColorBase(SingleHistBase):
    """Core functionality for color plots.

    __init__: Initialize.
    kBird: Create the kBird color scheme.
    zaxis: Return z-axis of histogram.
    palette: Return color palette of histogram.
    """

    def __init__(self, hist, name='ColorPlot', fill=4954, workinprogress=False):
        """Initialize core functionality of a color plot."""
        SingleHistBase.__init__(self, hist, name, fill, workinprogress)
        self._above = True
        self._drawoption = 'COLZ'
        self.kBird()

    @staticmethod
    def kBird():
        """Create the kBird color scheme."""
        red = array('d', [0.2082, 0.0592, 0.0780, 0.0232, 0.1802,
                          0.5301, 0.8186, 0.9956, 0.9764])
        grn = array('d', [0.1664, 0.3599, 0.5041, 0.6419, 0.7178,
                          0.7492, 0.7328, 0.7862, 0.9832])
        blu = array('d', [0.5293, 0.8684, 0.8385, 0.7914, 0.6425,
                          0.4662, 0.3499, 0.1968, 0.0539])
        stp = array('d', [0.0   , 0.125 , 0.25  , 0.375 , 0.5   ,
                          0.625 , 0.75  , 0.875 , 1.0   ])
        return TColor.CreateGradientColorTable(9, stp, red, grn, blu, 255)

    def zaxis(self):
        """Return z-axis of histogram."""
        return self._graph.GetZaxis()

    def palette(self):
        """Return color palette of histogram."""
        return self._graph.GetListOfFunctions().FindObject('palette')

    def _draw_second(self):
        if self._ztitle is not None:
            self.zaxis().SetTitleOffset(0.9)
            self.palette().SetX2NDC(0.929)
