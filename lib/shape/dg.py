"""Provides classes for double Gaussian beam shape models.

DoubleGaussCore: Base class (abstract).
DoubleGaussFit: double Gaussian beam shape model (parametrized for fit).
DoubleGaussToy: double Gaussian beam shape model (parametrized for MC).
SuperGaussFit: super Gaussian beam shape model (parametrized for fit).
SuperGaussFit: super Gaussian beam shape model (parametrized for MC).
"""

from lib.shape.sg import SingleGaussCore
from lib.vars import ArgList, FormulaVar, RealVar
from plugins.dg import DoubleGauss_V1, DoubleGauss_V2, DoubleGaussOverlap

class DoubleGaussCore(SingleGaussCore):
    """Core functionality for double Gaussian beam shapes (abstract).

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
        'xVtxRes', 'yVtxRes'
    ]

    def __init__(self, crange=(-10.0, 10.0)):
        """Initialize core functionality of double Gaussian beam shapes.

        crange: 2-tuple of limits of the coordinates.
        """
        SingleGaussCore.__init__(self, crange)

    @staticmethod
    def dof():
        """Return number of independent parameters."""
        return 18

    def model_functions(self):
        """Create functions for the fit model of the Beam Imaging scan."""
        x1 = DoubleGauss_V1(
            'beam1RestVerticesUnfold_XScan',
            'beam1RestVerticesUnfold_XScan',
            self.xvar(), self.yvar(),
            self.parameter('x011'), self.parameter('y011'),
            self.parameter('w1N'),
            self.parameter('rhoN1'),
            self.parameter('xWidthN1'), self.parameter('yWidthN1'),
            self.parameter('rhoM1'),
            self.parameter('xWidthM1'), self.parameter('yWidthM1'),
            self.parameter('w2N'),
            self.parameter('yWidthN2'), self.parameter('yWidthM2'),
            self.parameter('xVtxRes'), self.parameter('yVtxRes')
        )
        y1 = DoubleGauss_V2(
            'beam1RestVerticesUnfold_YScan',
            'beam1RestVerticesUnfold_YScan',
            self.xvar(), self.yvar(),
            self.parameter('x012'), self.parameter('y012'),
            self.parameter('w1N'),
            self.parameter('rhoN1'),
            self.parameter('xWidthN1'), self.parameter('yWidthN1'),
            self.parameter('rhoM1'),
            self.parameter('xWidthM1'), self.parameter('yWidthM1'),
            self.parameter('w2N'),
            self.parameter('xWidthN2'), self.parameter('xWidthM2'),
            self.parameter('xVtxRes'), self.parameter('yVtxRes')
        )
        x2 = DoubleGauss_V1(
            'beam2RestVerticesUnfold_XScan',
            'beam2RestVerticesUnfold_XScan',
            self.xvar(), self.yvar(),
            self.parameter('x021'), self.parameter('y021'),
            self.parameter('w2N'),
            self.parameter('rhoN2'),
            self.parameter('xWidthN2'), self.parameter('yWidthN2'),
            self.parameter('rhoM2'),
            self.parameter('xWidthM2'), self.parameter('yWidthM2'),
            self.parameter('w1N'),
            self.parameter('yWidthN1'), self.parameter('yWidthM1'),
            self.parameter('xVtxRes'), self.parameter('yVtxRes')
        )
        y2 = DoubleGauss_V2(
            'beam2RestVerticesUnfold_YScan',
            'beam2RestVerticesUnfold_YScan',
            self.xvar(), self.yvar(),
            self.parameter('x022'), self.parameter('y022'),
            self.parameter('w2N'),
            self.parameter('rhoN2'),
            self.parameter('xWidthN2'), self.parameter('yWidthN2'),
            self.parameter('rhoM2'),
            self.parameter('xWidthM2'), self.parameter('yWidthM2'),
            self.parameter('w1N'),
            self.parameter('xWidthN1'), self.parameter('xWidthM1'),
            self.parameter('xVtxRes'), self.parameter('yVtxRes')
        )
        return [x1, y1, x2, y2]

    def overlap(self, x, par):
        """Compute product of the beam shapes.

        x: list of variable values (two entries).
        par: list of parameter values (18 entries).
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
        try:
            beamN1 = self.gauss(xx, yy, x01, y01, xWidthN1, yWidthN1, rhoN1)
            beamM1 = self.gauss(xx, yy, x01, y01, xWidthM1, yWidthM1, rhoM1)
            beamN2 = self.gauss(xx, yy, x02, y02, xWidthN2, yWidthN2, rhoN2)
            beamM2 = self.gauss(xx, yy, x02, y02, xWidthM2, yWidthM2, rhoM2)
            return (w1N*beamN1+(1.0-w1N)*beamM1)*(w2N*beamN2+(1.0-w2N)*beamM2)
        except (ArithmeticError, ValueError) as error:
            print '<<< Error (overlap):', error
            return -1.0

    def assign_overlap(self, overlap, random=None):
        overlap = SingleGaussCore.assign_overlap(self, overlap, random)
        names = ['w1N', 'w2N', 'xWidthM1', 'yWidthM1', 'xWidthM2', 'yWidthM2',
                 'rhoM1', 'rhoM2']
        overlap = self._assign_overlap(overlap, names, 10, random)
        return overlap

    def overlap_func(self):
        """Return beam shape product as TF2."""
        overlap = DoubleGaussOverlap(self.factor)
        overlap = self.assign_overlap(overlap)
        return overlap

