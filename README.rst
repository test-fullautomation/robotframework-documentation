.. Copyright 2020-2022 Robert Bosch GmbH

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

With the ``setup.py`` within this repository the documentation can be build also.

The following preconditions have to be fulfilled before ``setup.py`` is executed:

1. Clone the `robotframework-documentation <https://github.com/test-fullautomation/robotframework-documentation>`_ repository to your computer.

   .. code::

      git clone https://github.com/test-fullautomation/robotframework-documentation.git


1. Clone all repositories containing components that shall be part of the documentation, to your computer.

2. Add relative paths to these repositories to the ``maindoc`` configuration: ``maindoc\maindoc_config.json``, section "``IMPORTS``":

   .. code::

      "IMPORTS" : ["../../python-genpackagedoc",
                   "../../python-extensions-collection",
                   ...

3. Install a LaTeX compiler (full installation of Texlive recommended)

4. Introduce an environment variable "``GENDOC_LATEXPATH``" containing the path to the LaTeX interpreter ``pdflatex.exe`` (Windows) / ``pdflatex`` (Linux).

   This is also configured in the ``maindoc`` configuration: ``maindoc\maindoc_config.json``, section "``TEX``":

   .. code::

      "TEX" : {
               "WINDOWS" : "%GENDOC_LATEXPATH%/pdflatex.exe",
               "LINUX"   : "${GENDOC_LATEXPATH}/pdflatex"
              }

5. Use the following command to build the documentation:

   .. code::

      setup.py install

   The output can be found here:

   ``RobotFrameworkAIO\RobotFrameworkAIO_Reference.pdf``


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

Copyright 2020-2022 Robert Bosch GmbH

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

