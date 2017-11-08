"""Import model functions for double Gaussian models."""

from lib.compile import require
require('plugins/src', 'DoubleGauss_V1')
require('plugins/src', 'DoubleGauss_V2')
require('plugins/src', 'DoubleGaussOverlap')

from ROOT import DoubleGauss_V1, DoubleGauss_V2, DoubleGaussOverlap
