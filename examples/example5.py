"""

Example of application of MLForge to a simple case.
(C) J. Renero, 2024

"""
from sample_classes import HostClass, SampleClass
import sys
import os

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))

from mlforge.mlforge import Pipeline, Stage

# pylint: disable=E1101:no-member, W0201:attribute-defined-outside-init, W0511:fixme
# pylint: disable=C0103:invalid-name
# pylint: disable=C0116:missing-function-docstring, C0115:missing-class-docstring
# pylint: disable=R0913:too-many-arguments, R0903:too-few-public-methods
# pylint: disable=R0914:too-many-locals, R0915:too-many-statements
# pylint: disable=W0106:expression-not-assigned, R1702:too-many-branches


def example5():
    host = HostClass()

    stage1 = Stage(method_name='method', class_name=SampleClass)
    stage2 = Stage(attribute_name='object', class_name=SampleClass)
    stage3 = Stage(attribute_name='result1', method_name='method',
                   class_name=SampleClass, arguments={'param2': 'there!'})
    stage4 = Stage(attribute_name='result2', method_name='object.object_method')
    stage5 = Stage(method_name='host_method')
    stage6 = Stage(method_name='host_method',
                   arguments={'param1': 'Hello', 'param2': 'there'})

    pipeline = Pipeline(host, log_level="info", verbose=True, prog_bar=False)
    pipeline.add_stages([stage1, stage2, stage3, stage4, stage5, stage6])
    pipeline.run()

    pipeline.show()
    pipeline.close()


if __name__ == "__main__":
    print("Running example 5")
    example5()
