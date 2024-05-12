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

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))

from mlforge.progbar import ProgBar
from mlforge.mlforge import Pipeline, Stage


class SlowClass:
    def __init__(self):
        pass

    def slow_method(self, num_steps, delay):
        p = ProgBar().start_subtask(num_steps)
        for _ in range(num_steps):
            time.sleep(delay)
            p.update_subtask()


class SlowPredictClass:
    def __init__(self):
        self.myname="SlowPredictClass"

    def slow_method(self, num_steps, delay):
        p = ProgBar().start_subtask(num_steps)
        for _ in range(num_steps):
            time.sleep(delay)
            p.update_subtask()


class Fit:
    def __init__(self):
        self.pipeline = Pipeline(subtask=True, description="Fit")
        self.pipeline.from_config(
            "/Users/renero/phd/code/mlforge/examples/.config6.yaml")

    def run(self):
        self.pipeline.run()


class Predict:
    def __init__(self):
        self.pipeline = Pipeline(subtask=True, description="Predict")
        stage1 = Stage(attribute_name="slow_object", class_name=SlowPredictClass)
        stage2 = Stage(method_name="slow_object.slow_method",
                       arguments={"num_steps": 10, "delay": 0.1})
        stage3 = Stage(method_name="slow_object.slow_method",
                          arguments={"num_steps": 10, "delay": 0.1})
        self.pipeline.add_stages([stage1, stage2, stage3])

    def run(self):
        self.pipeline.run()


if __name__ == "__main__":
    print("Running example 6")
    Fit().run()
    Predict().run()

