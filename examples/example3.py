"""

Example of application of MLForge to a simple case.
(C) J. Renero, 2024

"""
# pylint: disable=E1101:no-member, W0201:attribute-defined-outside-init, W0511:fixme
# pylint: disable=C0103:invalid-name, W0611:unused-import
# pylint: disable=C0116:missing-function-docstring, C0115:missing-class-docstring
# pylint: disable=R0913:too-many-arguments, R0903:too-few-public-methods
# pylint: disable=R0914:too-many-locals, R0915:too-many-statements
# pylint: disable=W0106:expression-not-assigned, R1702:too-many-branches

from sample_classes import HostClass, SampleClass
import sys
import os

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))

from mlforge.mlforge import Pipeline


def example3():
    host = HostClass()
    pipeline = Pipeline(host, verbose=True, prog_bar=False)
    pipeline.from_config(
        "/Users/renero/phd/code/mlforge/examples/config3.yml")
    pipeline.show()
    pipeline.run()

    print(host.result1)
    print(host.param1, host.param2)

    print()


if __name__ == "__main__":
    print("Running example 3")
    example3()