class DoubleGaussFit(DoubleGaussCore):
    """Double Gaussian beam shape, parametrized for fit.

    fit_parameters: List of names of fit parameters.
    __init__: Initialize.
    name: Return model name.
    """

    fit_parameters = [
        'xWidthN1', 'xWidthN2', 'yWidthN1', 'yWidthN2', 'rhoN1', 'rhoN2',
        'xWidthM1Diff', 'xWidthM2Diff', 'yWidthM1Diff', 'yWidthM2Diff',
        'rhoM1', 'rhoM2',
        'w1N', 'w2N',
        'x011', 'x012', 'x021', 'x022', 'y011', 'y012', 'y021', 'y022'
    ]

    def __init__(self, crange=(-10.0, 10.0)):
        """Initialize double Gaussian beam shape.

        crange: 2-tuple of limits of the coordinates.
        """
        DoubleGaussCore.__init__(self, crange)
        for nameA, nameB in [
            ('xWidthN1', 'xWidthM1'), ('xWidthN2', 'xWidthM2'),
            ('yWidthN1', 'yWidthM1'), ('yWidthN2', 'yWidthM2')
        ]:
            # Narrow width
            parA = RealVar(nameA, 1.3, 3.0)
            self._physics_parameters[nameA] = parA
            # Difference of narrow width to wide width
            nameC = '{0}Diff'.format(nameB)
            parC = RealVar(nameC, 0.01, 1.7)
            self._fit_parameters[nameC] = parC
            # Wide width
            formulaB = '{0}+{1}'.format(nameA, nameC)
            arglistB = ArgList([nameA, nameC], self.parameter)
            errorB = (
                lambda a,c: lambda p:
                (p(a).err(p)**2+p(c).err(p)**2)**0.5
            )(nameA, nameC)
            parB = FormulaVar(nameB, formulaB, arglistB, errorB)
            self._physics_parameters[nameB] = parB
        for name in ['rhoN1', 'rhoN2', 'rhoM1', 'rhoM2']:
            # Correlation parameter
            par = RealVar(name, -0.48, 0.48)
            self._physics_parameters[name] = par
        for nameA, nameB in [('w1N', 'w1M'), ('w2N', 'w2M')]:
            # Weight of narrow component
            parA = RealVar(nameA, 0.0, 1.0)
            self._physics_parameters[nameA] = parA
            # Weight of wide component
            formulaB = '1.0-{0}'.format(nameA)
            arglistB = ArgList([nameA], self.parameter)
            errorB = (
                lambda a: lambda p:
                p(a).err(p)
            )(nameA)
            parB = FormulaVar(nameB, formulaB, arglistB, errorB)
            self._physics_parameters[nameB] = parB

    @staticmethod
    def name():
        """Return (unique) abbreviation of model name."""
        return 'DG'

