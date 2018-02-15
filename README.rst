Pytest Clickpecker plugin
#########################

This extension allows you to organise and launch your tests with py.test
Python library.

Features
========

Pytest-Clickpecker allows:
    * Acquire and release devices from Device Manager automatically
    * Save device scrrenshot history to PDF (tags are saved separately for now)
    * Save device logcat (using functions from ``utils`` module)

Requirements and Installation
=============================

This extension requires:
    * Requests library
    * Clickpecker library
    * Clickpecker Device Manager
    * Pytest

To work with Android OS versions use ``packaging`` library

**Install plugin from source code**::

    pip install git+https://github.com/VladX09/clickpecker-pytest.git

Launching tests
===============

All standard pytest launching methods are available. 
To specify output directory for screenshot history, logcat, traces, etc. use
``--output-dir`` option of ``pytest`` runner. If this option is ommited
``<rootdir>/output/`` directory will be created and used.
(``<rootdir>/`` is the nearest directory with ``.conftest`` file, for more
information `check this <https://docs.pytest.org/en/latest/customize.html#finding-the-rootdir>`_).

Fixtures
========

This plugin contains some usefull fixtures.

output_dir
  Obtain output directory. Returns pathlib.Path object with ``<rootdir>/output/``
  or directory specified in ``--output-dir`` pytest parameter.

testing_api
  Returns contextmanager which allows to acquire specific device from device manager
  and release it automatically.

Utilits
=======

``pytest_clickpecker.utils`` module contains simple but yet usefull functions for:
    * Acquiring/releasing devices from device/manager
    * Creating files with unique and informative names
    * Saving logcat and screen history

See ``examples/`` to understand, how to use and extend this plugin.
