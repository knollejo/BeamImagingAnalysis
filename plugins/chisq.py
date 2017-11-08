"""Import MyRooChi2Var class from ROOT.

chi2FitTo: Perform a chi-square minimization using MyRooChi2Var.
"""

from lib.compile import require
require('plugins/src', 'MyRooChi2Var')

from ROOT import Double, MyRooChi2Var as Chi2Var, RooMinimizer

def chi2FitTo(pdf, data):
    """Perform a chi-square minimization using MyRooChi2Var."""
    chi2 = Chi2Var('chi2', 'chi2', pdf, data)
    m = RooMinimizer(chi2)
    m.setPrintEvalErrors(10)
    m.setPrintLevel(1)
    m.optimizeConst(1)
    m.setVerbose(0)
    m.minimize('Minuit', 'minuit')
    m.hesse()
    return m.save('fitResult', 'Result of fit')
