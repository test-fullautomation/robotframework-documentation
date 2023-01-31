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

The RobotFramework AIO documentation can be build either with ``genmaindoc.py`` immediately or with ``setup.py`` indirectly. The difference is that ``genmaindoc.py``
only builds the documentation, whereas ``setup.py`` additionally installs the documentation in 

   .. code::

      python39\Lib\site-packages\RobotFrameworkAIO

The execution of ``setup.py`` includes the execution of ``genmaindoc.py``.

Some preparations are necessary before ``genmaindoc.py`` or ``setup.py`` can be executed:

1. Install a LaTeX compiler (full installation of Texlive recommended)

2. Clone the `robotframework-documentation <https://github.com/test-fullautomation/robotframework-documentation>`_ repository to your computer.

   .. code::

      git clone https://github.com/test-fullautomation/robotframework-documentation.git

3. Clone all repositories containing components that shall be part of the documentation, to your computer.

   The code inside the repository ``robotframework-testsuitesmanagement`` contains a "meta information", that are the name, the version
   and the date of the entire bundle that we call "RobotFramework AIO". This information is taken over to the title page of the resulting PDF.
   Therefore including the repository ``robotframework-testsuitesmanagement`` is mandatory. The include of all other repositories is optional and
   may depend on the audience or depend on the localization (e.g. if the document shall be released Bosch internal only or in the open source
   community outside Bosch.

4. Add relative paths to these repositories to the ``genmaindoc`` configuration files inside: ``maindoc/maindoc_configs``, section ``"IMPORTS"``:

   .. code::

      "IMPORTS" : ["../../../python-genpackagedoc",
                   "../../../python-extensions-collection",
                   ...

   Currently two configuration files are available: a Bosch internal version (``maindoc_config_BIOS.json``) and an open source version (``maindoc_config_OSS.json``).

   ``genmaindoc.py`` requires such a configuration file in command line, e.g. the BIOS version:

   .. code::

      "%RobotPythonPath%/python.exe" ./genmaindoc.py --configfile "./maindoc_configs/maindoc_config_BIOS.json"


5. Introduce an environment variable ``DOCBUILDER_ARGUMENTS`` containing the command line parameters for ``genmaindoc.py``.

   ``setup.py`` is not prepared to provide any command line parameter to ``genmaindoc.py``. In case of the documentation build shall be triggered by ``setup.py``,
   another possibility is required to provide mandatory command line parameters to ``genmaindoc.py``.

   With the help of the environment variable ``DOCBUILDER_ARGUMENTS`` this can be done, e.g. like this:

   .. code::

      set DOCBUILDER_ARGUMENTS=--configfile "./maindoc_configs/maindoc_config_BIOS.json"

6. Introduce an environment variable "``GENDOC_LATEXPATH``" containing the path to the LaTeX interpreter ``pdflatex.exe`` (Windows) / ``pdflatex`` (Linux).

   This has to be configured in the ``genmaindoc`` configuration, section ``"TEX"``:

   .. code::

      "TEX" : {
               "WINDOWS" : "%GENDOC_LATEXPATH%/pdflatex.exe",
               "LINUX"   : "${GENDOC_LATEXPATH}/pdflatex"
              }

7. Use the following command to build and install the documentation:

   .. code::

      setup.py install

   The output can be found here:

   .. code::

      RobotFrameworkAIO\RobotFrameworkAIO_Reference.pdf


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

