"""

Pipeline class to define and run several execution steps.

(C) J. Renero, 2023

"""
import importlib
import inspect
import types
import typing
from dataclasses import asdict, dataclass
from importlib import import_module
from random import getrandbits
from typing import Any, List, Union

import yaml
from rich import print as rp
from rich.columns import Columns
from rich.table import Table
from tqdm.auto import tqdm

# pylint: disable=E1101:no-member, W0201:attribute-defined-outside-init, W0511:fixme
# pylint: disable=C0103:invalid-name, R0902:too-many-instance-attributes
# pylint: disable=C0116:missing-function-docstring, C0115:missing-class-docstring
# pylint: disable=R0913:too-many-arguments, R0903:too-few-public-methods
# pylint: disable=R0914:too-many-locals, R0915:too-many-statements
# pylint: disable=W0106:expression-not-assigned, R1702:too-many-branches
# pylint: disable=W0212:protected-access


@dataclass
class Stage:
    _num: int = None
    _id: str = None
    attribute_name: str = None
    method_name: str = None
    _method_call: callable = None
    class_name: type = None
    _parameters: dict = None
    arguments: dict = None


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

    Parameters
    ----------
    host: object
        Object containing the parameters to be used in the execution steps.
    prog_bar: bool
        Flag indicating whether to display the progress bar.
    prog_bar_params: dict
        Dictionary containing the parameters for the progress bar.
    verbose: bool
        Flag indicating whether to display verbose output.
    silent: bool
        Flag indicating whether to disable the progress bar.
    """

    def __init__(
            self,
            host: type = None,
            prog_bar: bool = True,
            prog_bar_params: dict = None,
            verbose: bool = False,
            silent: bool = False):
        self.host = host
        self.pipeline = []
        self.verbose = verbose
        self.prog_bar = prog_bar
        self.prog_bar_params = {
            "desc": "Running pipeline",
            "disable": ((not self.prog_bar) or silent),
            "position": 1,
            "leave": False
        }
        if prog_bar_params is not None:
            self.prog_bar_params.update(
                {k: v for k, v in prog_bar_params.items() if k in self.prog_bar_params})

        self.silent = silent
        self.objects_ = {'host': self.host}

    def from_list(self, steps: list):
        """
        Load a pipeline from a list of steps.

        Parameters
        ----------
        steps: list
            List of steps to be run. Each step can be a tuple containing the name
            of the attribute to be created in the host object and the function or
            class to be called. But also, each step can be a function or method name.
            In the case of a tuple, the value returned by the function or the fit
            method of the class will be assigned to the attribute of the host object.
            In the case of a function or method name, the value returned by the
            function or the fit method of the class will not be
            assigned to any attribute of the host object.

        """
        if self.verbose:
            print(
                f"Into '{self.from_list.__name__}' with '{len(steps)}' steps")
        for step_number, step_name in enumerate(steps):
            # Create a new stage of type Stage, and initialize it with the step number
            # and a random id.
            stage = Stage(
                step_number, f"{getrandbits(32):08x}",
                None, None, None, None, None, None)

            if self.verbose:
                print(f"> Step #{step_number}({stage._id}) {str(step_name)}")

            # Get the method to be called, the parameters that the
            # method accepts and the arguments to be passed to the method.
            # The variable name is the name to be given to the result of the call.
            # vble_name, step_call, step_parameters, step_arguments = \
            #     self._get_step_components(step_name, stage)
            stage = self._get_step_components(step_name, stage)

            self.pipeline.append(stage)

    def from_config(self, config_filename: str):
        """
        Load a pipeline from a YAML configuration file.

        Parameters
        ----------
        config_filename: str
            Name of the YAML configuration file.
        """
        if self.verbose:
            print(f"Into '{self.from_config.__name__}' with "
                  f"config_filename='{config_filename}'")

        with open(config_filename, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)

        # Retrieve the caller's module name
        caller_module = inspect.stack()[1].frame.f_globals['__name__']

        # Process the config and set the pipeline steps
        self.pipeline = self._process_config(config, caller_module)

    def run(self):
        """
        Run the pipeline.

        Parameters
        ----------
        steps: list
            List of steps to be run. Each step can be a tuple containing the name
            of the attribute to be created in the host object and the function or
            class to be called. But also, each step can be a function or method name.
            In the case of a tuple, the value returned by the function or the fit
            method of the class will be assigned to the attribute of the host object.
            In the case of a function or method name, the value returned by the
            function or the fit method of the class will not be assigned to any
            attribute of the host object.
        """
        assert self.pipeline, "Pipeline is empty. No steps to run."
        self._pbar_create()
        if self.verbose:
            print(f"RUN pipeline with {len(self.pipeline)} steps")

        for stage in self.pipeline:
            if self.verbose:
                print(f"  > Step #{stage._num:>03d}({stage._id})")
                print(f"    > attribute_name: {stage.attribute_name}")
                print(f"    > method_name: {stage.method_name}")
                print(f"    > class_name: {stage.class_name}")
                print(f"    > arguments: {stage.arguments}")
            # Check if step_name is a method within Host, a method or a function in globals
            stage._method_call = self._get_callable_method(
                stage.method_name, stage.class_name)
            stage._parameters = self._get_method_signature(stage._method_call)

            # If step_parameters has 'self' as first key, remove it.
            if 'self' in stage._parameters.keys():
                stage._parameters.pop('self')

            # Given the parameters that the method accepts and the arguments
            # passed for the method, build the parameters to be passed to the
            # method, using default values or values from the host object.
            step_parameters = self._build_params(
                stage._parameters, stage.arguments)
            return_value = self._run_step(stage._method_call, step_parameters)

            # If return value needs to be stored in a variable, do it.
            if stage.attribute_name is not None:
                setattr(self.host, stage.attribute_name, return_value)
                # Check if the new attribute created is an object and if so,
                # add it to the list of objects.
                if not isinstance(return_value, type):
                    self.objects_[stage.attribute_name] = return_value
                if self.verbose:
                    print(f"      New attribute: <{stage.attribute_name}>")

            print("-"*100) if self.verbose else None
            self._pbar_update(1)

        self._pbar_close()

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
            print(f"  > Into '{self._get_step_components.__name__}' "
                  f"with forge_step='{forge_step}'")

        stage.attribute_name, stage.method_name, stage.class_name, stage.arguments = \
            self._parse_step(forge_step)

        return stage

    def _get_method_signature(self, method_call):
        """
        Get the signature of a method.

        Parameters:
        - method_call: The method to get the signature of.

        Returns:
        - method_parameters: A dictionary containing the method's parameters and their 
            default values.
        """
        parameters = inspect.signature(method_call).parameters
        if parameters is None:
            return None

        return {arg: parameters[arg].default for arg in parameters.keys()}

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
            print(f"    > Into '{self._parse_step.__name__}' "
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
                f"      > Into '{self._get_callable_method.__name__}' with "
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
                f"        > Into '{self._build_params.__name__}' with "
                f"method_parameters='{method_parameters}', "
                f"method_arguments='{method_arguments}'")

        params = {}
        for parameter, default_value in method_parameters.items():
            if method_arguments is not None:
                # If the parameter is in method_arguments, use the value from
                # method_arguments.
                if parameter in method_arguments:
                    # Two possibilities here: either the parameter is a normal value,
                    # in which case we simply take it, or is the name of an object
                    # created in a previous step, in which case we take the object.
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
                    f"step_name ({step_name}) must be object's method: object.method")
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

        print("      > Return value:", type(
            return_value)) if self.verbose else None
        return return_value

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
                f"[white]Stage #{i}, id: #{self.pipeline[i]._id}[/white]",
                justify="left", no_wrap=True)
            line = ""
            # Loop through the elements of the stage tuple
            for k, v in asdict(self.pipeline[i]).items():
                if k == '_num' or k == '_id' or k == '_method_call' or \
                    k == "_parameters" \
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

    def _process_config(self, config: dict, caller_module) -> dict:
        """
        Process the YAML configuration and convert it into a list of pipeline steps.

        Parameters
        ----------
        config: dict
            Dictionary containing the YAML configuration.

        Returns
        -------
        steps: list
            List of pipeline steps.
        """
        steps = []

        if self.verbose:
            print(f"> caller_module: {caller_module}")
        module = importlib.import_module(caller_module)

        for nr, (step_id, step_contents) in enumerate(config.items()):
            stage = Stage()
            stage._num = nr
            stage._id = step_id
            for k, v in step_contents.items():
                if k == 'attribute':
                    stage.attribute_name = v
                elif k == 'method':
                    stage.method_name = v
                elif k == 'class':
                    try:
                        stage.class_name = getattr(module, v)
                    except AttributeError as exc:
                        raise AttributeError(
                            f"Class '{v}' not found in module '{module}'") from exc
                elif k == 'arguments':
                    stage.arguments = v
                else:
                    raise ValueError(
                        f"Key '{k}' not recognized in the configuration")
            steps.append(stage)

        if self.verbose:
            print(f"> Processed {len(steps)} steps")
        return steps

    def _pbar_create(self):
        """
            Creates a progress bar using the tqdm library.

            The progress bar is used to track the progress of the pipeline execution.

            Args:
                None

            Returns:
                None
        """
        if len(self.pipeline) == 0:
            self._pbar = None
            return

        self._pbar = tqdm(total=len(self.pipeline), **self.prog_bar_params)
        self._pbar.update(0)
        print("-"*100) if self.verbose else None

    def _pbar_update(self, step=1):
        """
        Update the progress bar by the specified step.

        Parameters:
        - step (int): The step size to update the progress bar. Default is 1.
        """
        self._pbar.update(step)
        self._pbar.refresh()

    def _pbar_close(self):
        """
        Close the progress bar.
        """
        self._pbar.close()
        self._pbar = None
        print("-"*100) if self.verbose else None
