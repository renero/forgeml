Usage
=====

Installation
------------

To use ForgeML, first install it using pip:

.. code-block:: console

   (.venv) $ pip install forgeml

Basic Usage
-----------

The general assumption is that this module will help you out in executing a pipeline 
of tasks. The tasks are defined in a configuration file, or within your code, and 
the pipeline will execute them in the order they are defined, as follows:

.. code-block:: python

   from forgeml import Pipeline

   pipeline = Pipeline().from_config('path/to/config.yml')
   pipeline.run()

The configuration file is a YAML file that defines the tasks to be executed.

Alternatively, you can define the tasks in your code and execute them as follows:

.. code-block:: python

   from forgeml import Pipeline, Task

   task1 = Task(
       return_variable='result',
       method='my_module.my_function', 
       args={'arg1': 'value1'})
    task2 = Task(
       return_variable='result2',
       method='my_module.my_function2', 
       args={'arg1': 'result'})
    
    pipeline = Pipeline().add_tasks([task1, task2])
    pipeline.run()