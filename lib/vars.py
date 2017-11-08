"""Provides classes for variables.

RealVar: Variable that takes a value.
FormulaVar: Variable that depends on other variables.
ArgList: List of variables.
"""

from ROOT import RooArgList, RooFit, RooFormulaVar, RooRealVar

class RealVar(RooRealVar):
    """A variable that takes a value.

    __init__: Initialize.
    is_formula: Return false.
    val: Return value.
    err: Return error.
    set_range: Set boundaries.
    set_fixed_minimum: Set lower boundary to different variable.
    set_fixed_maximum: Set upper boundary to different variable.
    """

    def __init__(self, name, lower, higher=None):
        """Initialize a variable.

        Takes a name (string) and one or two numbers (float) as arguments.
        One number: Initialize variable with a constant value.
        Two numbers: Initialize variable with a fixed range.
        """
        if higher is None:
            RooRealVar.__init__(self, name, name, lower)
        else:
            RooRealVar.__init__(self, name, name, lower, higher)
        self._fixed_minimum = None
        self._fixed_maximum = None

    def is_formula(self):
        """Check if variable depends on other variables."""
        return False

    def val(self):
        """Return currently set value of the variable."""
        return self.getValV()

    def err(self, parameter=None):
        """Return uncertainty of currently set value of the variable.

        The argument is unused (for compability with FormulaVar functionality).
        """
        return self.getError()

    def set_range(self, lower, higher):
        """Set range of variable to boundaries given as arguments."""
        if self._fixed_minimum is None and self._fixed_maximum is None:
            minimum, maximum = lower, higher
        elif self._fixed_minimum is None:
            minimum, maximum = RooFit.RooConst(lower), self._fixed_maximum
        elif self._fixed_maximum is None:
            minimum, maximum = self._fixed_minimum, RooFit.RooConst(higher)
        else:
            minimum, maximum = self._fixed_minimum, self._fixed_maximum
        self.setRange(minimum, maximum)

    def set_fixed_minimum(self, lower):
        """Set lower boundary of the variable to value of another variable."""
        self._fixed_minimum = lower
        self.set_range(self.getMin(), self.getMax())

    def set_fixed_maximum(self, higher):
        """Set upper boundary of the variable to value of another variable."""
        self._fixed_maximum = higher
        self.set_range(self.getMin(), self.getMax())

class FormulaVar(RooFormulaVar):
    """A variable that depends on other variables.

    __init__: Initialize.
    set_error: Define error function.
    is_formula: Return true.
    val: Return value.
    err: Return error.
    """

    def __init__(self, name, formula, arglist, error=None):
        """Initialize a variable.

        Takes a name, a formula (strings), an list of variables (RooArgList) the
        variable depends on, and (optionally) an error (function).
        """
        RooFormulaVar.__init__(self, name, name, formula, arglist)
        self.set_error(error)

    def set_error(self, error):
        """Define the error function."""
        self._error = error

    def is_formula(self):
        """Check if variable depends on other variables."""
        return True

    def val(self):
        """Return currently set value of the variable."""
        return self.getValV()

    def err(self, parameter):
        """Return uncertainty of the current value of the variable.

        Takes a function that returns on name input the corresponding variable
        (RealVar, FormulaVar).
        """
        if self._error is None:
            msg = 'FormulaVar: Error called but not set! ({})' \
                  .format(self.GetName())
            raise NotImplementedError(msg)
        return self._error(parameter)

class ArgList(RooArgList):
    """List of variables.

    __init__: Initialize.
    """

    def __init__(self, names, parameter):
        """Initialize a list of variables.

        names: List of strings that contain the names of variables.
        parameter: Function that returns variable on name (string) input.
        """
        RooArgList.__init__(self)
        for name in names:
            self.add(parameter(name))
