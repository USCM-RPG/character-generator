from importlib.metadata import PackageNotFoundError, version

from uscm_character_generator import character_generator, extra_types

try:
    __version__ = version("uscm-character-generator")
except PackageNotFoundError:
    # package is not installed
    pass
