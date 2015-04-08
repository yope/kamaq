from distutils.core import setup
from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

audiostep_sources = ['audiostep.pyx', 'audiodev.c']
move_sources = ['move.pyx']
vector_sources = ['vector.pyx']

ext_modules=[
	Extension("audiostep", audiostep_sources, libraries=["asound", "m"]),
	Extension("move", move_sources, libraries = ['m']),
	Extension("vector", vector_sources, libraries = ['m'])
]

setup(
  name = "Audiostep",
  cmdclass = {"build_ext": build_ext},
  ext_modules = ext_modules
)

