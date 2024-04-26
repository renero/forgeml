"""
    Implements a progress bar for the mlforge package.
"""

from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)


class Singleton(type):
    """
    A metaclass that allows a class to have only one instance.

    This metaclass ensures that only one instance of a class is created and
    provides a global point of access to that instance.

    Usage:
        class MyClass(metaclass=Singleton):
            # class definition

    Note:
        This metaclass should be used as a metaclass for the class that you want
        to make a singleton.
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(
                Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class ProgBar(metaclass=Singleton):
    """
    Implements a progress bar for the mlforge package.
    """

    def __init__(self, name: str = None, num_steps: int = None, subtask: bool = False):
        self.num_steps = num_steps
        self.sub_task = subtask
        self.progress = Progress(
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            BarColumn(),
            MofNCompleteColumn(),
            TextColumn("•"),
            TimeElapsedColumn(),
            TextColumn("•"),
            TimeRemainingColumn(),
        )
        pb_name = name if name else "Progress..."
        self.main_task = self.progress.add_task(pb_name, total=num_steps)
        if self.sub_task:
            self.sub_task = self.progress.add_task('subtask', start=False)

    def start_subtask(self, num_steps: int):
        """
        Starts a subtask with the specified number of steps.

        Args:
            num_steps (int): The total number of steps in the subtask.

        Returns:
            None
        """
        self.progress.reset(self.sub_task, total=num_steps)
        self.progress.start_task(self.sub_task)
        return self

    def update_subtask(self, advance: int = 1):
        """
        Updates the progress of the subtask.

        Parameters:
        - advance (int): The amount by which to advance the progress. Default is 1.
        """
        self.progress.update(self.sub_task, advance=advance)
