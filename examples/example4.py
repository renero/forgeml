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
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from mlforge.mlforge import Pipeline
from mlforge.progbar import ProgBar


class SlowClass:
    def __init__(self):
        pass

    def slow_method(self, num_steps, delay):
        p = ProgBar().start_subtask(num_steps)
        for _ in range(num_steps):
            time.sleep(delay)
            p.update_subtask()

class Example:
    def __init__(self):
        self.pipeline = Pipeline(subtask=True, description="Example 4")
        self.pipeline.from_config(
            "/Users/renero/phd/code/mlforge/examples/.config4.yaml")

    def run(self):
        self.pipeline.run()


if __name__ == "__main__":
    print("Running example 4")
    example4 = Example()
    example4.run()
