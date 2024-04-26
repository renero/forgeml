MLForge
=======

**MLForge** is a simple package to write simple pipelines of calls (to
methods, classes, …). You can access the documentation at
`ReadTheDocs <https://mlforge.readthedocs.io/en/latest/>`__

It surges from the need to execute several things in a row, and to be
able to easily add or remove steps in the pipeline.

This is a Work in Progress.

Installation
------------

To use MLForge, first install it using pip:

.. code:: bash

   (.venv) $ pip install mlforge

Basic Usage
-----------

The general assumption is that this module will help you out in
executing a pipeline of tasks. The tasks are defined in a configuration
file, or within your code, and it will execute them in the order they
are defined.

A Pipeline is normally created with a host object, which is an object
that contains some of the methods that will be called in the pipeline,
but primarily, it is used to store the results of the methods that are
called. If you don’t provide a host object, the pipeline will store the
results in an internal dictionary, from where you can retrieve them with
``get_attribute``.

.. code:: python

   from mlforge import Pipeline

   my_stages= [
       ('method1'),
       ('method2', {'param1': 'value2'}),
       ('method3', ClassName, {param1: 'value1'}),
       ('new_attribute', 'method4', ClassName, {'param1': 'value1'}),
   ]
   pipeline = Pipeline().from_list(my_stages)
   pipeline.run()

This pipeline will execute the following tasks:

1. Call the method ``method1``, which will be located in the host object
   or in globals.
2. Call the method ``method2`` which will be located in the host object
   or in globals, passing the parameter ``param1`` with the value
   ``value2``.
3. Call the method ``method3`` of the class ``ClassName``, passing the
   parameter ``param1`` with the value ``value1``.
4. Call the method ``method4`` of the class ``ClassName``, passing the
   parameter ``param1`` with the value ``value1``, and store the result
   in a new attribute ``new_attribute``. To access the attribute you can
   use the method ``pipeline.get_attribute('new_attribute')``.

If you prefer to specify the stages in a separate YAML configuration
file, you then can use MLForge as follows:

.. code:: python

   from mlforge import Pipeline

   pipeline = Pipeline().from_config('path/to/config.yaml')
   pipeline.run()

The configuration file is a YAML file that defines the tasks to be
executed. The following is an example of YAML configuration file:

.. code:: yaml

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

For each stage of the pipeline (specified in order), you can define the
method to be executed, the class that contains the method, the arguments
to be passed to the method, and the attribute to store the result of the
method. Method arguments can be specified as key-value pairs in the
``arguments`` section.

Alternatively, you can define the tasks in your code and execute them as
follows:

.. code:: python

   from mlforge import Pipeline, Stage

   stage1 = Stage(
       attribute_name='result',
       method_name='my_module.my_function',
       arguments={'arg1': 'value1'})
   stage2 = Stage(
       attribute_name='result2',
       method_name='my_module.my_function2',
       arguments={'arg1': 'result'})

   pipeline = Pipeline().add_stages([stage1, stage2])
   pipeline.run()

Syntax for the stages of the pipeline
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In your code, define a list with the stages to be added to the pipeline.
Each of the stages can be specified as any of the following options:

Simply call a method of the host object:

.. code:: python

   'method_name',

Same, but put everything in a tuple

.. code:: python

   ('method_name'),

Call the constructor of a class

.. code:: python

   (ClassHolder),

Call a method of a class

.. code:: python

   ('method_name', ClassHolder),

Call a method of the host object, and keep the result in a new attribute

.. code:: python

   ('new_attribute', 'method_name'),

Call the constructor of a class, and keep the result in a new attribute

.. code:: python

   ('new_attribute', ClassHolder),

Call a method of the host object, with specific parameters, and keep the
result in a new attribute

.. code:: python

   ('new_attribute', 'method_name', {'param1': 'value1', 'param2': 'value2'}),

Call a class method, and get the result in a new attribute

.. code:: python

   ('new_attribute', 'method_name', ClassHolder),

Call a method of the host object, with specific parameters

.. code:: python

   ('method_name', {'param1': 'value1', 'param2': 'value2'}),

Call a method of a specific class, with specific parameters.

.. code:: python

   ('method_name', ClassHolder, {'param1': 'value1'}),

Call a method of a specific class, with specific parameters, and keep
the result in a new attribute

.. code:: python

   ('new_attribute', 'method_name', ClassHolder, {'param1': 'value1'}),

To do
-----

-  Add a way to add a step at a specific position
-  Add a way to remove a step
-  Add a way to replace a step
-  Add a way to add a step before or after another step
-  And many other things…
