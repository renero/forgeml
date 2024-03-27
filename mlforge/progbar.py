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


class ProgBar:
    """
    Implements a progress bar for the mlforge package.
    """

    def __init__(self, name: str = None, num_steps: int = None):
        assert num_steps is not None, "Number of steps must be provided."
        assert num_steps > 0, "Number of steps must be greater than 0."

        self.num_steps = num_steps
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
        self.sub_task = self.progress.add_task('subtask', start=False)
