"""

Tests for the forge module.

"""
# pylint: disable=E1101:no-member, W0201:attribute-defined-outside-init, W0511:fixme
# pylint: disable=C0103:invalid-name, W0212:protected-access
# pylint: disable=C0116:missing-function-docstring, C0115:missing-class-docstring
# pylint: disable=R0913:too-many-arguments, R0903:too-few-public-methods
# pylint: disable=R0914:too-many-locals, R0915:too-many-statements
# pylint: disable=W0106:expression-not-assigned, R1702:too-many-branches
# pylint: disable=C0413:import-misplaced

import os
import sys

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../mlforge')))

from mlforge import Pipeline

# Used to test access to global classes
class SomeClass:
    def __init__(self):
        pass

    def method_name(self):
        pass


def global_method():
    # Used to test access to global methods
    pass


def test_parse_step():
    """
    Depending on the length, we can have different scenarios:

        'method_name'
        ClassHolder
        ('method_name')
        (ClassHolder)

        ('method_name', ClassHolder)
        ('new_attribute', 'method_name')
        ('new_attribute', ClassHolder)
        ('method_name', {'param1': 'value1'})

        ('new_attribute', 'method_name', {'param1': 'value1'})
        ('new_attribute', ClassHolder, {'param1': 'value1'})
        ('method_name', ClassHolder, {'param1': 'value1'})

        ('new_attribute', 'method_name', ClassHolder, {'param1': 'value1'})

    """
    forge = Pipeline()

    # Test case 1: step_name is a string
    attribute_name, method_name, class_name, arguments = forge._parse_step(
        "step_name")
    assert attribute_name is None
    assert method_name == "step_name"
    assert class_name is None
    assert arguments is None

    # Test case 1b: step_name is a string
    attribute_name, method_name, class_name, arguments = forge._parse_step(
        ("method_name"))
    assert attribute_name is None
    assert method_name == "method_name"
    assert class_name is None
    assert arguments is None

    # Test case 1b: step_name is a string
    attribute_name, method_name, class_name, arguments = forge._parse_step(
        (SomeClass))
    assert attribute_name is None
    assert method_name is None
    assert class_name == SomeClass
    assert arguments is None

    # Test case 2: step_name is a tuple with length 2
    attribute_name, method_name, class_name, arguments = forge._parse_step(
        ("attribute_name", "method_name"))
    assert attribute_name == "attribute_name"
    assert method_name == "method_name"
    assert class_name is None
    assert arguments is None

    # Test case 2: the method does not exists, so the __init__ method should be called.
    attribute_name, method_name, class_name, arguments = forge._parse_step(
        ("attribute_name", SomeClass))
    assert attribute_name == "attribute_name"
    assert method_name is None
    assert class_name == SomeClass
    assert arguments is None

    # Test case 2b: step_name is a tuple with length 2
    attribute_name, method_name, class_name, arguments = forge._parse_step(
        ("method_name", SomeClass))
    assert attribute_name is None
    assert method_name == "method_name"
    assert class_name == SomeClass
    assert arguments is None

    # Test case 2c: step_name is a tuple with length 2
    attribute_name, method_name, class_name, arguments = forge._parse_step(
        ("method_name", {"param": "value"}))
    assert attribute_name is None
    assert method_name == "method_name"
    assert class_name is None
    assert arguments == {"param": "value"}

    # Test case 3: step_name is a tuple with length 3
    attribute_name, method_name, class_name, arguments = forge._parse_step(
        ("method_name", SomeClass, {"param": "value"}))
    assert attribute_name is None
    assert method_name == "method_name"
    assert class_name == SomeClass
    assert arguments == {"param": "value"}

    # Test case 3b: step_name is a tuple with length 3
    attribute_name, method_name, class_name, arguments = forge._parse_step(
        ("attribute_name", "method_name", {"param": "value"}))
    assert attribute_name == "attribute_name"
    assert method_name == "method_name"
    assert class_name is None
    assert arguments == {"param": "value"}

    # Test case 3c: step_name is a tuple with length 3
    attribute_name, method_name, class_name, arguments = forge._parse_step(
        ("attribute_name", SomeClass, {"param": "value"}))
    assert attribute_name == "attribute_name"
    assert method_name is None
    assert class_name == SomeClass
    assert arguments == {"param": "value"}

    # Test case 4: step_name is a tuple with length 4
    attribute_name, method_name, class_name, arguments = forge._parse_step(
        ("attribute_name", "method_name", SomeClass, {"param": "value"}))
    assert attribute_name == "attribute_name"
    assert method_name == "method_name"
    assert class_name == SomeClass
    assert arguments == {"param": "value"}


def test_get_callable_method():
    # Pipeline without host
    forge = Pipeline()

    # method_name is a method of SomeClass
    method = forge._get_callable_method("method_name", SomeClass)
    assert method is not None

    # wrong_method is NOT a method of SomeClass
    method = forge._get_callable_method("wrong_method", SomeClass)
    assert method is None

    # The class sent does not exist
    try:
        method = forge._get_callable_method(
            "method_name", test_get_callable_method)
        catch = False
    except AttributeError:
        catch = True
    assert catch

    # Now, with a host object
    forge = Pipeline(host=SomeClass())

    # Test case 1: method_name is a method of the host object
    method = forge._get_callable_method("method_name")
    assert method is not None

    # Test case 2: method_name is a method in the pipeline object
    # Create a method in the pipeline object
    setattr(forge, "local_method", lambda: None)
    method = forge._get_callable_method("local_method")
    assert method is not None

    # CANNOT test this since tests are in a different namespace
    # Test case 3: method_name is a function in globals
    # globals()["global_method"] = global_function
    # method = forge._get_callable_method("global_method")
    # assert method is not None

    # Test case 4: method_name is not found
    method = forge._get_callable_method("nonexistent_method")
    assert method is None
