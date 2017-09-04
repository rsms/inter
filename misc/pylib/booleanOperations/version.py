try:
    __version__ = __import__('pkg_resources').require('booleanOperations')[0].version
except Exception:
    __version__ = 'unknown'