class DoubleGaussToy(DoubleGaussCore):
    """Double Gaussian beam shape, parametrized for toy model generation.

    fit_parameters: List of names of free toy model parameters.
    __init__: Initialize.
    name: Return model name.
    """

    fit_parameters = [
        'xWidthN1', 'xWidthN2', 'yWidthN1', 'yWidthN2', 'rhoN1', 'rhoN2',
        'xWidthM1', 'xWidthM2', 'yWidthM1', 'yWidthM2', 'rhoM1', 'rhoM2',
        'w1N', 'w2N',
        'x011', 'x012', 'x021', 'x022', 'y011', 'y012', 'y021', 'y022'
    ]

    def __init__(self, crange=(-10.0, 10.0)):
        """Initialize double Gaussian beam shape.

        crange: 2-tuple of limits of the coordinates.
        """
        DoubleGaussCore.__init__(self, crange)
        for name in [
            'xWidthN1', 'xWidthN2', 'yWidthN1', 'yWidthN2',
            'xWidthM1', 'xWidthM2', 'yWidthM1', 'yWidthM2'
        ]:
            # Width
            par = RealVar(name, 1.3, 3.0)
            self._physics_parameters[name] = par
        for name in ['rhoN1', 'rhoN2', 'rhoM1', 'rhoM2']:
            # Correlation parameter
            par = RealVar(name, -0.48, 0.48)
            self._physics_parameters[name] = par
        for nameA, nameB in [('w1N', 'w1M'), ('w2N', 'w2M')]:
            # Weight of narrow component
            parA = RealVar(nameA, 0.0, 1.0)
            self._physics_parameters[nameA] = parA
            # Weight of wide component
            formulaB = '1.0-{0}'.format(nameA)
            arglistB = ArgList([nameA], self.parameter)
            errorB = (
                lambda a: lambda p:
                p(a).err(p)
            )(nameA)
            parB = FormulaVar(nameB, formulaB, arglistB, errorB)
            self._physics_parameters[nameB] = parB

    @staticmethod
    def name():
        """Return (unique) abbreviation of model name."""
        return 'toyDG'

class SuperGaussFit(DoubleGaussCore):
    """Super Gaussian beam shape, parametrized for fit.

    fit_parameters: List of names of fit parameters.
    __init__: Initialize.
    name: Return model name.
    """

    fit_parameters = [
        'xWidthN1Ratio', 'xWidthN2Ratio', 'yWidthN1Ratio', 'yWidthN2Ratio',
        'rhoN1', 'rhoN2',
        'xWidthM1', 'xWidthM2', 'yWidthM1', 'yWidthM2', 'rhoM1', 'rhoM2',
        'omega1', 'omega2',
        'x011', 'x012', 'x021', 'x022', 'y011', 'y012', 'y021', 'y022'
    ]

    def __init__(self, crange=(-10.0, 10.0)):
        """Initialize super Gaussian beam shape.

        crange: 2-tuple of limits of the coordinates.
        """
        DoubleGaussCore.__init__(self, crange)
        for nameA, nameB in [
            ('xWidthN1', 'xWidthM1'), ('xWidthN2', 'xWidthM2'),
            ('yWidthN1', 'yWidthM1'), ('yWidthN2', 'yWidthM2')
        ]:
            # Wide width
            parB = RealVar(nameB, 1.3, 3.0)
            self._physics_parameters[nameB] = parB
            # Ratio of narrow width to wide width
            nameC = '{0}Ratio'.format(nameA)
            parC = RealVar(nameC, 0.1, 0.99)
            self._fit_parameters[nameC] = parC
            # Narrow width
            formulaA = '{0}*{1}'.format(nameB, nameC)
            arglistA = ArgList([nameB, nameC], self.parameter)
            errorA = (
                lambda b,c: lambda p:
                ((p(b).val()*p(c).err(p))**2+(p(c).val()*p(b).err(p))**2)**0.5
            )(nameB, nameC)
            parA = FormulaVar(nameA, formulaA, arglistA, errorA)
            self._physics_parameters[nameA] = parA
        for nameA, nameB in [('rhoN1', 'rhoM1'), ('rhoN2', 'rhoM2')]:
            nameC = 'xWidthN{0}Ratio'.format(nameA[-1])
            nameD = 'yWidthN{0}Ratio'.format(nameA[-1])
            # Correlation parameter of wide component
            parB = RealVar(nameB, -0.48, 0.48)
            self._physics_parameters[nameB] = parB
            # Minimum value of correlation parameter (narrow component)
            nameE = '{0}Min'.format(nameA)
            formulaE = ('max(-0.99,{0}/{1}/{2}-sqrt(1.0/{1}^2-1.0)'
                        '*sqrt(1.0/{2}^2-1.0))').format(nameB, nameC, nameD)
            arglistE = ArgList([nameB, nameC, nameD], self.parameter)
            errorE = (lambda: lambda p: 0.0)()
            parE = FormulaVar(nameE, formulaE, arglistE, errorE)
            self._auxiliary_parameters[nameE] = parE
            # Maximum value of correlation parameter (narrow component)
            nameF = '{0}Max'.format(nameA)
            formulaF = ('min(0.99,{0}/{1}/{2}+sqrt(1.0/{1}^2-1.0)'
                        '*sqrt(1.0/{2}^2-1.0))').format(nameB, nameC, nameD)
            arglistF = ArgList([nameB, nameC, nameD], self.parameter)
            errorF = (lambda: lambda p: 0.0)()
            parF = FormulaVar(nameF, formulaF, arglistF, errorF)
            self._auxiliary_parameters[nameF] = parF
            # Correlation parameter of narrow component
            parA = RealVar(nameA, -0.48, 0.48)
            parA.set_fixed_minimum(parE)
            parA.set_fixed_maximum(parF)
            self._physics_parameters[nameA] = parA
        for nameA, nameB, nameC in [
            ('w1N', 'w1M', 'omega1'), ('w2N', 'w2M', 'omega2')
        ]:
            nameD = 'xWidthN{0}Ratio'.format(nameC[-1])
            nameE = 'yWidthN{0}Ratio'.format(nameC[-1])
            nameF = 'rhoN{0}'.format(nameC[-1])
            nameG = 'rhoM{0}'.format(nameC[-1])
            # Maximum value of weight parameter
            nameH = '{}Max'.format(nameC)
            formulaH = '{0}*{1}*sqrt((1.0-{2}^2)/(1.0-{3}^2))' \
                       .format(nameD, nameE, nameF, nameG)
            arglistH = ArgList([nameD, nameE, nameF, nameG], self.parameter)
            errorH = (lambda: lambda p: 0.0)()
            parH = FormulaVar(nameH, formulaH, arglistH, errorH)
            self._auxiliary_parameters[nameH] = parH
            # Weight parameter
            parC = RealVar(nameC, 0.0, 0.99)
            parC.set_fixed_maximum(parH)
            self._fit_parameters[nameC] = parC
            # Weight of narrow component
            formulaA = '-{0}/(1.0-{0})'.format(nameC)
            arglistA = ArgList([nameC], self.parameter)
            errorA = (
                lambda c: lambda p:
                p(c).err(p)/(1.0-p(c).val()**2)
            )(nameC)
            parA = FormulaVar(nameA, formulaA, arglistA, errorA)
            self._physics_parameters[nameA] = parA
            # Weight of wide component
            formulaB = '1.0/(1.0-{0})'.format(nameC)
            arglistB = ArgList([nameC], self.parameter)
            errorB = (
                lambda c: lambda p:
                p(c).err(p)/(1.0-p(c).val())**2
            )(nameC)
            parB = FormulaVar(nameB, formulaB, arglistB, errorB)
            self._physics_parameters[nameB] = parB

    @staticmethod
    def name():
        """Return (unique) abbreviation of model name."""
        return 'SupG'

