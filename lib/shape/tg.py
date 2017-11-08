"""Provides classes for triple Gaussian beam shape models.

TripleGaussCore: Base class (abstract).
TripleGaussFit: triple Gaussian beam shape model (parametrized for fit).
TripleGaussToy: triple Gaussian beam shape model (parametrized for MC).
SuperDoubleGaussFit: sup-d Gaussian beam shape model (parametrized for fit).
SuperDoubleGaussFit: sup-d Gaussian beam shape model (parametrized for MC).
"""

from math import cos, pi, sin

from lib.shape.dg import DoubleGaussCore
from lib.vars import ArgList, FormulaVar, RealVar
from plugins.tg import TripleGauss_V1, TripleGauss_V2, TripleGaussOverlap

class TripleGaussCore(DoubleGaussCore):
    """Core functionality for triple Gaussian beam shapes (abstract).

    physics_parameters: List of names of physics parameters.
    __init__: Initialize.
    dof: Return parameter number.
    model_functions: Create fit model functions.
    overlap: Compute beam shape overlap.
    assign_overlap: Assign parameter values to overlap function.
    """

    physics_parameters = [
        'xWidthN1', 'xWidthN2', 'yWidthN1', 'yWidthN2',
        'rhoN1', 'rhoN2',
        'w1N', 'w2N',
        'xWidthM1', 'xWidthM2', 'yWidthM1', 'yWidthM2',
        'rhoM1', 'rhoM2',
        'w1M', 'w2M',
        'xWidthW1', 'xWidthW2', 'yWidthW1', 'yWidthW2',
        'rhoW1', 'rhoW2',
        'w1W', 'w2W',
        'xVtxRes', 'yVtxRes'
    ]

    def __init__(self, crange=(-10.0, 10.0)):
        """Initialize core functionality of triple Gaussian beam shapes.

        crange: 2-tuple of limits of the coordinates.
        """
        DoubleGaussCore.__init__(self, crange)

    @staticmethod
    def dof():
        """Return number of independent parameters."""
        return 26

    def model_functions(self):
        """Create functions for the fit model of the Beam Imaging scan."""
        x1 = TripleGauss_V1(
            'beam1RestVerticesUnfold_XScan',
            'beam1RestVerticesUnfold_XScan',
            self.xvar(), self.yvar(),
            self.parameter('x011'), self.parameter('y011'),
            self.parameter('w1N'), self.parameter('w1M'),
            self.parameter('rhoN1'),
            self.parameter('xWidthN1'), self.parameter('yWidthN1'),
            self.parameter('rhoM1'),
            self.parameter('xWidthM1'), self.parameter('yWidthM1'),
            self.parameter('rhoW1'),
            self.parameter('xWidthW1'), self.parameter('yWidthW1'),
            self.parameter('w2N'), self.parameter('w2M'),
            self.parameter('yWidthN2'), self.parameter('yWidthM2'),
            self.parameter('yWidthW2'),
            self.parameter('xVtxRes'), self.parameter('yVtxRes')
        )
        y1 = TripleGauss_V2(
            'beam1RestVerticesUnfold_YScan',
            'beam1RestVerticesUnfold_YScan',
            self.xvar(), self.yvar(),
            self.parameter('x012'), self.parameter('y012'),
            self.parameter('w1N'), self.parameter('w1M'),
            self.parameter('rhoN1'),
            self.parameter('xWidthN1'), self.parameter('yWidthN1'),
            self.parameter('rhoM1'),
            self.parameter('xWidthM1'), self.parameter('yWidthM1'),
            self.parameter('rhoW1'),
            self.parameter('xWidthW1'), self.parameter('yWidthW1'),
            self.parameter('w2N'), self.parameter('w2M'),
            self.parameter('xWidthN2'), self.parameter('xWidthM2'),
            self.parameter('xWidthW2'),
            self.parameter('xVtxRes'), self.parameter('yVtxRes')
        )
        x2 = TripleGauss_V1(
            'beam2RestVerticesUnfold_XScan',
            'beam2RestVerticesUnfold_XScan',
            self.xvar(), self.yvar(),
            self.parameter('x021'), self.parameter('y021'),
            self.parameter('w2N'), self.parameter('w2M'),
            self.parameter('rhoN2'),
            self.parameter('xWidthN2'), self.parameter('yWidthN2'),
            self.parameter('rhoM2'),
            self.parameter('xWidthM2'), self.parameter('yWidthM2'),
            self.parameter('rhoW2'),
            self.parameter('xWidthW2'), self.parameter('yWidthW2'),
            self.parameter('w1N'), self.parameter('w1M'),
            self.parameter('yWidthN1'), self.parameter('yWidthM1'),
            self.parameter('yWidthW1'),
            self.parameter('xVtxRes'), self.parameter('yVtxRes')
        )
        y2 = TripleGauss_V2(
            'beam2RestVerticesUnfold_YScan',
            'beam2RestVerticesUnfold_YScan',
            self.xvar(), self.yvar(),
            self.parameter('x022'), self.parameter('y022'),
            self.parameter('w2N'), self.parameter('w2M'),
            self.parameter('rhoN2'),
            self.parameter('xWidthN2'), self.parameter('yWidthN2'),
            self.parameter('rhoM2'),
            self.parameter('xWidthM2'), self.parameter('yWidthM2'),
            self.parameter('rhoW2'),
            self.parameter('xWidthW2'), self.parameter('yWidthW2'),
            self.parameter('w1N'), self.parameter('w1M'),
            self.parameter('xWidthN1'), self.parameter('xWidthM1'),
            self.parameter('xWidthW1'),
            self.parameter('xVtxRes'), self.parameter('yVtxRes')
        )
        return [x1, y1, x2, y2]

    def overlap(self, x, par):
        """Compute product of the beam shapes.

        x: list of variable values (two entries).
        par: list of parameter values (26 entries).
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
        w1N = par[10]
        w2N = par[11]
        xWidthM1 = par[12]
        yWidthM1 = par[13]
        xWidthM2 = par[14]
        yWidthM2 = par[15]
        rhoM1 = par[16]
        rhoM2 = par[17]
        w1M = par[18]
        w2M = par[19]
        xWidthW1 = par[20]
        yWidthW1 = par[21]
        xWidthW2 = par[22]
        yWidthW2 = par[23]
        rhoW1 = par[24]
        rhoW2 = par[25]
        try:
            beamN1 = self.gauss(xx, yy, x01, y01, xWidthN1, yWidthN1, rhoN1)
            beamM1 = self.gauss(xx, yy, x01, y01, xWidthM1, yWidthM1, rhoM1)
            beamW1 = self.gauss(xx, yy, x01, y01, xWidthW1, yWidthW1, rhoW1)
            beamN2 = self.gauss(xx, yy, x02, y02, xWidthN2, yWidthN2, rhoN2)
            beamM2 = self.gauss(xx, yy, x02, y02, xWidthM2, yWidthM2, rhoM2)
            beamW2 = self.gauss(xx, yy, x02, y02, xWidthW2, yWidthW2, rhoW2)
            return (w1N*beamN1+w1M*beamM1+(1.0-w1N-w1M)*beamW1) \
                 * (w2N*beamN2+w2M*beamM2+(1.0-w2N-w2M)*beamW2)
        except (ArithmeticError, ValueError) as error:
            print '<<< Error (overlap):', error
            return -1.0

    def assign_overlap(self, overlap, random=None):
        overlap = DoubleGaussCore.assign_overlap(self, overlap, random)
        names = ['w1M', 'w2M', 'xWidthW1', 'yWidthW1', 'xWidthW2', 'yWidthW2',
                 'rhoW1', 'rhoW2']
        overlap = self._assign_overlap(overlap, names, 18, random)
        return overlap

    def overlap_func(self):
        """Return beam shape product as TF2."""
        overlap = TripleGaussOverlap(self.factor)
        overlap = self.assign_overlap(overlap)
        return overlap

class TripleGaussFit(TripleGaussCore):
    """Triple Gaussian beam shape, parametrized for fit.

    fit_parameters: List of names of fit parameters.
    __init__: Initialize.
    name: Return model name.
    """

    fit_parameters = [
        'xWidthN1', 'xWidthN2', 'yWidthN1', 'yWidthN2', 'rhoN1', 'rhoN2',
        'xWidthM1Diff', 'xWidthM2Diff', 'yWidthM1Diff', 'yWidthM2Diff',
        'rhoM1', 'rhoM2',
        'xWidthW1Diff', 'xWidthW2Diff', 'yWidthW1Diff', 'yWidthW2Diff',
        'rhoW1', 'rhoW2',
        'theta1', 'theta2', 'phi1', 'phi2',
        'x011', 'x012', 'x021', 'x022', 'y011', 'y012', 'y021', 'y022'
    ]

    def __init__(self, crange=(-10.0, 10.0)):
        """Initialize triple Gaussian beam shape.

        crange: 2-tuple of limits of the coordinates.
        """
        TripleGaussCore.__init__(self, crange)
        for nameA, nameB, nameC in [
            ('xWidthN1', 'xWidthM1', 'xWidthW1'),
            ('xWidthN2', 'xWidthM2', 'xWidthW2'),
            ('yWidthN1', 'yWidthM1', 'yWidthW1'),
            ('yWidthN2', 'yWidthM2', 'yWidthW2')
        ]:
            # Narrow width
            parA = RealVar(nameA, 1.3, 3.0)
            self._physics_parameters[nameA] = parA
            # Difference of narrow width to medium width
            nameD = '{0}Diff'.format(nameB)
            parD = RealVar(nameD, 0.01, 1.7)
            self._fit_parameters[nameD] = parD
            # Medium width
            formulaB = '{0}+{1}'.format(nameA, nameD)
            arglistB = ArgList([nameA, nameD], self.parameter)
            errorB = (
                lambda a,d: lambda p:
                (p(a).err(p)**2+p(d).err(p)**2)**0.5
            )(nameA, nameD)
            parB = FormulaVar(nameB, formulaB, arglistB, errorB)
            self._physics_parameters[nameB] = parB
            # Difference of medium width to wide width
            nameE = '{0}Diff'.format(nameC)
            parE = RealVar(nameE, 0.01, 1.7)
            self._fit_parameters[nameE] = parE
            # Wide width
            formulaC = '{0}+{1}'.format(nameB, nameE)
            arglistC = ArgList([nameB, nameE], self.parameter)
            errorC = (
                lambda b,e: lambda p:
                (p(b).err(p)**2+p(e).err(p)**2)**0.5
            )(nameB, nameE)
            parC = FormulaVar(nameC, formulaC, arglistC, errorC)
            self._physics_parameters[nameC] = parC
        for name in ['rhoN1', 'rhoN2', 'rhoM1', 'rhoM2', 'rhoW1', 'rhoW2']:
            # Correlation parameter
            par = RealVar(name, -0.48, 0.48)
            self._physics_parameters[name] = par
        for nameA, nameB, nameC, nameD, nameE in [
            ('w1N', 'w1M', 'w1W', 'theta1', 'phi1'),
            ('w2N', 'w2M', 'w2W', 'theta2', 'phi2')
        ]:
            # First weight parameter
            parD = RealVar(nameD, 0.0, 0.5*pi)
            self._fit_parameters[nameD] = parD
            # Second weight parameter
            parE = RealVar(nameE, 0.0, 0.5*pi)
            self._fit_parameters[nameE] = parE
            # Weight of narrow component
            formulaA = 'cos({0})^2'.format(nameD)
            arglistA = ArgList([nameD], self.parameter)
            errorA = (
                lambda d: lambda p:
                2.0*sin(p(d).val())*cos(p(d).val())*p(d).err(p)
            )(nameD)
            parA = FormulaVar(nameA, formulaA, arglistA, errorA)
            self._physics_parameters[nameA] = parA
            # Weight of medium component
            formulaB = 'sin({0})^2*cos({1})^2'.format(nameD, nameE)
            arglistB = ArgList([nameD, nameE], self.parameter)
            errorB = (
                lambda d,e: lambda p:
                2.0*sin(p(d).val())*cos(p(e).val())*((p(d).err(p)
                *cos(p(d).val())*cos(p(e).val()))**2+(p(e).err(p)
                *sin(p(d).val())*sin(p(e).val()))**2)**0.5
            )(nameD, nameE)
            parB = FormulaVar(nameB, formulaB, arglistB, errorB)
            self._physics_parameters[nameB] = parB
            # Weight of wide component
            formulaC = 'sin({0})^2*sin({1})^2'.format(nameD, nameE)
            arglistC = ArgList([nameD, nameE], self.parameter)
            errorC = (
                lambda d,e: lambda p:
                2.0*sin(p(d).val())*sin(p(e).val())*((p(d).err(p)
                *cos(p(d).val())*sin(p(e).val()))**2+(p(e).err(p)
                *sin(p(d).val())*cos(p(e).val()))**2)**0.5
            )(nameD, nameE)
            parC = FormulaVar(nameC, formulaC, arglistC, errorC)
            self._physics_parameters[nameC] = parC

    @staticmethod
    def name():
        """Return (unique) abbreviation of model name."""
        return 'TG'

class TripleGaussToy(TripleGaussCore):
    """Triple Gaussian beam shape, parametrized for toy model generation.

    fit_parameters: List of names of free toy model parameters.
    __init__: Initialize.
    name: Return model name.
    """

    fit_parameters = [
        'xWidthN1', 'xWidthN2', 'yWidthN1', 'yWidthN2', 'rhoN1', 'rhoN2',
        'xWidthM1', 'xWidthM2', 'yWidthM1', 'yWidthM2', 'rhoM1', 'rhoM2',
        'xWidthW1', 'xWidthW2', 'yWidthW1', 'yWidthW2', 'rhoW1', 'rhoW2',
        'w1N', 'w2N', 'w1MFraction', 'w2MFraction',
        'x011', 'x012', 'x021', 'x022', 'y011', 'y012', 'y021', 'y022'
    ]

    def __init__(self, crange=(-10.0, 10.0)):
        """Initialize triple Gaussian beam shape.

        crange: 2-tuple of limits of the coordinates.
        """
        TripleGaussCore.__init__(self, crange)
        for name in [
            'xWidthN1', 'xWidthN2', 'yWidthN1', 'yWidthN2',
            'xWidthM1', 'xWidthM2', 'yWidthM1', 'yWidthM2',
            'xWidthW1', 'xWidthW2', 'yWidthW1', 'yWidthW2'
        ]:
            # Width
            par = RealVar(name, 1.3, 3.0)
            self._physics_parameters[name] = par
        for name in ['rhoN1', 'rhoN2', 'rhoM1', 'rhoM2', 'rhoW1', 'rhoW2']:
            # Correlation parameter
            par = RealVar(name, -0.48, 0.48)
            self._physics_parameters[name] = par
        for nameA, nameB, nameC in [
            ('w1N', 'w1M', 'w1W'), ('w2N', 'w2M', 'w2W')
        ]:
            # Weight of narrow component
            parA = RealVar(nameA, 0.0, 1.0)
            self._physics_parameters[nameA] = parA
            # Fraction of weight of medium component w.r.t. wide component
            nameD = '{0}Fraction'.format(nameB)
            parD = RealVar(nameD, 0.0, 1.0)
            self._fit_parameters[nameD] = parD
            # Weight of medium component
            formulaB = '(1.0-{0})*{1}'.format(nameA, nameD)
            arglistB = ArgList([nameA, nameD], self.parameter)
            errorB = (
                lambda a,d: lambda p:
                ((p(a).err(p)*p(d).val())**2+((1.0-p(a).val())*p(d).err(p))**2
                )**0.5
            )(nameA, nameD)
            parB = FormulaVar(nameB, formulaB, arglistB, errorB)
            self._physics_parameters[nameB] = parB
            # Weight of wide component
            formulaC = '(1.0-{0})*(1.0-{1})'.format(nameA, nameD)
            arglistC = ArgList([nameA, nameD], self.parameter)
            errorC = (
                lambda a,d: lambda p:
                ((p(a).err(p)*(1.0-p(d).val()))**2+((1.0-p(a).val())
                 *p(d).err(p))**2)**0.5
            )(nameA, nameD)
            parC = FormulaVar(nameC, formulaC, arglistC, errorC)
            self._physics_parameters[nameC] = parC

    @staticmethod
    def name():
        """Return (unique) abbreviation of model name."""
        return 'toyTG'

class SuperDoubleGaussFit(TripleGaussCore):
    """Super double Gaussian beam shape, parametrized for fit.

    fit_parameters: List of names of fit parameters.
    __init__: Initialize.
    name: Return model name.
    """

    fit_parameters = [
        'xWidthN1Ratio', 'xWidthN2Ratio', 'yWidthN1Ratio', 'yWidthN2Ratio',
        'rhoN1', 'rhoN2',
        'xWidthM1', 'xWidthM2', 'yWidthM1', 'yWidthM2', 'rhoM1', 'rhoM2',
        'xWidthW1Diff', 'xWidthW2Diff', 'yWidthW1Diff', 'yWidthW2Diff',
        'rhoW1', 'rhoW2',
        'omega1', 'omega2', 'w1MFraction', 'w2MFraction',
        'x011', 'x012', 'x021', 'x022', 'y011', 'y012', 'y021', 'y022'
    ]

    def __init__(self, crange=(-10.0, 10.0)):
        """Initialize super double Gaussian beam shape.

        crange: 2-tuple of limits of the coordinates.
        """
        TripleGaussCore.__init__(self, crange)
        for nameA, nameB, nameC in [
            ('xWidthN1', 'xWidthM1', 'xWidthW1'),
            ('xWidthN2', 'xWidthM2', 'xWidthW2'),
            ('yWidthN1', 'yWidthM1', 'yWidthW1'),
            ('yWidthN2', 'yWidthM2', 'yWidthW2')
        ]:
            # Medium width
            parB = RealVar(nameB, 1.3, 3.0)
            self._physics_parameters[nameB] = parB
            # Ratio of narrow width to medium width
            nameD = '{0}Ratio'.format(nameA)
            parD = RealVar(nameD, 0.1, 0.99)
            self._fit_parameters[nameD] = parD
            # Narrow width
            formulaA = '{0}*{1}'.format(nameB, nameD)
            arglistA = ArgList([nameB, nameD], self.parameter)
            errorA = (
                lambda b,d: lambda p:
                ((p(b).val()*p(d).err(p))**2+(p(d).val()*p(b).err(p))**2)**0.5
            )(nameB, nameD)
            parA = FormulaVar(nameA, formulaA, arglistA, errorA)
            self._physics_parameters[nameA] = parA
            # Difference of wide width to medium width
            nameE = '{0}Diff'.format(nameC)
            parE = RealVar(nameE, 0.01, 1.7)
            self._fit_parameters[nameE] = parE
            # Wide width
            formulaC = '{0}+{1}'.format(nameB, nameE)
            arglistC = ArgList([nameB, nameE], self.parameter)
            errorC = (
                lambda b,e: lambda p:
                (p(b).err(p)**2+p(e).err(p)**2)**0.5
            )(nameB, nameE)
            parC = FormulaVar(nameC, formulaC, arglistC, errorC)
            self._physics_parameters[nameC] = parC
            # Ratio of wide width to medium width
            nameF = '{0}Ratio'.format(nameC)
            formulaF = '{0}/{1}'.format(nameC, nameB)
            arglistF = ArgList([nameC, nameB], self.parameter)
            errorF = (lambda: lambda p: 0.0)()
            parF = FormulaVar(nameF, formulaF, arglistF, errorF)
            self._auxiliary_parameters[nameF] = parF
        for nameA, nameB, nameC in [
            ('rhoN1', 'rhoM1', 'rhoW1'), ('rhoN2', 'rhoM2', 'rhoW2')
        ]:
            nameD = 'xWidthN{0}Ratio'.format(nameA[-1])
            nameE = 'yWidthN{0}Ratio'.format(nameA[-1])
            nameF = 'xWidthW{0}Ratio'.format(nameA[-1])
            nameG = 'yWidthW{0}Ratio'.format(nameA[-1])
            # Correlation parameter of medium component
            parB = RealVar(nameB, -0.48, 0.48)
            self._physics_parameters[nameB] = parB
            # Minimum value of correlation parameter (wide component)
            nameH = '{0}Min'.format(nameC)
            formulaH = ('max(-0.99,({0}-sqrt(1.0-{1})*sqrt(1.0-{2}))/{3}/{4}'
                        '-sqrt(1.0-({1}/{3})^2)*sqrt(1.0-({2}/{4})^2))') \
                       .format(nameB, nameD, nameE, nameF, nameG)
            arglistH = ArgList([nameB, nameD, nameE, nameF, nameG],
                               self.parameter)
            errorH = (lambda: lambda p: 0.0)()
            parH = FormulaVar(nameH, formulaH, arglistH, errorH)
            self._auxiliary_parameters[nameH] = parH
            # Maximum value of correlation parameter (wide component)
            nameI = '{0}Max'.format(nameC)
            formulaI = ('min(0.99,({0}+sqrt(1.0-{1})*sqrt(1.0-{2}))/{3}/{4}'
                        '+sqrt(1.0-({1}/{3})^2)*sqrt(1.0-({2}/{4})^2))') \
                       .format(nameB, nameD, nameE, nameF, nameG)
            arglistI = ArgList([nameB, nameD, nameE, nameF, nameG],
                               self.parameter)
            errorI = (lambda: lambda p: 0.0)()
            parI = FormulaVar(nameI, formulaI, arglistI, errorI)
            self._auxiliary_parameters[nameI] = parI
            # Correlation parameter of wide component
            parC = RealVar(nameC, -0.48, 0.48)
            parC.set_fixed_minimum(parH)
            parC.set_fixed_maximum(parI)
            self._physics_parameters[nameC] = parC
            # Minimum value of correlation parameter (narrow component)
            nameJ = '{0}Min'.format(nameA)
            formulaJ = ('max(-0.99,max({0}/{1}/{2}-sqrt(1.0/{1}^2-1.0)'
                        '*sqrt(1.0/{2}^2-1.0),{5}*{3}*{4}/{1}/{2}'
                        '-sqrt(({3}/{1})^2-1.0)*sqrt(({4}/{2})^2-1.0)))') \
                       .format(nameB, nameD, nameE, nameF, nameG, nameC)
            arglistJ = ArgList([nameB, nameD, nameE, nameF, nameG, nameC],
                               self.parameter)
            errorJ = (lambda: lambda p: 0.0)()
            parJ = FormulaVar(nameJ, formulaJ, arglistJ, errorJ)
            self._auxiliary_parameters[nameJ] = parJ
            # Maximum value of correlation parameter (narrow component)
            nameK = '{0}Max'.format(nameA)
            formulaK = ('min(0.99,min({0}/{1}/{2}+sqrt(1.0/{1}^2-1.0)'
                        '*sqrt(1.0/{2}^2-1.0),{5}*{3}*{4}/{1}/{2}'
                        '+sqrt(({3}/{1})^2-1.0)*sqrt(({4}/{2})^2-1.0)))') \
                       .format(nameB, nameD, nameE, nameF, nameG, nameC)
            arglistK = ArgList([nameB, nameD, nameE, nameF, nameG, nameC],
                               self.parameter)
            errorK = (lambda: lambda p: 0.0)()
            parK = FormulaVar(nameK, formulaK, arglistK, errorK)
            self._auxiliary_parameters[nameK] = parK
            # Correlation parameter of narrow component
            parA = RealVar(nameA, -0.48, 0.48)
            parA.set_fixed_minimum(parJ)
            parA.set_fixed_maximum(parK)
            self._physics_parameters[nameA] = parA
        for nameA, nameB, nameC, nameD in [
            ('w1N', 'w1M', 'w1W', 'omega1'), ('w2N', 'w2M', 'w2W', 'omega2')
        ]:
            nameE = 'xWidthN{0}Ratio'.format(nameD[-1])
            nameF = 'yWidthN{0}Ratio'.format(nameD[-1])
            nameG = 'xWidthW{0}Ratio'.format(nameD[-1])
            nameH = 'yWidthW{0}Ratio'.format(nameD[-1])
            nameI = 'rhoN{0}'.format(nameD[-1])
            nameJ = 'rhoM{0}'.format(nameD[-1])
            nameK = 'rhoW{0}'.format(nameD[-1])
            # Fraction of weight of medium component w.r.t. wide component
            nameL = '{0}Fraction'.format(nameB)
            parL = RealVar(nameL, 0.0, 1.0)
            self._fit_parameters[nameL] = parL
            # Maximum value of weight parameter (narrow component)
            nameM = '{0}Max'.format(nameD)
            formulaM = ('{0}*{1}*sqrt(1.0-{2}^2)*({3}/sqrt(1.0-{4}^2)+(1.0-{3})'
                        '/sqrt(1.0-{5}^2)/{6}/{7})').format(nameE, nameF, nameI,
                        nameL, nameJ, nameK, nameG, nameH)
            arglistM = ArgList([nameE, nameF, nameI, nameL, nameJ, nameK, nameG,
                                nameH], self.parameter)
            errorM = (lambda: lambda p: 0.0)()
            parM = FormulaVar(nameM, formulaM, arglistM, errorM)
            self._auxiliary_parameters[nameM] = parM
            # Weight parameter of narrow component
            parD = RealVar(nameD, 0.0, 0.99)
            parD.set_fixed_maximum(parM)
            self._fit_parameters[nameD] = parD
            # Weight of narrow component
            formulaA = '-{0}/(1.0-{0})'.format(nameD)
            arglistA = ArgList([nameD], self.parameter)
            errorA = (
                lambda d: lambda p:
                p(d).err(p)/(1.0-p(d).val())**2
            )(nameD)
            parA = FormulaVar(nameA, formulaA, arglistA, errorA)
            self._physics_parameters[nameA] = parA
            # Weight of medium component
            formulaB = '{0}/(1.0-{1})'.format(nameL, nameD)
            arglistB = ArgList([nameL, nameD], self.parameter)
            errorB = (
                lambda l,d: lambda p:
                1.0/(1.0-p(d).val())*(p(l).err(p)**2+(p(d).err(p)*p(l).val()
                /(1.0-p(d).val()))**2)**0.5
            )(nameL, nameD)
            parB = FormulaVar(nameB, formulaB, arglistB, errorB)
            self._physics_parameters[nameB] = parB
            # Weight of wide component
            formulaC = '(1.0-{0})/(1.0-{1})'.format(nameL, nameD)
            arglistC = ArgList([nameL, nameD], self.parameter)
            errorC = (
                lambda l,d: lambda p:
                1.0/(1.0-p(d).val())*(p(l).err(p)**2+(p(d).err(p)*(1.0
                -p(l).val())/(1.0-p(d).val()))**2)**0.5
            )(nameL, nameD)
            parC = FormulaVar(nameC, formulaC, arglistC, errorC)
            self._physics_parameters[nameC] = parC

    @staticmethod
    def name():
        """Return (unique) abbreviation of model name."""
        return 'SupDG'

class SuperDoubleGaussToy(TripleGaussCore):
    """Super double Gaussian beam shape, parametrized for toy model generation.

    fit_parameters: List of names of free toy model parameters.
    __init__: Initialize.
    name: Return model name.
    """

    fit_parameters = [
        'xWidthN1', 'xWidthN2', 'yWidthN1', 'yWidthN2',
        'rhoN1Factor', 'rhoN2Factor',
        'xWidthM1', 'xWidthM2', 'yWidthM1', 'yWidthM2', 'rhoM1', 'rhoM2',
        'xWidthW1', 'xWidthW2', 'yWidthW1', 'yWidthW2',
        'rhoW1Factor', 'rhoW2Factor',
        'omega1Prime', 'omega2Prime', 'w1MFraction', 'w2MFraction',
        'x011', 'x012', 'x021', 'x022', 'y011', 'y012', 'y021', 'y022'
    ]

    def __init__(self, crange=(-10.0, 10.0)):
        """Initialize super double Gaussian beam shape.

        crange: 2-tuple of limits of the coordinates.
        """
        TripleGaussCore.__init__(self, crange)
        for nameA, nameB, nameC in [
            ('xWidthN1', 'xWidthM1', 'xWidthW1'),
            ('xWidthN2', 'xWidthM2', 'xWidthW2'),
            ('yWidthN1', 'yWidthM1', 'yWidthW1'),
            ('yWidthN2', 'yWidthM2', 'yWidthW2')
        ]:
            # Narrow width
            parA = RealVar(nameA, 1.3, 3.0)
            self._physics_parameters[nameA] = parA
            # Medium width
            parB = RealVar(nameB, 1.3, 3.0)
            self._physics_parameters[nameB] = parB
            # Wide width
            parC = RealVar(nameC, 1.3, 3.0)
            self._physics_parameters[nameC] = parC
            # Ratio of narrow width to medium width
            nameD = '{0}Ratio'.format(nameA)
            formulaD = '{0}/{1}'.format(nameA, nameB)
            arglistD = ArgList([nameA, nameB], self.parameter)
            errorD = (lambda: lambda p: 0.0)()
            parD = FormulaVar(nameD, formulaD, arglistD, errorD)
            self._auxiliary_parameters[nameD] = parD
            # Ratio of wide width to medium width
            nameE = '{0}Ratio'.format(nameC)
            formulaE = '{0}/{1}'.format(nameC, nameB)
            arglistE = ArgList([nameC, nameB], self.parameter)
            errorE = (lambda: lambda p: 0.0)()
            parE = FormulaVar(nameE, formulaE, arglistE, errorE)
            self._auxiliary_parameters[nameE] = parE
        for nameA, nameB, nameC in [
            ('rhoN1', 'rhoM1', 'rhoW1'), ('rhoN2', 'rhoM2', 'rhoW2')
        ]:
            nameD = 'xWidthN{0}Ratio'.format(nameA[-1])
            nameE = 'yWidthN{0}Ratio'.format(nameA[-1])
            nameF = 'xWidthW{0}Ratio'.format(nameA[-1])
            nameG = 'yWidthW{0}Ratio'.format(nameA[-1])
            # Correlation parameter of medium component
            parB = RealVar(nameB, -0.48, 0.48)
            self._physics_parameters[nameB] = parB
            # Minimum value of correlation parameter (wide component)
            nameH = '{0}Min'.format(nameC)
            formulaH = ('max(-0.99,({0}-sqrt(1.0-{1})*sqrt(1.0-{2}))/{3}/{4}'
                        '-sqrt(1.0-({1}/{3})^2)*sqrt(1.0-({2}/{4})^2))') \
                       .format(nameB, nameD, nameE, nameF, nameG)
            arglistH = ArgList([nameB, nameD, nameE, nameF, nameG],
                               self.parameter)
            errorH = (lambda: lambda p: 0.0)()
            parH = FormulaVar(nameH, formulaH, arglistH, errorH)
            self._auxiliary_parameters[nameH] = parH
            # Maximum value of correlation parameter (wide component)
            nameI = '{0}Max'.format(nameC)
            formulaI = ('min(0.99,({0}+sqrt(1.0-{1})*sqrt(1.0-{2}))/{3}/{4}'
                        '+sqrt(1.0-({1}/{3})^2)*sqrt(1.0-({2}/{4})^2))') \
                       .format(nameB, nameD, nameE, nameF, nameG)
            arglistI = ArgList([nameB, nameD, nameE, nameF, nameG],
                               self.parameter)
            errorI = (lambda: lambda p: 0.0)()
            parI = FormulaVar(nameI, formulaI, arglistI, errorI)
            self._auxiliary_parameters[nameI] = parI
            # Position between minimum and maximum value of correlation
            # parameter (wide component)
            nameJ = '{0}Factor'.format(nameC)
            parJ = RealVar(nameJ, 0.0, 1.0)
            self._fit_parameters[nameJ] = parJ
            # Correlation parameter of wide component
            formulaC = '{0}+({1}-{0})*{2}'.format(nameH, nameI, nameJ)
            arglistC = ArgList([nameH, nameI, nameJ], self.parameter)
            errorC = (
                lambda h,i,j: lambda p:
                (p(i).val()-p(h).val())*p(j).err(p)
            )
            parC = FormulaVar(nameC, formulaC, arglistC, errorC)
            self._physics_parameters[nameC] = parC
            # Minimum value of correlation parameter (narrow component)
            nameK = '{0}Min'.format(nameA)
            formulaK = ('max(-0.99,max({0}/{1}/{2}-sqrt(1.0/{1}^2-1.0)'
                        '*sqrt(1.0/{2}^2-1.0),{5}*{3}*{4}/{1}/{2}'
                        '-sqrt(({3}/{1})^2-1.0)*sqrt(({4}/{2})^2-1.0)))') \
                       .format(nameB, nameD, nameE, nameF, nameG, nameC)
            arglistK = ArgList([nameB, nameD, nameE, nameF, nameG, nameC],
                               self.parameter)
            errorK = (lambda: lambda p: 0.0)()
            parK = FormulaVar(nameK, formulaK, arglistK, errorK)
            self._auxiliary_parameters[nameK] = parK
            # Maximum value of correlation parameter (narrow component)
            nameL = '{0}Max'.format(nameA)
            formulaL = ('min(0.99,min({0}/{1}/{2}+sqrt(1.0/{1}^2-1.0)'
                        '*sqrt(1.0/{2}^2-1.0),{5}*{3}*{4}/{1}/{2}'
                        '+sqrt(({3}/{1})^2-1.0)*sqrt(({4}/{2})^2-1.0)))') \
                       .format(nameB, nameD, nameE, nameF, nameG, nameC)
            arglistL = ArgList([nameB, nameD, nameE, nameF, nameG, nameC],
                               self.parameter)
            errorL = (lambda: lambda p: 0.0)()
            parL = FormulaVar(nameL, formulaL, arglistL, errorL)
            self._auxiliary_parameters[nameL] = parL
            # Position between minimum and maximum value of correlation
            # parameter (narrow component)
            nameM = '{0}Factor'.format(nameA)
            parM = RealVar(nameM, 0.0, 1.0)
            self._fit_parameters[nameM] = parM
            # Correlation parameter of narrow component
            formulaA = '{0}+({1}-{0})*{2}'.format(nameK, nameL, nameM)
            arglistA = ArgList([nameK, nameL, nameM], self.parameter)
            errorA = (
                lambda k,l,m: lambda p:
                (p(l).val()-p(k).val())*p(m).err(p)
            )
            parA = FormulaVar(nameA, formulaA, arglistA, errorA)
            self._physics_parameters[nameA] = parA
        for nameA, nameB, nameC, nameD in [
            ('w1N', 'w1M', 'w1W', 'omega1'), ('w2N', 'w2M', 'w2W', 'omega2')
        ]:
            nameE = 'xWidthN{0}Ratio'.format(nameD[-1])
            nameF = 'yWidthN{0}Ratio'.format(nameD[-1])
            nameG = 'xWidthW{0}Ratio'.format(nameD[-1])
            nameH = 'yWidthW{0}Ratio'.format(nameD[-1])
            nameI = 'rhoN{0}'.format(nameD[-1])
            nameJ = 'rhoM{0}'.format(nameD[-1])
            nameK = 'rhoW{0}'.format(nameD[-1])
            # Fraction of weight of medium component w.r.t. wide component
            nameL = '{0}Fraction'.format(nameB)
            parL = RealVar(nameL, 0.0, 1.0)
            self._fit_parameters[nameL] = parL
            # Maximum value of weight parameter (narrow component)
            nameM = '{0}Max'.format(nameD)
            formulaM = ('{0}*{1}*sqrt(1.0-{2}^2)*({3}/sqrt(1.0-{4}^2)+(1.0-{3})'
                        '/sqrt(1.0-{5}^2)/{6}/{7})').format(nameE, nameF, nameI,
                        nameL, nameJ, nameK, nameG, nameH)
            arglistM = ArgList([nameE, nameF, nameI, nameL, nameJ, nameK, nameG,
                                nameH], self.parameter)
            errorM = (lambda: lambda p: 0.0)()
            parM = FormulaVar(nameM, formulaM, arglistM, errorM)
            self._auxiliary_parameters[nameM] = parM
            # Position between minimum and maximum value of weight parameter
            # (narrow component)
            nameN = '{0}Prime'.format(nameD)
            parN = RealVar(nameN, 0.0, 1.0)
            self._fit_parameters[nameN] = parN
            # Weight parameter of narrow component
            formulaD = '{0}*{1}'.format(nameM, nameN)
            arglistD = ArgList([nameM, nameN], self.parameter)
            errorD = (
                lambda m,n: lambda p:
                p(m).val()*p(n).err(p)
            )(nameM, nameN)
            parD = FormulaVar(nameD, formulaD, arglistD, errorD)
            self._auxiliary_parameters[nameD] = parD
            # Weight of narrow component
            formulaA = '-{0}/(1.0-{0})'.format(nameD)
            arglistA = ArgList([nameD], self.parameter)
            errorA = (
                lambda d: lambda p:
                p(d).err(p)/(1.0-p(d).val())**2
            )(nameD)
            parA = FormulaVar(nameA, formulaA, arglistA, errorA)
            self._physics_parameters[nameA] = parA
            # Weight of medium component
            formulaB = '{0}/(1.0-{1})'.format(nameL, nameD)
            arglistB = ArgList([nameL, nameD], self.parameter)
            errorB = (
                lambda l,d: lambda p:
                1.0/(1.0-p(d).val())*(p(l).err(p)**2+(p(d).err(p)*p(l).val()
                /(1.0-p(d).val()))**2)**0.5
            )(nameL, nameD)
            parB = FormulaVar(nameB, formulaB, arglistB, errorB)
            self._physics_parameters[nameB] = parB
            # Weight of wide component
            formulaC = '(1.0-{0})/(1.0-{1})'.format(nameL, nameD)
            arglistC = ArgList([nameL, nameD], self.parameter)
            errorC = (
                lambda l,d: lambda p:
                1.0/(1.0-p(d).val())*(p(l).err(p)**2+(p(d).err(p)*(1.0
                -p(l).val())/(1.0-p(d).val()))**2)**0.5
            )(nameL, nameD)
            parC = FormulaVar(nameC, formulaC, arglistC, errorC)
            self._physics_parameters[nameC] = parC

    @staticmethod
    def name():
        """Return (unique) abbreviation of model name."""
        return 'toySupDG'
