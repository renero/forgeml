Usage
=====

Installation
------------

To use MLForge, first install it using pip:

.. code-block:: console

   (.venv) $ pip install mlforge

Basic Usage
-----------

The general assumption is that this module will help you out in executing a pipeline
of tasks. The tasks are defined in a configuration file, or within your code, and
the pipeline will execute them in the order they are defined, as follows:

.. code-block:: python

   from mlforge import Pipeline

   pipeline = Pipeline().from_config('path/to/config.yml')
   pipeline.run()

The configuration file is a YAML file that defines the tasks to be executed. The
following is an example of YAML configuration file:

.. code-block:: yaml

   step1:
       method: method
       class: SampleClass
   step2:
       attribute: object
       class: SampleClass
   step3:
     attribute: result1
     method: method
     class: SampleClass
     arguments:
       param2: there!

For each stage of the pipeline (specified in order), you can define the method to be
executed, the class that contains the method, the arguments to be passed to the method,
and the attribute to store the result of the method. Method arguments can be specified
as key-value pairs in the `arguments` section.

Alternatively, you can define the tasks in your code and execute them as follows:

.. code-block:: python

   from mlforge import Pipeline, Stage

   stage1 = Stage(
       return_variable='result',
       method='my_module.my_function',
       args={'arg1': 'value1'})
    stage2 = Stage(
       return_variable='result2',
       method='my_module.my_function2',
       args={'arg1': 'result'})

    pipeline = Pipeline().add_stages([stage1, stage2])
    pipeline.run()


Syntax for the stages of the pipeline
--------------------------------------

Syntax:
    Simply call a method of the host object

    .. code-block:: python

        'method_name',

    Same, but put everything in a tuple

    .. code-block:: python

        ('method_name'),

    Call the constructor of a class

    .. code-block:: python

        (ClassHolder),

    Call a method of a class

    .. code-block:: python

        ('method_name', ClassHolder),

    Call a method of the host object, and keep the result in a new attribute

    .. code-block:: python

        ('new_attribute', 'method_name'),

    Call the constructor of a class, and keep the result in a new attribute

    .. code-block:: python

        ('new_attribute', ClassHolder),

    Call a method of the host object, with specific parameters, and keep the
    result in a new attribute

    .. code-block:: python

        ('new_attribute', 'method_name', {'param1': 'value1', 'param2': 'value2'}),

    Call a method of the host object, with specific parameters

    .. code-block:: python

        ('method_name', {'param1': 'value1', 'param2': 'value2'}),

    Call a method of a specific class, with specific parameters.

    .. code-block:: python

        ('method_name', ClassHolder, {'param1': 'value1'}),

    Call a method of a specific class, with specific parameters, and keep the
    result in a new attribute

    .. code-block:: python

        ('new_attribute', 'method_name', ClassHolder, {'param1': 'value1'}),