class SuperGaussToy(DoubleGaussCore):
    """Super Gaussian beam shape, parametrized for toy model generation.

    fit_parameters: List of names of free toy model parameters.
    __init__: Initialize.
    name: Return model name.
    """

    fit_parameters = [
        'xWidthN1', 'xWidthN2', 'yWidthN1', 'yWidthN2',
        'rhoN1Factor', 'rhoN2Factor',
        'xWidthM1', 'xWidthM2', 'yWidthM1', 'yWidthM2', 'rhoM1', 'rhoM2',
        'omega1Prime', 'omega2Prime',
        'x011', 'x012', 'x021', 'x022', 'y011', 'y012', 'y021', 'y022'
    ]

    def __init__(self, crange=(-10.0, 10.0)):
        """Initialize super Gaussian beam shape.

        crange: 2-tuple of limits of the coordinates.
        """
        DoubleGaussCore.__init__(self, crange)
        for nameA, nameB in [
            ('xWidthN1', 'xWidthM1'), ('xWidthN2', 'xWidthM2'),
            ('yWidthN1', 'yWidthM1'), ('yWidthN2', 'yWidthM2')
        ]:
            # Narrow width
            parA = RealVar(nameA, 1.3, 3.0)
            self._physics_parameters[nameA] = parA
            # Wide width
            parB = RealVar(nameB, 1.3, 3.0)
            self._physics_parameters[nameB] = parB
            # Ratio of narrow width to wide width
            nameC = '{0}Ratio'.format(nameA)
            formulaC = '{0}/{1}'.format(nameA, nameB)
            arglistC = ArgList([nameA, nameB], self.parameter)
            errorC = (lambda: lambda p: 0.0)()
            parC = FormulaVar(nameC, formulaC, arglistC, errorC)
            self._auxiliary_parameters[nameC] = parC
        for nameA, nameB in [('rhoN1', 'rhoM1'), ('rhoN2', 'rhoM2')]:
            nameC = 'xWidthN{0}Ratio'.format(nameA[-1])
            nameD = 'yWidthN{0}Ratio'.format(nameA[-1])
            # Correlation parameter of wide component
            parB = RealVar(nameB, -0.48, 0.48)
            self._physics_parameters[nameB] = parB
            # Minimum value of correlation parameter (narrow component)
            nameE = '{0}Min'.format(nameA)
            formulaE = ('max(-0.99,{0}/{1}/{2}-sqrt(1.0/{1}^2-1.0)'
                        '*sqrt(1.0/{2}^2-1.0))').format(nameB, nameC, nameD)
            arglistE = ArgList([nameB, nameC, nameD], self.parameter)
            errorE = (lambda: lambda p: 0.0)()
            parE = FormulaVar(nameE, formulaE, arglistE, errorE)
            self._auxiliary_parameters[nameE] = parE
            # Maximum value of correlation parameter (narrow component)
            nameF = '{0}Max'.format(nameA)
            formulaF = ('min(0.99,{0}/{1}/{2}+sqrt(1.0/{1}^2-1.0)'
                        '*sqrt(1.0/{2}^2-1.0))').format(nameB, nameC, nameD)
            arglistF = ArgList([nameB, nameC, nameD], self.parameter)
            errorF = (lambda: lambda p: 0.0)()
            parF = FormulaVar(nameF, formulaF, arglistF, errorF)
            self._auxiliary_parameters[nameF] = parF
            # Position between minimum and maximum value of correlation
            # parameter (narrow component)
            nameG = '{0}Factor'.format(nameA)
            parG = RealVar(nameG, 0.0, 1.0)
            self._fit_parameters[nameG] = parG
            # Correlation parameter of narrow component
            formulaA = '{0}+({1}-{0})*{2}'.format(nameE, nameF, nameG)
            arglistA = ArgList([nameE, nameF, nameG], self.parameter)
            errorA = (
                lambda e,f,g: lambda p:
                (p(f).val()-p(e).val())*p(g).err(p)
            )(nameE, nameF, nameG)
            parA = FormulaVar(nameA, formulaA, arglistA, errorA)
            self._physics_parameters[nameA] = parA
        for nameA, nameB, nameC in [
            ('w1N', 'w1M', 'omega1'), ('w2N', 'w2M', 'omega2')
        ]:
            nameD = 'xWidthN{0}Ratio'.format(nameC[-1])
            nameE = 'yWidthN{0}Ratio'.format(nameC[-1])
            nameF = 'rhoN{0}'.format(nameC[-1])
            nameG = 'rhoM{0}'.format(nameC[-1])
            # Maximum value of weight parameter
            nameH = '{0}Max'.format(nameC)
            formulaH = '{0}*{1}*sqrt((1.0-{2}^2)/(1.0-{3}^2))' \
                       .format(nameD, nameE, nameF, nameG)
            arglistH = ArgList([nameD, nameE, nameF, nameG], self.parameter)
            errorH = (lambda: lambda p: 0.0)()
            parH = FormulaVar(nameH, formulaH, arglistH, errorH)
            self._auxiliary_parameters[nameH] = parH
            # Position between minimum and maximum value of weight parameter
            nameI = '{0}Prime'.format(nameC)
            parI = RealVar(nameI, 0.0, 1.0)
            self._fit_parameters[nameI] = parI
            # Weight parameter
            formulaC = '{0}*{1}'.format(nameH, nameI)
            arglistC = ArgList([nameH, nameI], self.parameter)
            errorC = (
                lambda h,i: lambda p:
                p(h).val()*p(i).err(p)
            )(nameH, nameI)
            parC = FormulaVar(nameC, formulaC, arglistC, errorC)
            self._auxiliary_parameters[nameC] = parC
            # Weight of narrow component
            formulaA = '-{0}/(1.0-{0})'.format(nameC)
            arglistA = ArgList([nameC], self.parameter)
            errorA = (
                lambda c: lambda p:
                p(c).err(p)/(1.0-p(c).val()**2)
            )(nameC)
            parA = FormulaVar(nameA, formulaA, arglistA, errorA)
            self._physics_parameters[nameA] = parA
            # Weight of wide component
            formulaB = '1.0/(1.0-{0})'.format(nameC)
            arglistB = ArgList([nameC], self.parameter)
            errorB = (
                lambda c: lambda p:
                p(c).err(p)/(1.0-p(c).val()**2)
            )(nameC)
            parB = FormulaVar(nameB, formulaB, arglistB, errorB)
            self._physics_parameters[nameB] = parB

    @staticmethod
    def name():
        """Return (unique) abbreviation of model name."""
        return 'toySupG'
