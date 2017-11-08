"""Import model functions for single Gaussian models."""

from lib.compile import require
require('plugins/src', 'SingleGauss_V1')
require('plugins/src', 'SingleGauss_V2')
require('plugins/src', 'SingleGaussOverlap')

from ROOT import SingleGauss_V1, SingleGauss_V2, SingleGaussOverlap
