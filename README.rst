.. Copyright 2020-2026 Robert Bosch GmbH

.. Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

.. http://www.apache.org/licenses/LICENSE-2.0

.. Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

RobotFramework AIO documentation
================================

The RobotFramework AIO documentation is available as PDF file and can be found here:
`RobotFrameworkAIO_Reference.pdf <https://github.com/test-fullautomation/robotframework-documentation/blob/develop/RobotFrameworkAIO/RobotFrameworkAIO_Reference.pdf>`_

The documentation consists of two parts:

1. Common description
2. Description of the interfaces of RobotFramework AIO components

How to render
-------------

The **RobotFramework AIO** documentation can be rendered with ``genmaindoc.py``. This requires:

* A Python installation
* A PyPi package ``GenPackageDoc``
* A LaTeX installation

All details about the steps that are required for all installations can be found here:
`README.rst <https://github.com/test-fullautomation/python-genpackagedoc/blob/develop/README.rst>`_

**In detail:**

1. Install a LaTeX compiler (full installation of Texlive recommended)

2. Clone the `robotframework-documentation <https://github.com/test-fullautomation/robotframework-documentation>`_ repository to your computer.

   .. code::

      git clone https://github.com/test-fullautomation/robotframework-documentation.git

3. Clone all repositories containing components that shall be part of the documentation, to your computer.

4. Add relative paths to these repositories to the ``genmaindoc`` configuration files inside: ``maindoc/maindoc_configs``, section ``"IMPORTS"``:

   .. code::

      "IMPORTS" : ["../../../python-genpackagedoc",
                   "../../../python-extensions-collection",
                   ...

5. Prepare the ``genmaindoc.py`` command line

   ``genmaindoc.py`` requires the following command line parameters:

   * ``--configfile`` : Path and name of maindoc configuration file
   * ``--bundle_name`` : The name of the entire framework bundle
   * ``--bundle_version`` : The version of the entire framework bundle
   * ``--bundle_version_date`` : The version date of the entire framework bundle

   The values are taken over to the resulting PDF file (e.g. in the title page).

6. Introduce an environment variable "``GENDOC_LATEXPATH``" containing the path to the LaTeX interpreter ``pdflatex.exe`` (Windows) / ``pdflatex`` (Linux).

   This has to be configured in the ``genmaindoc`` configuration, section ``"TEX"``:

   .. code::

      "TEX" : {
               "WINDOWS" : "%GENDOC_LATEXPATH%/pdflatex.exe",
               "LINUX"   : "${GENDOC_LATEXPATH}/pdflatex"
              }

7. Optionally it is possible to install the documentation under ``site-packages``.

   .. code::

      python -m pip install .

   The output can be found here:

   .. code::

      RobotFrameworkAIO\RobotFrameworkAIO_Reference.pdf

   The name of the PDF file is defined in the ``genmaindoc`` configuration.


Feedback
--------

To give us a feedback, you can send an email to `Thomas Pollerspöck <mailto:Thomas.Pollerspoeck@de.bosch.com>`_

In case you want to report a bug or request any interesting feature, please don't
hesitate to raise a ticket.

Maintainers
-----------

`Thomas Pollerspöck <mailto:Thomas.Pollerspoeck@de.bosch.com>`_

Contributors
------------


License
-------

Copyright 2020-2026 Robert Bosch GmbH

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    |License: Apache v2|

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.


.. |License: Apache v2| image:: https://img.shields.io/pypi/l/robotframework.svg
   :target: http://www.apache.org/licenses/LICENSE-2.0.html

