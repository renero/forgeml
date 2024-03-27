"""

Example of application of MLForge to a simple case.
(C) J. Renero, 2024

"""
import numpy as np
import pandas as pd

from mlforge import Pipeline


# pylint: disable=E1101:no-member, W0201:attribute-defined-outside-init, W0511:fixme
# pylint: disable=C0103:invalid-name
# pylint: disable=C0116:missing-function-docstring, C0115:missing-class-docstring
# pylint: disable=R0913:too-many-arguments, R0903:too-few-public-methods
# pylint: disable=R0914:too-many-locals, R0915:too-many-statements
# pylint: disable=W0106:expression-not-assigned, R1702:too-many-branches


class Host:
    def __init__(self, param1, param2):
        self.param1 = param1
        self.param2 = param2
        self.X = pd.DataFrame(np.random.randint(
            0, 100, size=(100, 4)), columns=list('ABCD'))

    def host_method(self):
        return "Host.host_method"

    def my_method(self, param1, param2):
        return f"my_method({param1} {param2})"

    def method_with_object(self, obj):
        return f"{obj.method()}>"

    def m1(self, message="default_message"):
        return f"m1_return_value={message}"

    def m2(self, msg):
        return f"m2_return_value={msg}"

    def m3(self, msg):
        return f"m3 dataframe argument shape={msg.shape}"


class SampleClass:
    def __init__(self, param1=None, param2=False):
        self.param1 = param1
        self.param2 = param2
        self.fitted = False

    def fit(self):
        self.fitted = True
        return self

    def method(self):
        return "<Have been in SampleClass.method>"


what_msg = "(argument for m1 and m2)"


def example2():
    host = Host('host_value1', 'host_value2')
    pipeline = Pipeline(host)
    print(f"Host object: {host}")
    print(f"Pipeline initiated: {pipeline}")

    steps = [
        ('myobject1', SampleClass),
        ('method_with_object', {'obj': 'myobject1'}),
        ('r1', 'm1'),
        ('r2', 'm2', {'msg': 'new_what_value'}),
        ('r3', 'm2', {'msg': host.X}),
        ('myobject2', SampleClass, {'param2': True}),
        ('myobject2.fit'),
        'myobject2.method',
        'host_method',
        ('my_method')
    ]
    pipeline.from_list(steps)
    pipeline.run()


if __name__ == "__main__":
    example2()
