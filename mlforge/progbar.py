# This is the general idea, but with a generic nesteable class
from dataclasses import dataclass
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)
from time import sleep


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(
                Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

    def clear(cls):
        cls._instances = {}


@dataclass
class Entry:
    id: int
    name: str
    steps: int
    progress: float


class ProgBar(metaclass=Singleton):
    stack = []
    progress = None

    def __init__(
            self,
            name: str = None,
            num_steps: int = None,
            max_descr_len: int = 30,
            verbose: bool = False):
        self.verbose = verbose
        self.max_descr_len = max_descr_len

        pb_name = name if name else "Progress"
        pb_name = pb_name[:max_descr_len] + \
            '.' if len(pb_name) > max_descr_len else pb_name
        if len(pb_name) < max_descr_len:
            pb_name = pb_name + "." * (max_descr_len - len(pb_name))

        description = "[progress.description]{{task.description:<{}s}}".format(
            self.max_descr_len)
        self.progress = Progress(
            TextColumn(description),
            TextColumn("•"),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            BarColumn(),
            MofNCompleteColumn(),
            TextColumn("•"),
            TimeElapsedColumn(),
            TextColumn("•"),
            TimeRemainingColumn(),
            transient=True)
        self.start_subtask(name, num_steps)
        self.main_task = self.stack[0].id

    def start_subtask(self, name: str = None, steps: int = None):
        assert steps is not None, "The total number of steps must be provided"
        if name is None:
            name = f"subtask_{len(self.stack)}"
        id = self.progress.add_task(name, total=steps)
        self.stack.append(Entry(id, name, steps, 0.0))
        self.progress.update(id, completed=0)

        self._m(f"STARTING '{name}' with {steps} steps")

        if not self.verbose:
            self.progress.start()

        return self

    def update_subtask(self, name, steps):
        idx = self._get_idx(name)
        assert idx != - 1,\
            f"Element '{name}' NOT found. Available pbars are: {[n.name for n in self.stack]}"

        stack_element = self._get_element_by_name(name)
        self.progress.update(stack_element.id, completed=steps, refresh=True)
        change_in_pbar = (steps - stack_element.progress) != 0.0
        upper_steps = self._upper_steps(name)

        # Guess if this is last element in the stack, by checking if the
        # name corresponds to the last element in the stack
        last_pbar_in_stack = name == self.stack[-1].name

        stack_element.progress = steps
        self._log_update(name, steps, idx, change_in_pbar, upper_steps)

        if upper_steps is None or not last_pbar_in_stack:
            self._m(f"   (leaving update)\n")
            self._reset_if_completed(idx)
            return

        multiplier = (1 / stack_element.steps)
        for i, n_steps in enumerate(upper_steps):
            upper_task_id = self.stack[idx - (i + 1)].id
            upper_stack_element = self._get_element(upper_task_id)
            percentage = (multiplier * (1 / n_steps)) * upper_stack_element.steps
            self.progress.update(
                upper_task_id, advance=percentage, refresh=True)
            upper_stack_element.progress += percentage
            multiplier = multiplier * (1 / n_steps)

            self._log_advance(upper_task_id, percentage)

        self._reset_if_completed(idx)

    def remove(self, name: str):
        idx = self._get_idx(name)
        if idx == -1:
            self._m(f"Element '{name}' NOT found")
            return
        if len(self.stack) > 1 and idx == 0:
            self._m("Cannot remove first element when len > 1")
            return

        stack_element = self._get_element_by_name(name)
        self.progress.remove_task(stack_element.id)
        del self.stack[idx]

        if len(self.stack) == 0:
            self.progress.stop()
            self.progress = None

        self._m(f"Element '{name}' REMOVED")
        self._m(f"  Stack contains {len(self.stack)} elements")
        return

    def _upper_steps(self, name: str):
        idx = self._get_idx(name)
        if idx == 0:
            self._m(f"Element '{name}' is the TOP one")
            return None
        if idx == -1:
            self._m(f"Element '{name}' NOT found")
            return None
        upper_bars_steps = [
            self.stack[i].steps for i in range(idx - 1, -1, -1)]
        return upper_bars_steps

    def _get_idx(self, name):
        idx = next(
            (i for i, element in enumerate(self.stack) if element.name == name), -1
        )
        return idx

    def _get_element(self, id):
        return next(
            (element for element in self.stack if element.id == id), None
        )

    def _get_element_by_name(self, name):
        return next(
            (element for element in self.stack if element.name == name), None
        )

    def _log_advance(self, upper_task_id, percentage):
        stck_element = self._get_element(upper_task_id)
        self._m(
            f"-> Advancing '{stck_element.name}' by {percentage:.4f}"
            f" steps  (progress: {stck_element.progress:.4f} / "
            f"{stck_element.steps})", end="")
        if stck_element.progress > stck_element.steps:
            self._m(" - ERROR")
        else:
            self._m("")

    def _log_update(self, name, steps, idx, change_in_pbar, upper_steps):
        stack_element = self._get_element_by_name(name)
        self._m(
            f"Updating '{name}' (id={stack_element.id}) with {steps} steps"
            f" (progress: {stack_element.progress:.4f}) / {stack_element.steps}"
            f" [delta:{change_in_pbar}({(steps - stack_element.progress):E}); "
            f" upper_steps:{upper_steps}]",
            end="")
        if stack_element.progress > stack_element.steps:
            self._m(" - ERROR")
        else:
            self._m("")

    def _reset_if_completed(self, idx):
        stack_element = self._get_element(idx)
        if stack_element is None:
            return

        if (idx > 0) and (idx < len(self.stack) - 1) and \
                stack_element.progress >= stack_element.steps:
            self._m("\nUPON CONDITION")
            self.progress.update(stack_element.id, completed=0, refresh=True)
            stack_element.progress = 0.

    def _m(self, str="", **kwargs):
        if not self.verbose:
            return
        print(str, **kwargs)


def main():
    steps = [2, 3, 3]
    pbar = ProgBar("main", steps[0], verbose=False)
    for i, n_steps in enumerate(steps[1:]):
        ProgBar().start_subtask(f"pbar_{i+1}", n_steps)

    for i in range(steps[0]):
        for j in range(steps[1]):
            for k in range(steps[2]):
                sleep(1)
                pbar.update_subtask(f"pbar_2", k + 1)
            pbar._m()
            pbar.update_subtask(f"pbar_1", j + 1)
        pbar._m()
        pbar.update_subtask(f"main", i + 1)

    for i in range(len(steps) - 1, 0, -1):
        pbar.remove(f"pbar_{i}")
    pbar.remove("main")


if __name__ == "__main__":
    main()
