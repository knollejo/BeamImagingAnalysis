"""Import model functions for triple Gaussian models."""

from lib.compile import require
require('plugins/src', 'TripleGauss_V1')
require('plugins/src', 'TripleGauss_V2')
require('plugins/src', 'TripleGaussOverlap')

from ROOT import TripleGauss_V1, TripleGauss_V2, TripleGaussOverlap
