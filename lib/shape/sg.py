"""Provides classes for single Gaussian beam shape models.

SingleGaussCore: Base class (abstract).
SingleGauss: single Gaussian beam shape model with correlations.
SingleGaussUncorrelated: single Gaussian beam shape model without correlations.
"""

from math import exp, pi

from lib.shape.shape import BeamShapeCore
from lib.vars import RealVar
from plugins.sg import SingleGauss_V1, SingleGauss_V2, SingleGaussOverlap

class SingleGaussCore(BeamShapeCore):
    """Core functionality for single Gaussian beam shapes (abstract).

    physics_parameters: List of names of physics parameters.
    __init__: Initialize.
    dof: Return parameter number.
    model_functions: Create fit model functions.
    gauss: Compute simple Gaussian.
    overlap: Compute beam shape overlap.
    assign_overlap: Assign parameter values to overlap function.
    """

    physics_parameters = [
        'xWidthN1', 'xWidthN2', 'yWidthN1', 'yWidthN2', 'rhoN1', 'rhoN2',
        'w1N', 'w2N',
        'xVtxRes', 'yVtxRes'
    ]

    def __init__(self, crange=(-10.0, 10.0)):
        """Initialize core functionality of single Gaussian beam shapes.

        crange: 2-tuple of limits of the coordinates.
        """
        BeamShapeCore.__init__(self, crange)

    @staticmethod
    def dof():
        """Return number of independent parameters."""
        return 10

    def model_functions(self):
        """Create functions for the fit model of the Beam Imaging scan."""
        x1 = SingleGauss_V1(
            'beam1RestVerticesUnfold_XScan',
            'beam1RestVerticesUnfold_XScan',
            self.xvar(), self.yvar(),
            self.parameter('x011'), self.parameter('y011'),
            self.parameter('rhoN1'),
            self.parameter('xWidthN1'), self.parameter('yWidthN1'),
            self.parameter('yWidthN2'),
            self.parameter('xVtxRes'), self.parameter('yVtxRes')
        )
        y1 = SingleGauss_V2(
            'beam1RestVerticesUnfold_YScan',
            'beam1RestVerticesUnfold_YScan',
            self.xvar(), self.yvar(),
            self.parameter('x012'), self.parameter('y012'),
            self.parameter('rhoN1'),
            self.parameter('xWidthN1'), self.parameter('yWidthN1'),
            self.parameter('xWidthN2'),
            self.parameter('xVtxRes'), self.parameter('yVtxRes')
        )
        x2 = SingleGauss_V1(
            'beam2RestVerticesUnfold_XScan',
            'beam2RestVerticesUnfold_XScan',
            self.xvar(), self.yvar(),
            self.parameter('x021'), self.parameter('y021'),
            self.parameter('rhoN2'),
            self.parameter('xWidthN2'), self.parameter('yWidthN2'),
            self.parameter('yWidthN1'),
            self.parameter('xVtxRes'), self.parameter('yVtxRes')
        )
        y2 = SingleGauss_V2(
            'beam2RestVerticesUnfold_YScan',
            'beam2RestVerticesUnfold_YScan',
            self.xvar(), self.yvar(),
            self.parameter('x022'), self.parameter('y022'),
            self.parameter('rhoN2'),
            self.parameter('xWidthN2'), self.parameter('yWidthN2'),
            self.parameter('xWidthN1'),
            self.parameter('xVtxRes'), self.parameter('yVtxRes')
        )
        return [x1, y1, x2, y2]

    def gauss(self, x, y, x0, y0, xwidth, ywidth, rho):
        xx = (x-x0) / xwidth
        yy = (y-y0) / ywidth
        return 0.5 * self.factor / (pi*(1.0-rho**2)**0.5*abs(xwidth*ywidth)) \
               * exp(-0.5/(1.0-rho**2)*(xx**2+yy**2-2.0*rho*xx*yy))

    def overlap(self, x, par):
        """Compute product of the beam shapes.

        x: list of variable values (two entries).
        par: list of parameter values (10 entries).
        """
        xx = x[0]
        yy = x[1]
        x01 = par[0]
        y01 = par[1]
        x02 = par[2]
        y02 = par[3]
        xWidthN1 = par[4]
        yWidthN1 = par[5]
        xWidthN2 = par[6]
        yWidthN2 = par[7]
        rhoN1 = par[8]
        rhoN2 = par[9]
        try:
            beamN1 = self.gauss(xx, yy, x01, y01, xWidthN1, yWidthN1, rhoN1)
            beamN2 = self.gauss(xx, yy, x02, y02, xWidthN2, yWidthN2, rhoN2)
            return beamN1 * beamN2
        except (ArithmeticError, ValueError) as error:
            print '<<< Error (overlap):', error
            return -1.0

    def assign_overlap(self, overlap, random=None):
        """Assigns current parameter values to overlap function."""
        overlap = BeamShapeCore.assign_overlap(self, overlap, random)
        names = ['xWidthN1', 'yWidthN1', 'xWidthN2', 'yWidthN2',
                 'rhoN1', 'rhoN2']
        overlap = self._assign_overlap(overlap, names, 4, random)
        return overlap

    def overlap_func(self):
        """Return beam shape product as TF2."""
        overlap = SingleGaussOverlap(self.factor)
        overlap = self.assign_overlap(overlap)
        return overlap

class SingleGauss(SingleGaussCore):
    """Single Gaussian beam shape, including correlations.

    fit_parameters: List of names of fit parameters.
    __init__: Initialize.
    name: Return model name.
    """

    fit_parameters = [
        'xWidthN1', 'xWidthN2', 'yWidthN1', 'yWidthN2', 'rhoN1', 'rhoN2',
        'x011', 'x012', 'x021', 'x022', 'y011', 'y012', 'y021', 'y022'
    ]

    def __init__(self, crange=(-10.0, 10.0)):
        """Initialize single Gaussian beam shape.

        crange: 2-tuple of limits of the coordinates.
        """
        SingleGaussCore.__init__(self, crange)
        for name in ['xWidthN1', 'xWidthN2', 'yWidthN1', 'yWidthN2']:
            # Width
            par = RealVar(name, 1.3, 3.0)
            self._physics_parameters[name] = par
        for name in ['rhoN1', 'rhoN2']:
            # Correlation parameter
            par = RealVar(name, -0.48, 0.48)
            self._physics_parameters[name] = par
        for name in ['w1N', 'w2N']:
            # Weight
            par = RealVar(name, 1.0)
            self._physics_parameters[name] = par

    @staticmethod
    def name():
        """Return (unique) abbreviation of model name."""
        return 'SG'

class SingleGaussUncorrelated(SingleGauss):
    """Single Gaussian beam shape, without correlations.

    fit_parameters: List of names of fit parameters.
    __init__: Initialize.
    name: Return model name.
    """

    fit_parameters = [
        'xWidthN1', 'xWidthN2', 'yWidthN1', 'yWidthN2',
        'x011', 'x012', 'x021', 'x022', 'y011', 'y012', 'y021', 'y022'
    ]

    def __init__(self, crange=(-10.0, 10.0)):
        """Initialize single Gaussian beam shape.

        crange: 2-tuple of limits of the coordinates.
        """
        SingleGauss.__init__(self, crange)
        for name in ['rhoN1', 'rhoN2']:
            # Correlation parameter
            par = self.parameter(name)
            par.setVal(0.0)
            par.setConstant()

    @staticmethod
    def name():
        """Return (unique) abbreviation of model name."""
        return 'noCorr'
