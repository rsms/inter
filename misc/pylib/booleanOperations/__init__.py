from __future__ import print_function, division, absolute_import
from .booleanOperationManager import BooleanOperationManager
from .exceptions import BooleanOperationsError
from .version import __version__

# export BooleanOperationManager static methods
union = BooleanOperationManager.union
difference = BooleanOperationManager.difference
intersection = BooleanOperationManager.intersection
xor = BooleanOperationManager.xor
getIntersections = BooleanOperationManager.getIntersections
