from enum import Enum

class BinaryType(Enum):
    EXECUTABLE = 'EXECUTABLE'
    SHARED_LIB = 'SHARED_LIB'
    STATIC_LIB = 'STATIC_LIB'

class BuildType(Enum):
    DEBUG = 'DEBUG'
    RELEASE = 'RELEASE'
