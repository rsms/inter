from __future__ import print_function, division, absolute_import


class BooleanOperationsError(Exception):
    """Base BooleanOperations exception"""


class InvalidContourError(BooleanOperationsError):
    """Rased when any input contour is invalid"""


class InvalidSubjectContourError(InvalidContourError):
    """Rased when a 'subject' contour is not valid"""


class InvalidClippingContourError(InvalidContourError):
    """Rased when a 'clipping' contour is not valid"""


class ExecutionError(BooleanOperationsError):
    """Raised when clipping execution fails"""
