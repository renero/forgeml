"""

Example of application of MLForge to a simple case.
(C) J. Renero, 2024

"""
from sample_classes import HostClass, SampleClass

from mlforge import Pipeline

# pylint: disable=E1101:no-member, W0201:attribute-defined-outside-init, W0511:fixme
# pylint: disable=C0103:invalid-name
# pylint: disable=C0116:missing-function-docstring, C0115:missing-class-docstring
# pylint: disable=R0913:too-many-arguments, R0903:too-few-public-methods
# pylint: disable=R0914:too-many-locals, R0915:too-many-statements
# pylint: disable=W0106:expression-not-assigned, R1702:too-many-branches


def example1():
    host = HostClass()
    pipeline = Pipeline(host, verbose=True, prog_bar=False)
    steps = [
        ('method', SampleClass),
        ('object', SampleClass),
        ('result1', 'method', SampleClass, {'param2': 'there!'}),
        ('result2', 'object.object_method'),

        'host_method',
        ('host_method', {'param1': 'Hello', 'param2': 'there'}),
    ]

    pipeline.from_list(steps)
    pipeline.run()

    print(host.result1)
    print(host.result2)
    print(host.param1, host.param2)

    print()
    pipeline.show()


if __name__ == "__main__":
    print("Running example 1")
    example1()
