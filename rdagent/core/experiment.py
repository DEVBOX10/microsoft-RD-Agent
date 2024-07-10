from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Generic, Optional, Sequence, TypeVar

"""
This file contains the all the class about organizing the task in RD-Agent.
"""


class Task:
    # TODO: 把name放在这里作为主键
    # Please refer to rdagent/model_implementation/task.py for the implementation
    # I think the task version applies to the base class.
    pass


ASpecificTask = TypeVar("ASpecificTask", bound=Task)


class Implementation(ABC, Generic[ASpecificTask]):
    def __init__(self, target_task: ASpecificTask) -> None:
        self.target_task = target_task

    @abstractmethod
    def execute(self, *args, **kwargs) -> object:
        raise NotImplementedError("execute method is not implemented.")


ASpecificImp = TypeVar("ASpecificImp", bound=Implementation)


class ImpLoader(ABC, Generic[ASpecificTask, ASpecificImp]):
    @abstractmethod
    def load(self, task: ASpecificTask) -> ASpecificImp:
        raise NotImplementedError("load method is not implemented.")


class FBImplementation(Implementation):
    """
    File-based task implementation

    The implemented task will be a folder which contains related elements.
    - Data
    - Code Implementation
    - Output
        - After execution, it will generate the final output as file.

    A typical way to run the pipeline of FBImplementation will be
    (We didn't add it as a method due to that we may pass arguments into `prepare` or `execute` based on our requirements.)

    .. code-block:: python

        def run_pipeline(self, **files: str):
            self.prepare()
            self.inject_code(**files)
            self.execute()

    """

    # TODO:
    # FileBasedFactorImplementation should inherit from it.
    # Why not directly reuse FileBasedFactorImplementation.
    #   Because it has too much concrete dependencies.
    #   e.g.  dataframe, factors
    def __init__(self, *args, code_dict: Dict[str, str] = None, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.code_dict = code_dict  # The code to be injected into the folder, store them in the variable
        self.workspace_path: Optional[Path] = None

    @property
    def code(self) -> str:
        code_string = ""
        for file_name, code in self.code_dict.items():
            code_string += f"File: {file_name}\n{code}\n"
        return code_string

    @abstractmethod
    def prepare(self, *args, **kwargs):
        """
        Prepare all the files except the injected code
        - Data
        - Documentation
        - TODO: env?  Env is implicitly defined by the document?

            typical usage of `*args, **kwargs`:
                Different methods shares the same data. The data are passed by the arguments.
        """

    def inject_code(self, **files: str):
        """
        Inject the code into the folder.
        {
            "model.py": "<model code>"
        }
        """
        self.code_dict = files
        for k, v in files.items():
            with open(self.workspace_path / k, "w") as f:
                f.write(v)

    def get_files(self) -> list[Path]:
        """
        Get the environment description.

        To be general, we only return a list of filenames.
        How to summarize the environment is the responsibility of the TaskGenerator.
        """
        return list(self.workspace_path.iterdir())


class Experiment(ABC, Generic[ASpecificTask, ASpecificImp]):
    """
    The experiment is a sequence of tasks and the implementations of the tasks after generated by the TaskGenerator.
    """

    def __init__(self, sub_tasks: Sequence[ASpecificTask]) -> None:
        self.sub_tasks = sub_tasks
        self.sub_implementations: Sequence[ASpecificImp] = [None for _ in self.sub_tasks]
        self.based_experiments: Sequence[Experiment] = []
        self.result: object = None  # The result of the experiment, can be different types in different scenarios.


TaskOrExperiment = TypeVar("TaskOrExperiment", Task, Experiment)


class Loader(ABC, Generic[TaskOrExperiment]):
    @abstractmethod
    def load(self, *args, **kwargs) -> TaskOrExperiment:
        raise NotImplementedError("load method is not implemented.")
