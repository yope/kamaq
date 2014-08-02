from distutils.core import setup
from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

sources = ['audiostep.pyx', 'audiodev.c']

ext_modules=[
    Extension("audiostep",
              sources,
              libraries=["asound", "m"])
]

setup(
  name = "Audiostep",
  cmdclass = {"build_ext": build_ext},
  ext_modules = ext_modules
)

