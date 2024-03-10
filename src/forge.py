"""

Pipeline class to define and run several execution steps.
(C) J. Renero, 2023

Syntax:
    # Simply call a method of the host object
    'method_name',

    # Same, but put everything in a tuple
    ('method_name'),

    # Call a method of a class
    ('method_name', ClassHolder),

    # Call a method of the host object, and keep the result in a new attribute
    ('new_attribute', 'method_name'),

    # Call a method of the host object, with specific parameters, and keep the 
    # result in a new attribute
    ('new_attribute', 'method_name', {'param1': 'value1', 'param2': 'value2'}),

    # Call a method of the host object, with specific parameters    
    ('method_name', {'param1': 'value1', 'param2': 'value2'}),
    
    # Call a method of a specific class, with specific parameters.
    ('method_name', ClassHolder, {'param1': 'value1'}),
    
    # Call a method of a specific class, with specific parameters, and keep the
    # result in a new attribute
    ('new_attribute', 'method_name', ClassHolder, {'param1': 'value1'}),
    
"""
import inspect
import types
import typing
from dataclasses import asdict, dataclass, fields
from importlib import import_module
from random import getrandbits
from typing import Any, List, Union

from rich import print as rp
from rich.columns import Columns
from rich.table import Table
from tqdm.auto import tqdm

# pylint: disable=E1101:no-member, W0201:attribute-defined-outside-init, W0511:fixme
# pylint: disable=C0103:invalid-name
# pylint: disable=C0116:missing-function-docstring, C0115:missing-class-docstring
# pylint: disable=R0913:too-many-arguments, R0903:too-few-public-methods
# pylint: disable=R0914:too-many-locals, R0915:too-many-statements
# pylint: disable=W0106:expression-not-assigned, R1702:too-many-branches

# TODO: Eliminate the need to pass the host object to the pipeline
# TODO: Consider the case when parameters are not specified and do not exist, but
#       the method does not need them because they are optional.


@dataclass
class Stage:
    num: int
    id: str
    attribute_name: str
    method_name: str
    method_call: callable
    class_name: type
    parameters: dict
    arguments: dict


def tqdm_params(desc, prog_bar, leave=False, position=1, silent=False):
    """
    Generate parameters for tqdm progress bar.

    Parameters:
    - desc (str): Description for the progress bar.
    - prog_bar (bool): Flag indicating whether to display the progress bar.
    - leave (bool): Flag indicating whether to leave the progress bar displayed after completion.
    - position (int): Position of the progress bar in the output.
    - silent (bool): Flag indicating whether to disable the progress bar.

    Returns:
    - dict: Dictionary containing the generated parameters for tqdm progress bar.
    """
    return {
        "desc": f"{desc:<25}",
        "disable": ((not prog_bar) or silent),
        "position": position,
        "leave": leave
    }


