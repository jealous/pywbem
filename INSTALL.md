Installation of PyWBEM Client
=============================

The PyWBEM Client can be installed quite easily by running its standard Python
setup script (`setup.py`) with the `install` command, or by using `pip install`
(which also invokes the setup script).

As of PyWBEM Client v0.8.0, the setup script has support for installing its
prerequisites. This includes installing Python packages and OS-level packages,
and it includes the usual install mode and development mode.

OS-level prerequisites are installed using new setup.py commands 'install_os'
(for the usual install mode) and 'develop_os' (for development mode). These
commands perform the installation for a number of well-known Linux
distributions, using 'sudo' (so your userid needs to be authorized for sudo,
if you run these commands). For other Linux distributions and operating
systems, these setup.py commands just display the names of the OS-level
packages that would be needed on RHEL, leaving it to the user to
translate the package names to the actual system, and to establish the
prerequisites. This approach is compatible with PyPI because 'pip install'
invokes 'setup.py install' but not the new commands. It is also compatible
with packaging PyWBEM into OS-level Python packages, for the same reason.
This approach is also compatible with 
[virtual Python environments](http://docs.python-guide.org/en/latest/dev/virtualenvs/).

Examples
--------

* Install latest version from PyPI into default system Python (assuming
  OS-level prerequisites are already satisfied):

      sudo pip install pywbem

* Install latest version from PyPI into new Python 2.7 virtual environment
  (assuming OS-level prerequisites are already satisfied):

      mkvirtualenv -p python2.7 pywbem27
      pip install pywbem

* Install from master branch on GitHub into new Python 2.7 virtual environment,
  installing OS-level prerequisites as needed:

      git clone git@github.com:pywbem/pywbem.git pywbem
      cd pywbem
      mkvirtualenv -p python2.7 pywbem27
      python setup.py install_os install

  Note that you do not need to use 'sudo' in the command line, because you
  want to install into the current virtual Python. The OS-level packages are
  installed by involing 'sudo' under the covers.

* Install from a particular distribution archive on GitHub into new Python 2.7
  virtual environment, installing OS-level prerequisites as needed:

      wget https://github.com/pywbem/pywbem/blob/master/dist/pywbem-0.8.0/pywbem-0.8.0.zip
      unzip pywbem-0.8.0.zip
      cd pywbem-0.8.0
      mkvirtualenv -p python2.7 pywbem27
      python setup.py install_os install

* The installation of PyWBEM in development mode is supported as well:

      python setup.py develop_os develop

The command syntax above is shown for Linux, but this works the same way on
Windows and on other operating systems supported by Python.

Test of the installation
------------------------

To test that PyWBEM is sucessfully installed, start up a Python interpreter and
try to import the pywbem module:

    python -c "import pywbem"

If you do not see any error messages after the import command, PyWBEM has been
sucessfully installed and its Python dependencies are available.

If you have installed in development mode, you can run the test suite:

    make test
