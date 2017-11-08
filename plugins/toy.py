"""Import ToyGenerator class from ROOT.

ToyGenerator: Wrapper class for corresponding ROOT class.
"""

from lib.compile import require
require('plugins/src', 'ToyGenerator')

from numpy import array

from ROOT import Double, Long, ToyGenerator as RootToyGenerator

class ToyGenerator(RootToyGenerator):
    """Wrapper class to include the ROOT class ToyGenerator.

    __init__: Set up a ROOT object of type ToyGenerator.
    Integral: Compute integral of function.
    SetResolution: Define value of vertex resolution.
    GetRandom2: Draw two coordinates.
    GenerateToys: Perform MC generation of BI scan.
    """

    def __init__(self, func, rand=None, resx=None, resy=None):
        """Initialize MC generation of BI scans.

        func: Beam shape product as TF2.
        rand (optional): Random number generator to be used (new TRandom3
            created otherwise).
        resx, resy: Vertex resolutions.
        """
        if rand is None:
            RootToyGenerator.__init__(self, func)
        else:
            RootToyGenerator.__init__(self, func, rand)
        if resx is None:
            resx = 0.0
        if resy is None:
            resy = resx
        self.SetResolution(resx, resy)

    def GetRandom2(self):
        """Draw two coordinates from PDF."""
        x = Double(0.0)
        y = Double(0.0)
        RootToyGenerator.GetRandom2(self, x, y)
        return float(x), float(y)

    def SimulateScan(self, c, pos, nbins=95):
        """Generate a toy BI scan.

        c: Index of the position parameter of the BI scan steps.
        pos: Lists of the scan steps of the beam.
        Returns: Histogram.
        """
        p = array(pos)
        nevents = Long(0)
        result = RootToyGenerator.GenerateToys(
            self, len(pos), c, p, nbins, nevents
        )
        return result, float(nevents)
