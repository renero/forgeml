"""

Example of application of ForgeML to a simple case.
(C) J. Renero, 2024

"""
from forge import Pipeline


# pylint: disable=E1101:no-member, W0201:attribute-defined-outside-init, W0511:fixme
# pylint: disable=C0103:invalid-name
# pylint: disable=C0116:missing-function-docstring, C0115:missing-class-docstring
# pylint: disable=R0913:too-many-arguments, R0903:too-few-public-methods
# pylint: disable=R0914:too-many-locals, R0915:too-many-statements
# pylint: disable=W0106:expression-not-assigned, R1702:too-many-branches


class HostClass:
    def __init__(self, param1=None, param2=None):
        self.param1 = param1
        self.param2 = param2

    def host_method(self, param1=None, param2=None):
        print(f"  > Calling the method \'my_method()\'\n"
              f"    > I got params: param1={param1}, param2={param2}")
        self.param1 = param1
        self.param2 = param2
        return f"host_method({param1}, {param2})"


class SampleClass:
    def __init__(self, param1=None, param2=False):
        self.param1 = param1
        self.param2 = param2
        print(f"  > Called the init of class {self.__class__}\n"
              f"    > I got params: {self.param1}, {self.param2}")

    @staticmethod
    def method():
        print(
            f"  > Called static method \'{SampleClass.method.__name__}\'")
        return "Hi"

    def object_method(self):
        print(f"  > Called object method {self.object_method.__name__}\n"
              f"    > I have params: {self.param1}, {self.param2}")
        return "there!"


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

    pipeline.run(steps)

    print(host.result1)
    print(host.result2)
    print(host.param1, host.param2)

    print()
    pipeline.show()


if __name__ == "__main__":
    print("Running example 1")
    example1()
