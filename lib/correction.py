"""Provides functions for determining xy correlation correction.

compute_correction: COmpute xy correlation correction.
"""

from ROOT import TRandom3

from lib.io import RootTree
from plugins.vdm import VdmSimulator

def compute_correction(
    overlap, steps=25, n=100, factor=100.0, rand=None, extended=True,
    eachtoy=None
):
    """Compute the xy correlation correction by simulation of VdM scans.

    overlap: Beam shape overlap function model (TF2).
    steps: Number of VdM steps to be simulated.
    n: Number of VdM scans to be simulated.
    factor: Factor by which model shapes are multiplied.
    rand: Random number generator (if not given: use a TRandom3).
    extended: Return full tree with information, correction only otherwise
    eachtoy: Function taking simulator and random number generator as argument,
        to be executed before each new toy generation.
    """
    if eachtoy is None:
        eachtoy = lambda s, r: s
    overlap.SetNpx(500)
    overlap.SetNpy(500)
    if rand is None:
        rand = TRandom3()
        rand.SetSeed(0)
    simulator = VdmSimulator(overlap)
    simulator.SetParametrized(False)
    overlapTrue = simulator.Integral() / factor**2
    if overlapTrue == 0.0:
        if extended:
            return None
        else:
            return -1.0, -1.0, -1.0
    if extended:
        tree = RootTree('corrTree', 'VdM simulation and correction results')
        for field in [
            'mu1_X', 'mu1_Y', 'mu2_X', 'mu2_Y',
            'sigma1_X', 'sigma1_Y', 'sigma2_X', 'sigma2_Y',
            'const_X', 'const_Y',
            'peak_X', 'peak_Y', 'area_X', 'area_Y',
            'overlapTrue', 'overlapFit', 'overlapDiff',
            'chiSq_X', 'chiSq_Y', 'sigmaDiff_X', 'sigmaDiff_Y'
        ]:
            tree.branch_f(field)
        tree.branch_f('nEvents', 2)
        tree.set('overlapTrue', overlapTrue)
    else:
        result_fit = []
        result_dif = []

    stepsX1 = [0.0 for i in range(steps)]
    stepsX2 = [i-0.5*(steps-1) for i in range(steps)]
    stepsY1 = [0.0 for i in range(steps)]
    stepsY2 = [i-0.5*(steps-1) for i in range(steps)]
    for nToy in range(n):
        simulator = eachtoy(simulator, rand)

        # X scan
        simulator.mu1_low = 8.5
        simulator.mu1_high = 14.6
        simulator.mu2_low = 8.2
        simulator.mu2_high = 15.1
        simulator.sigma1_low = 1.0
        simulator.sigma1_high = 2.9
        simulator.sigma2_low = 2.1
        simulator.sigma2_high = 4.0
        resX, peak_X, area_X, chiSq_X, nevents_X = \
            simulator.simulate(0, 2, stepsX1, stepsX2)

        # Y scan
        simulator.mu1_low = 8.1
        simulator.mu1_high = 15.8
        simulator.mu2_low = 8.4
        simulator.mu2_high = 15.6
        simulator.sigma1_low = 1.0
        simulator.sigma1_high = 2.5
        simulator.sigma2_low = 2.11
        simulator.sigma2_high = 4.0
        resY, peak_Y, area_Y, chiSq_Y, nevents_Y = \
            simulator.simulate(1, 3, stepsY1, stepsY2)

        overlapFit = peak_X/area_X * peak_Y/area_Y
        overlapDiff = (overlapFit-overlapTrue)/overlapTrue
        if extended:
            params = {
                'X': resX.floatParsFinal(),
                'Y': resY.floatParsFinal()
            }
            for field in [
                'peak_X', 'peak_Y', 'area_X', 'area_Y',
                'overlapFit', 'overlapDiff', 'chiSq_X', 'chiSq_Y'
            ]:
                tree.set(field, locals()[field])
            tree.set('nEvents', nevents_X, index=0)
            tree.set('nEvents', nevents_X, index=1)
            for c in ('X', 'Y'):
                for field in ['mu1', 'mu2', 'sigma1', 'const']:
                    name = '{0}_{1}'.format(field, c)
                    value = params[c].find(field).getValV()
                    tree.set(name, value)
                try:
                    name = 'sigmaDiff_{0}'.format(c)
                    value = params[c].find('sigmaDiff').getValV()
                    tree.set(name, value)
                    name = 'sigma2_{0}'.format(c)
                    value = params[c].find('sigma1').getValV() \
                          + params[c].find('sigmaDiff').getValV()
                    tree.set(name, value)
                except AttributeError as e:
                    name = 'sigma2_{0}'.format(c)
                    value = params[c].find('sigma2').getValV()
                    tree.set(name, value)
            tree.Fill()
        else:
            result_fit.append(overlapFit)
            result_dif.append(overlapDiff)

    if extended:
        return tree
    else:
        return overlapTrue, result_fit, result_dif
