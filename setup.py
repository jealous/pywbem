from setuptools import setup, find_packages
import io
import os

# Version of the pywbem package
# !!! Keep in sync with version stated in module docstring, above !!!
__version__ = '0.0.2'

__author__ = 'Cedric Zhuang'


def here(filename=None):
    ret = os.path.abspath(os.path.dirname(__file__))
    if filename is not None:
        ret = os.path.join(ret, filename)
    return ret


def read(*filenames, **kwargs):
    encoding = kwargs.get('encoding', 'utf-8')
    sep = kwargs.get('sep', '\n\n')
    buf = []
    for filename in filenames:
        with io.open(here(filename), encoding=encoding) as f:
            buf.append(f.read())
    return sep.join(buf)


def read_requirements(filename):
    with open(filename) as f:
        return f.read().splitlines()


def get_description():
    return "Fork of pywbem that only including requests."


def get_long_description():
    filename = 'README.rst'
    return read(filename)


setup(
    name="pywbemReq",
    version=__version__,
    author="Cedric Zhuang",
    author_email="cedric.zhuang@gmail.com",
    description=get_description(),
    license="LGPLv2+",
    keywords="pywbem, SMI-S",
    include_package_data=True,
    packages=find_packages(),
    platforms=['any'],
    long_description=get_long_description(),
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Natural Language :: English",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Topic :: Utilities",
        "License :: OSI Approved :: "
        "GNU Lesser General Public License v2 or later (LGPLv2+)",
    ],
    install_requires=read_requirements('requirements.txt'),
    tests_require=read_requirements('test-requirements.txt')
)
