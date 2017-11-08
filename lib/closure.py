"""Provides functions for a closure test.

generate_toys: Generate toy data for BI scan.
"""

from ROOT import TRandom3

from plugins.toy import ToyGenerator

def generate_toys(
    overlap, vtxresx, vtxresy=None, rand=None, nbins=95, verbose=False
):
    """Generate toy data of Beam Imaging scan.

    overlap: Beam shape overlap function model (TF2).
    vtxresx, vtxresy: Vertex resolution.
    rand: Random number generator (if not given: use a TRandom3).
    nbins: Number of bins in histograms.
    """
    if rand is None:
        rand = TRandom3()
        rand.SetSeed(0)
    if vtxresy is None:
        vtxresy = vtxresx
    overlap.SetNpx(500)
    overlap.SetNpy(500)
    generator = ToyGenerator(overlap, rand, vtxresx, vtxresy)
    generator.SetVerbose(verbose)

    pos = [-9.0+i*1.0 for i in range(19)]
    hists = []
    nevents = []
    for i in ('2', '1'):
        for c in ('X', 'Y'):
            name = 'Beam{0}Move{1}_Add'.format(i, c)
            par = {'1': 0, '2': 2}[i] + {'X': 0, 'Y': 1}[c]
            hist, nevent = generator.SimulateScan(par, pos, nbins)
            hist.SetName(name)
            hists.append(hist)
            nevents.append(nevent)
    return hists, nevents
