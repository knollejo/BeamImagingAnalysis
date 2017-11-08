"""Import VdmSimulator class from ROOT.

VdmSimulator: Wrapper class for corresponding ROOT class.
"""

from lib.compile import require
require('plugins/src', 'VdmSimulator')

from numpy import array

from ROOT import Double, VdmSimulator as RootVdmSimulator

class VdmSimulator(RootVdmSimulator):
    """Wrapper class to include the ROOT class VdmSimulator.

    __init__: Set up a ROOT object of type VdmSimulator.
    Integral: Compute integral of function.
    SimulateScan: Perform MC simulation of VdM scan.
    """

    def __init__(self, func, rand=None):
        """Initialize MC simulation of VdM scans.

        func: Beam shape product as TF2.
        rand (optional): Random number generator to be used (new TRandom3
            created otherwise).
        """
        if rand is None:
            RootVdmSimulator.__init__(self, func)
        else:
            RootVdmSimulator.__init__(self, func, rand)

    def simulate(self, c1, c2, pos1, pos2):
        """Perform a MC simulation of a VdM scan.

        c1, c2: Indices of the position parameters of the VdM scan steps.
        pos1, pos2: Lists of the scan steps of the two beams.
        Returns: 4-tuple with RooFitResult, peak value, area value, chi-squared.
        """
        p1 = array(pos1)
        p2 = array(pos2)
        peak = Double(0.0)
        area = Double(0.0)
        chisq = Double(0.0)
        nevents = Double(0.0)
        result = RootVdmSimulator.SimulateScan(
            self, len(pos1), c1, c2, p1, p2, peak, area, chisq, nevents
        )
        return result, float(peak), float(area), float(chisq), float(nevents)
