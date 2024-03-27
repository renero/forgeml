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

import time
from mlforge import Pipeline


class SlowClass:
    def __init__(self):
        pass

    def slow_method(self, num_steps, delay):
        for _ in range(num_steps):
            time.sleep(delay)


def example4():
    pipeline = Pipeline()
    pipeline.from_config(
        "/Users/renero/phd/code/mlforge/examples/.config4.yaml")
    pipeline.run()


if __name__ == "__main__":
    print("Running example 4")
    example4()
