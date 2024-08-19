from copy import deepcopy
from pathlib import Path

from rdagent.components.coder.factor_coder.factor import (
    FactorExperiment,
    FactorFBWorkspace,
    FactorTask,
)
from rdagent.core.prompts import Prompts
from rdagent.core.scenario import Scenario
from rdagent.scenarios.data_processing.experiment.workspace import DPFBWorkspace

prompt_dict = Prompts(file_path=Path(__file__).parent / "prompts.yaml")


class DPFeatureExperiment(FactorExperiment[FactorTask, DPFBWorkspace, FactorFBWorkspace]):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.experiment_workspace = DPFBWorkspace(template_folder_path=Path(__file__).parent / "feature_template")


class DPFeatureScenario(Scenario):
    def __init__(self) -> None:
        super().__init__()
        self._background = deepcopy(prompt_dict["data_processing_background"])
        self._output_format = deepcopy(prompt_dict["data_processing_output_format"])
        self._interface = deepcopy(prompt_dict["data_processing_interface"])
        self._simulator = deepcopy(prompt_dict["data_processing_simulator"])
        self._rich_style_description = deepcopy(prompt_dict["data_factor_rich_style_description"])
        self._experiment_setting = deepcopy(prompt_dict["data_factor_experiment_setting"])

    @property
    def background(self) -> str:
        return self._background

    # @property
    # def source_data(self) -> str:
    #     return self._source_data

    @property
    def output_format(self) -> str:
        return self._output_format

    @property
    def interface(self) -> str:
        return self._interface

    @property
    def simulator(self) -> str:
        return self._simulator

    @property
    def rich_style_description(self) -> str:
        return self._rich_style_description

    @property
    def experiment_setting(self) -> str:
        return self._experiment_setting

    def get_scenario_all_desc(self) -> str:
        return f"""Background of the scenario:
{self.background}
The interface you should follow to write the runnable code:
{self.interface}
The output of your code should be in the format:
{self.output_format}
The simulator user can use to test your factor:
{self.simulator}
"""


# The source data you can use:
# {self.source_data}