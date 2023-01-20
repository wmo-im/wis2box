.. _development:

Development
===========

wis2box is developed as a free and open source project on GitHub. The wis2box
codebase can be found at https://github.com/wmo-im/wis2box.


GitHub
------

wis2box can be installed using the git CLI as follows:

.. code-block:: bash

    # clone wis2box GitHub repository
    git clone https://github.com/wmo-im/wis2box.git
    cd wis2box

Testing
-------

wis2box continuous integration (CI) testing is managed by GitHub Actions. All commits and
pull requests to wis2box trigger continuous integration (CI) testing on `GitHub Actions`_.

GitHub Actions invokes functional testing as well as integration testing to ensure regressions.

Integration testing
^^^^^^^^^^^^^^^^^^^

Integration tests are in ``tests/integration/integration.py``.

Functional testing
^^^^^^^^^^^^^^^^^^

Functional tests are defined as part of GitHub Actions in ``.github/workflows/tests-docker.yml``.

Versioning
----------

wis2box follows the `Semantic Versioning Specification (SemVer)`_.

Code Conventions
-----------------

Python code follows `PEP8`_ coding conventions.


.. _`GitHub Actions`: https://github.com/wmo-im/wis2box/blob/main/.github/workflows/tests-docker.yml
.. _`Semantic Versioning Specification (SemVer)`: https://semver.org
.. _`PEP8`: https://peps.python.org/pep-0008