class Pipeline:
    """
    Pipeline class allows to define several execution steps to run sequentially.
    Pipeline is initialized with a host object that contains the parameters to be
    used in the execution steps.
    At each step, the pipeline can call either a function or a class. If a class
    is called, the pipeline will call the default method of the class. Such a default
    method must be specified in the pipeline constructor.
    If a function is called, it must be present globally or inside the host object.
    The pipeline can also create an attribute inside the host object with the value
    returned by the function or the fit method of the class.
    """

    def __init__(
            self,
            host: type = None,
            prog_bar: bool = True,
            verbose: bool = False,
            silent: bool = False):
        """
        Parameters
        ----------
        host: object
            Object containing the parameters to be used in the execution steps.
        """
        self.host = host
        self.pipeline = []
        self.verbose = verbose
        self.prog_bar = prog_bar
        self.silent = silent
        self.objects_ = {'host': self.host}

    def _get_step_components(self, forge_step: tuple, stage: Stage):
        """
        Get the components of a forge step, in a way that can be used to invoke it.

        Parameters
        ----------
        forge_step: tuple
            Tuple containing the components of a forge step.
        stage: Stage
            Named tuple to store the parameters of each step.

        Returns
        -------
        attribute_name: str
            Name of the attribute to be created in the host object.
        """
        if self.verbose:
            print(f"> Into '{self._get_step_components.__name__}' "
                  f"with forge_step='{forge_step}'")

        return_vble, method_name, class_name, call_arguments = \
            self._parse_step(forge_step)

        # Store the components of the step in the stage
        stage.attribute_name = return_vble
        stage.method_name = method_name
        stage.class_name = class_name
        stage.arguments = call_arguments

        # Check if step_name is a method within Host, a method or a function in globals
        method_call = self._get_callable_method(method_name, class_name)
        parameters = inspect.signature(method_call).parameters
        method_parameters = {
            arg: parameters[arg].default for arg in parameters.keys()}

        stage.method_call = method_call
        stage.parameters = method_parameters

        # If step_parameters has 'self' as first key, remove it.
        if 'self' in method_parameters.keys():
            method_parameters.pop('self')

        # return return_vble, method_call, method_parameters, call_arguments
        return stage

    def _parse_step(self, forge_step):
        """
        Parse a forge step to know who is who. The options are

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
        ('new_attribute', 'method_name', 'object_name', {'param1': 'value1'})

        Parameters
        ----------
        step_name: str
            The forget step.

        Returns
        -------
        list
            A 4-tuple with the attribute name, the method name, the class name 
            and the parameters.
        """
        if self.verbose:
            print(f"  > Into '{self._parse_step.__name__}' "
                  f"with forge_step='{forge_step}'")

        attribute_name, method_name, class_name, parameters = None, None, None, None
        if not isinstance(forge_step, (tuple)):
            forge_step = (forge_step,)

        # Check if step_name is a string/class or a tuple. In the former case,
        # this value is a method name or a class name.
        if len(forge_step) == 1:
            if isinstance(forge_step[0], str):
                method_name = forge_step[0]
            elif isinstance(forge_step[0], type):
                class_name = forge_step[0]
            else:
                raise ValueError(
                    f"Parameter \'{forge_step}\' must be a string or a class")
        elif len(forge_step) == 2:
            # When second element is a class, the first element can be a method name
            # or an attribute name.
            if isinstance(forge_step[1], type):
                # Check if the first element is a method name or an attribute name
                if isinstance(forge_step[0], str) and \
                        self._get_callable_method(
                            forge_step[0], forge_step[1]) is not None:
                    method_name, class_name = forge_step
                elif isinstance(forge_step[0], str) and \
                        self._get_callable_method(forge_step[0], forge_step[1]) is None:
                    attribute_name, class_name = forge_step
                else:
                    raise ValueError(
                        f"First element of tuple \'{forge_step}\' must be a string "
                        f"or a method name, when the second element is a class")
            elif isinstance(forge_step[1], dict) and isinstance(forge_step[0], str):
                method_name, parameters = forge_step
            elif isinstance(forge_step[0], str) and isinstance(forge_step[1], str):
                attribute_name, method_name = forge_step
            else:
                raise ValueError(
                    f"Tuple \'{forge_step}\' with 2 elements must be either "
                    f"(str, class), (str, str) or (str, dict)")
        elif len(forge_step) == 3:
            if not isinstance(forge_step[2], dict):
                raise ValueError(
                    f"Third element of tuple \'{forge_step}\' must be a dictionary"
                    f"with arguments for the call to the method or class")
            if isinstance(forge_step[0], str) and isinstance(forge_step[1], str):
                attribute_name, method_name, parameters = forge_step
            # Check the type of the first element of the tuple. If is is a method
            # name, the second element must be a class name.
            elif self._get_callable_method(forge_step[0], forge_step[1]) is not None \
                    and isinstance(forge_step[1], type):
                method_name, class_name, parameters = forge_step
            elif self._get_callable_method(forge_step[0], forge_step[1]) is None and \
                    isinstance(forge_step[1], type):
                attribute_name, class_name, parameters = forge_step
            else:
                raise ValueError(
                    f"Tuple \'{forge_step}\' with 3 elements must be either "
                    f"(str, str, dict) or (str, class, dict)")
        elif len(forge_step) == 4:
            if isinstance(forge_step[1], str) and isinstance(forge_step[2], type) and \
                    isinstance(forge_step[3], dict):
                attribute_name, method_name, class_name, parameters = forge_step
            else:
                raise ValueError(
                    f"Tuple \'{forge_step}\' with 4 elements must be "
                    f"(str, str, class, dict)")

        return (attribute_name, method_name, class_name, parameters)

    def _get_callable_method(
            self,
            method_name: str,
            class_name: type = None) -> callable:
        """
        Given a method name, get the callable method from the `host` object, this
        very object, or the globals. If the method is not found, return None.

        Parameters
        ----------
        method_name: str
            Name of the method to be called.

        Returns
        -------
        method: callable
            Method to be called, or None if the method is not found.
        """
        if self.verbose:
            print(
                f"    > Into '{self._get_callable_method.__name__}' with "
                f"method_name='{method_name}', class_name='{class_name}'")

        # Assert that method_name is a string or None
        assert method_name is None or \
            isinstance(method_name, str), \
            f"Method name '{method_name}' must be a string or None"

        # If class_name is not None, check if method is a method of the class.
        if class_name is not None and inspect.isclass(class_name):
            if method_name is not None:
                if hasattr(class_name, method_name):
                    return getattr(class_name, method_name)
            else:
                module_name = class_name.__module__
                module = import_module(module_name)
                return getattr(module, class_name.__name__)
            return None

        # Check if the class is a valid class
        if class_name is not None and not inspect.isclass(class_name):
            raise AttributeError(f"Parameter '{class_name}' must be a class")

        # Check if 'method_name' is a method of the host object.
        if hasattr(self.host, method_name):
            return getattr(self.host, method_name)

        # Check if 'method_name' is a method in the pipeline object.
        if hasattr(self, method_name):
            return getattr(self, method_name)

        # Check if 'method_name' is a function in globals.
        if method_name in globals():
            return globals()[method_name]

        # Check if 'method_name' contains a dot (.) and if so, try to get the
        # method from the object after the dot.
        if '.' in method_name:
            obj_name, method_name = method_name.split('.')
            if hasattr(self.host, obj_name):
                obj = getattr(self.host, obj_name)
                return getattr(obj, method_name)
            raise ValueError(
                f"Object {obj_name} not found in host object")

        return None

    def _build_params(self, method_parameters, method_arguments) -> dict:
        """
        This method builds the parameters to be passed to the method, using default
        values or values from the host object.

        Parameters
        ----------
        method_parameters: dict
            Dictionary containing the parameters that the method accepts.
        method_arguments: dict
            Dictionary containing the arguments to be passed to the method.

        Returns
        -------
        params: dict
            Dictionary containing the parameters to be passed to the method.

        """
        if self.verbose:
            print(
                f"      > Into '{self._build_params.__name__}' with "
                f"method_parameters='{method_parameters}', "
                f"method_arguments='{method_arguments}'")

        params = {}
        for parameter, default_value in method_parameters.items():
            if method_arguments is not None:
                # If the parameter is in method_arguments, use the value from
                # method_arguments.
                if parameter in method_arguments:
                    # Two possibilities here: either the parameter is a normal value,
                    # in which case we simply take it, or is the name of an object created
                    # in a previous step, in which case we take the object.
                    # But first, check if the parameter is hashable.
                    if not isinstance(method_arguments[parameter], typing.Hashable):
                        params[parameter] = method_arguments[parameter]
                        continue
                    if method_arguments[parameter] in self.objects_:
                        params[parameter] = self.objects_[
                            method_arguments[parameter]]
                    else:
                        params[parameter] = method_arguments[parameter]
                    continue

            # But always, try to get the parameter from the host object or globals.
            if hasattr(self.host, parameter):
                params[parameter] = getattr(self.host, parameter)
            elif parameter in globals():
                params[parameter] = globals()[parameter]
            # or if the parameter has a default value, use it.
            elif default_value is not inspect.Parameter.empty:
                params[parameter] = default_value
                # continue
            else:
                raise ValueError(
                    f"Parameter \'{parameter}\' not found in host object or globals")

        return params

    def run(self, steps: list, desc: str = "Running pipeline"):
        """
        Run the pipeline.

        Parameters
        ----------
        steps: dict
            Dictionary containing the steps to be run. Each key can be a tuple
            containing the name of the attribute to be created in the host object
            and the function or class to be called. But also, each key can be
            a function or method name. In the case of a tuple, the value returned by
            the function or the fit method of the class will be assigned to the
            attribute of the host object. In the case of a function or method name,
            the value returned by the function or the fit method of the class will
            not be assigned to any attribute of the host object.
            The value of each key is a list of parameters to be passed to the 
            function or class. Each parameter must be a string corresponding to
            an attribute of the host object or a value.
        """
        self._pbar = tqdm(total=len(steps),
                          **tqdm_params(desc, self.prog_bar, leave=False, position=0,
                                        silent=self.silent))
        self._pbar.update(0)
        print("-"*100) if self.verbose else None

        for step_number, step_name in enumerate(steps):
            # Create a new stage of type Stage, and initialize it with the step number
            # and a random id.
            stage = Stage(
                step_number, f"{getrandbits(32):08x}",
                None, None, None, None, None, None)

            if self.verbose:
                print(f"Step #{step_number}({stage.id}) {str(step_name)}")

            # Get the method to be called, the parameters that the
            # method accepts and the arguments to be passed to the method.
            # The variable name is the name to be given to the result of the call.
            # vble_name, step_call, step_parameters, step_arguments = \
            #     self._get_step_components(step_name, stage)
            stage = self._get_step_components(step_name, stage)

            # Given the parameters that the method accepts and the arguments
            # passed for the method, build the parameters to be passed to the
            # method, using default values or values from the host object.
            step_parameters = self._build_params(
                stage.parameters, stage.arguments)
            return_value = self._run_step(stage.method_call, step_parameters)

            # If return value needs to be stored in a variable, do it.
            if stage.attribute_name is not None:
                setattr(self.host, stage.attribute_name, return_value)
                # Check if the new attribute created is an object and if so,
                # add it to the list of objects.
                if not isinstance(return_value, type):
                    self.objects_[stage.attribute_name] = return_value
                if self.verbose:
                    print(f"      New attribute: <{stage.attribute_name}>")

            self.pipeline.append(stage)

            print("-"*100) if self.verbose else None
            self._pbar_update(1)

        self._pbar.close()

    def _run_step(
            self,
            step_name: Union[Any, str],
            list_of_params: List[Any] = None) -> Any:
        """
        Run a step of the pipeline.

        Parameters
        ----------
        step_name: str
            Function or class to be called.
        list_of_params: list
            List of parameters to be passed to the function or class.

        Returns
        -------
        return_value: any
            Value returned by the function or the fit method of the class.
        """
        return_value = None
        if list_of_params is None:
            list_of_params = []

        # Check if step_name is a function or a class already in globals
        if step_name in globals():
            step_name = globals()[step_name]
            # check if type of step_name is a function
            if isinstance(step_name, (types.FunctionType, types.MethodType)):
                return_value = step_name(**list_of_params)
            # check if type of step_name is a class
            elif isinstance(step_name, type):
                obj = step_name(**list_of_params)
                obj.fit()
                return_value = obj
            else:
                raise TypeError("step_name must be a class or a function")
        # Check if step_name is a function or a class in the calling module
        elif not isinstance(step_name, str) and hasattr(step_name, '__module__'):
            # check if type of step_name is a function
            if isinstance(step_name, (types.FunctionType, types.MethodType)):
                return_value = step_name(**list_of_params)
            # check if type of step_name is a class
            elif isinstance(step_name, type) or inspect.isclass(step_name):
                obj = step_name(**list_of_params)
                return_value = obj
            else:
                raise TypeError("step_name must be a class or a function")
        # Check if step_name is a method of the host object
        elif hasattr(self.host, step_name):
            step_name = getattr(self.host, step_name)
            # check if type of step_name is a function
            if isinstance(step_name, (types.FunctionType, types.MethodType)):
                return_value = step_name(**list_of_params)
            else:
                raise TypeError(
                    "step_name inside host object must be a function")
        # Consider that step_name is a method of some of the intermediate objects
        # in the pipeline
        else:
            # check if step name is of the form object.method
            if '.' not in step_name:
                raise ValueError(
                    f"step_name ({step_name}) must be method of an object: object.method")
            method_call = step_name
            root_object = self.host
            while '.' in method_call:
                call_composition = step_name.split('.')
                obj_name = call_composition[0]
                method_name = method_name = '.'.join(call_composition[1:])
                obj = getattr(root_object, obj_name)
                call_name = getattr(obj, method_name)
                method_call = '.'.join(method_name.split('.')[1:])
            return_value = call_name(**list_of_params)

        print("    > Return value:", type(
            return_value)) if self.verbose else None
        return return_value

    def _pbar_update(self, step=1):
        self._pbar.update(step)
        self._pbar.refresh()

    def show(self):
        """
        Show the pipeline. Print cards with the steps and the description of each step.
        """
        columns_layout = []
        table = []
        num_stages = len(self.pipeline)
        for i in range(num_stages):
            table.append(Table())
            table[i].add_column(
                f"[white]Stage #{i}, id: #{self.pipeline[i].id}[/white]",
                justify="left", no_wrap=True)
            line = ""
            # Loop through the elements of the stage tuple
            for k, v in asdict(self.pipeline[i]).items():
                if k == 'num' or k == 'id' or k == 'method_call' or k == "parameters" \
                        or v is None:
                    continue
                if isinstance(v, dict) and v:
                    line += f"[yellow1]{k}[/yellow1]:\n"
                    for k1, v1 in v.items():
                        line += f"- [orange1]{k1}[/orange1]: {v1}\n"
                elif isinstance(v, type):
                    line += f"[yellow1]{k}[/yellow1]: {v.__name__}\n"
                else:
                    line += f"[yellow1]{k}[/yellow1]: {v}\n"

            # Remove trailing newline from `line`
            line = line.rstrip("\n")
            table[i].add_row(line)
            columns_layout.append(table[i])
            if i < num_stages-1:
                columns_layout.append("\n->")

        columns = Columns(columns_layout)
        rp(columns)
