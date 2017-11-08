"""Provides base class for beam shape models.

BeamShapeCore: Base class (abstract).
"""

from json import load
from math import copysign
from os.path import exists

from ROOT import TF2

from lib.io import NamedFloat, RootFile
from lib.vars import RealVar

class BeamShapeCore:
    """Core functionality for beam shapes (abstract).

    __init__: Initialize.
    name: Return model name (abstract).
    dof: Return parameter number (abstract).
    xvar: Return x variable.
    yvar: Return y variable.
    parameter: Return specific variable.
    parameters: Iterate over parameters.
    set_vtxres: Set vertex resolution.
    load_json: Load values from JSON config.
    overlap: Compute beam shape overlap (abstract).
    assign_overlap: Assign parameter values to overlap function.
    overlap_func: Return beam shape overlap as TF2.
    """

    def __init__(self, crange=(-10.0, 10.0)):
        """Initialize core functionality of a beam shape model.

        crange: 2-tuple of limits of the coordinates.
        """
        self.factor = 1.0
        self._variables = {}
        self._physics_parameters = {}
        self._fit_parameters = {}
        self._auxiliary_parameters = {}
        for name in ['xVar', 'yVar']:
            # Coordinate
            var = RealVar(name, crange[0], crange[1])
            var.setBins(10000, 'cache')
            self._variables[name] = var
        for name in [
            'x011', 'x012', 'x021', 'x022', 'y011', 'y012', 'y021', 'y022'
        ]:
            # Peak position
            par = RealVar(name, -0.5, 0.5)
            self._physics_parameters[name] = par
        for name in ['xVtxRes', 'yVtxRes']:
            # Vertex resolution
            par = RealVar(name, 0.0, 5.0)
            self._physics_parameters[name] = par

    @staticmethod
    def name():
        """Return (unique) abbreviation of model name."""
        msg = 'BeamShapeCore: Called name() of abstract class!'
        raise NotImplementedError(msg)

    @staticmethod
    def dof():
        """Return number of independent parameters."""
        msg = 'BeamShapeCore: Called dof() of abstract class!'
        raise NotImplementedError(msg)

    def xvar(self):
        """Return x variable."""
        return self._variables['xVar']

    def yvar(self):
        """Return y variable."""
        return self._variables['yVar']

    def parameter(self, name):
        """Return parameter belonging to string argument."""
        if name in self._physics_parameters:
            return self._physics_parameters[name]
        elif name in self._fit_parameters:
            return self._fit_parameters[name]
        elif name in self._auxiliary_parameters:
            return self._auxiliary_parameters[name]
        else:
            msg = 'BeamShapeCore: Requested parameter does not exist! ({0})' \
                  .format(name)
            raise KeyError(msg)

    def parameters(self):
        """Return an iterator over physical and fit parameters."""
        for name in self._physics_parameters:
            yield self.parameter(name)
        for name in self._fit_parameters:
            if name not in self._physics_parameters:
                yield self.parameter(name)
        for name in self._auxiliary_parameters:
            if name not in self._physics_parameters \
            and name not in self._fit_parameters:
                yield self.parameter(name)

    def set_vtxres(self, vtxresx, vtxresy=None, constant=True):
        """Set the values of the vertex resolution."""
        if vtxresy is None:
            vtxresy = vtxresx
        self.parameter('xVtxRes').setVal(vtxresx)
        self.parameter('yVtxRes').setVal(vtxresy)
        self.parameter('xVtxRes').setConstant(constant)
        self.parameter('yVtxRes').setConstant(constant)

    def load_json(self, parameterfile=None, random=None):
        """Loads parameter boundaries and initial values from JSON config.

        If parameterfile (string) is specified, try to open file as JSON.
        Otherwise, use res/shapes/<model>.json.
        If random is specified, choose random initial values within boundaries.
        Returns TParameter list with boundaries, initial and constant values.
        """
        if parameterfile is None:
            parameterfile = 'res/shapes/{}.json'.format(self.name())
        if not exists(parameterfile):
            msg = 'BeamShapeCore: Parameter file does not exist! ({})' \
                  .format(parameterfile)
            raise IOError(msg)
        with open(parameterfile) as f:
            parameterlist = load(f)
        parameters = []
        for name in parameterlist:
            values = parameterlist[name]
            try:
                par = self.parameter(name)
            except KeyError as error:
                print '<<< {}'.format(error)
                continue
            if not par or par.is_formula():
                continue
            if len(values) == 1:
                par.setConstant(True)
                par.setVal(values[0])
                parameters.append(NamedFloat(name+'_const', values[0]))
            elif len(values) >= 2:
                par.setConstant(False)
                par.set_range(values[0], values[1])
                if random is not None:
                    ini = random.Uniform(values[0], values[1])
                elif len(values) >= 3:
                    ini = values[2]
                else:
                    ini = 0.5 * (values[0] + values[1])
                par.setVal(ini)
                parameters.append(NamedFloat(name+'_min', values[0]))
                parameters.append(NamedFloat(name+'_max', values[1]))
                parameters.append(NamedFloat(name+'_ini', ini))
        return parameters

    def load_root(self, filename):
        """Loads parameter values from ROOT results file.

        filename: (Part of) name of ROOT file with fit results.
        """
        with RootFile(filename) as f:
            for par in self.parameters():
                if par.is_formula():
                    continue
                value = f.Get('final/{0}'.format(par.GetName()))
                error = f.Get('final/{0}_error'.format(par.GetName()))
                if value and error:
                    val, err = value.GetVal(), error.GetVal()
                    par.setRange(val-2*err, val+2*err)
                    par.setVal(val)
                    par.setError(err)

    def overlap(self, x, par):
        """Compute product of the beam shapes.

        x: list of variable values (two entries).
        par: list of parameter values (model-dependent entries).
        """
        msg = 'BeamShapeCore: Called overlap() of abstract class!'
        raise NotImplementedError(msg)

    def _assign_overlap(self, overlap, names, start, random=None):
        """Auxiliary function to be called by subclasses."""
        values = {name: self.parameter(name).val() for name in names}
        if random is not None:
            for name, value in values.iteritems():
                error = self.parameter(name).err(self.parameter)
                value = random.Gaus(value, error)
                if name.startswith('rho') and abs(value) > 0.999:
                    value = copysign(0.999, value)
        for i, name in enumerate(names, start=start):
            overlap.SetParameter(i, values[name])
        return overlap

    def assign_overlap(self, overlap, random=None):
        """Assigns current parameter values to overlap function."""
        overlap.SetParameter(0, 0.0)
        overlap.SetParameter(1, 0.0)
        overlap.SetParameter(2, 0.0)
        overlap.SetParameter(3, 0.0)
        return overlap

    def overlap_func(self):
        """Return beam shape product as TF2."""
        overlap = TF2('overlap', self.overlap, -30.0, 30.0, -30.0, 30.0,
                      self.dof())
        overlap = self.assign_overlap(overlap)
        return overlap
