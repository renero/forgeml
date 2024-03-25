ForgeML
=======

|build-status| |coverage| |wheel| |documentation|


**ForgeML** is a simple package to write simple pipelines of calls (to methods, classes, ...).

This is a Work in Progress.

It surges from the need to execute several things in a row, and to be able to
easily add or remove steps in the pipeline.

.. include:: docs/source/usage.rst


To do
-----

- Add a logger
- Add a way to add a step at a specific position
- Add a way to remove a step
- Add a way to replace a step
- Add a way to add a step before or after another step
- And many other things...



.. |build-status| image:: https://github.com/renero/mlforge/actions/workflows/python-test.yml/badge.svg
    :target: https://github.com/renero/mlforge/actions/workflows/python-test.yml
    :alt: Tests Status

.. |coverage| image:: https://codecov.io/gh/renero/mlforge/graph/badge.svg?token=HRZAE9GS0I 
    :target: https://codecov.io/gh/renero/mlforge
    :alt: Code Coverage

.. |wheel| image:: https://github.com/renero/mlforge/actions/workflows/python-publish.yml/badge.svg
    :target: https://pypi.org/project/mlforge/
    :alt: PyPi Publish Status

.. |documentation| image:: https://readthedocs.org/projects/mlforge/badge/?version=latest
    :target: https://mlforge.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status
