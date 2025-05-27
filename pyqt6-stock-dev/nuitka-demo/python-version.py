import os
import sys

try:
    from platform import python_implementation
except ImportError:
    # Unable to import
    def python_implementation():
        # Return a string identifying the Python implementation
        # PyPy
        if 'PyPy' in sys.version:
            return 'PyPy'
        # Jython
        if os.name == 'java':
            return 'Jython'
        # IronPython
        if sys.version.startswith('IronPython'):
            return 'IronPython'
        # CPython
        return 'CPython'
    
if __name__ == "__main__":
    python_version = python_implementation()
    print(f'The version of your python is {python_version}! ')