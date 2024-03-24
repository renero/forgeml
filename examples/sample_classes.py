"""
    Sample classes for the examples in the documentation.
"""


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
