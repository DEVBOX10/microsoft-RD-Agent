import json

from rdagent.components.coder.CoSTEER import CoSTEER
from rdagent.components.coder.CoSTEER.config import CoSTEER_SETTINGS
from rdagent.components.coder.CoSTEER.evaluators import CoSTEERMultiEvaluator
from rdagent.components.coder.CoSTEER.evolving_strategy import (
    MultiProcessEvolvingStrategy,
)
from rdagent.components.coder.CoSTEER.knowledge_management import (
    CoSTEERQueriedKnowledge,
)
from rdagent.components.coder.data_science.workflow.eval import (
    WorkflowGeneralCaseSpecEvaluator,
)
from rdagent.components.coder.data_science.workflow.exp import WorkflowTask
from rdagent.core.experiment import FBWorkspace
from rdagent.core.scenario import Scenario
from rdagent.oai.llm_utils import APIBackend
from rdagent.utils.agent.tpl import T


class WorkflowMultiProcessEvolvingStrategy(MultiProcessEvolvingStrategy):
    def implement_one_task(
        self,
        target_task: WorkflowTask,
        queried_knowledge: CoSTEERQueriedKnowledge | None = None,
        workspace: FBWorkspace | None = None,
    ) -> dict[str, str]:
        # competition_info = self.scen.competition_descriptions
        workflow_information_str = target_task.get_task_information()

        # 1. query
        queried_similar_successful_knowledge = (
            queried_knowledge.task_to_similar_task_successful_knowledge[workflow_information_str]
            if queried_knowledge is not None
            else []
        )
        queried_former_failed_knowledge = (
            queried_knowledge.task_to_former_failed_traces[workflow_information_str]
            if queried_knowledge is not None
            else []
        )

        # 2. code
        system_prompt = T(".prompts:workflow_coder.system").r(
            task_desc=workflow_information_str,
            competition_info=self.scen.get_competition_full_desc(),
            queried_similar_successful_knowledge=queried_similar_successful_knowledge,
            queried_former_failed_knowledge=queried_former_failed_knowledge[0],
        )
        user_prompt = T(".prompts:workflow_coder.user").r(
            load_data_code=workspace.file_dict["load_data.py"],
            feature_code=workspace.file_dict["feature.py"],
            model_codes=workspace.get_codes(r"^model_(?!test)\w+\.py$"),
            ensemble_code=workspace.file_dict["ensemble.py"],
            latest_code=workspace.file_dict.get("main.py"),
            workflow_spec=workspace.file_dict["spec/workflow.md"],
        )
        workflow_code = json.loads(
            APIBackend().build_messages_and_create_chat_completion(
                user_prompt=user_prompt, system_prompt=system_prompt, json_mode=True
            )
        )["code"]

        return {"main.py": workflow_code}

    def assign_code_list_to_evo(self, code_list: list[dict[str, str]], evo):
        """
        Assign the code list to the evolving item.

        The code list is aligned with the evolving item's sub-tasks.
        If a task is not implemented, put a None in the list.
        """
        for index in range(len(evo.sub_tasks)):
            if code_list[index] is None:
                continue
            if evo.sub_workspace_list[index] is None:
                # evo.sub_workspace_list[index] = FBWorkspace(target_task=evo.sub_tasks[index])
                evo.sub_workspace_list[index] = evo.experiment_workspace
            evo.sub_workspace_list[index].inject_files(**code_list[index])
        return evo


class WorkflowCoSTEER(CoSTEER):
    def __init__(
        self,
        scen: Scenario,
        *args,
        **kwargs,
    ) -> None:
        eva = CoSTEERMultiEvaluator(
            WorkflowGeneralCaseSpecEvaluator(scen=scen), scen=scen
        )  # Please specify whether you agree running your eva in parallel or not
        es = WorkflowMultiProcessEvolvingStrategy(scen=scen, settings=CoSTEER_SETTINGS)
        super().__init__(*args, settings=CoSTEER_SETTINGS, eva=eva, es=es, evolving_version=2, scen=scen, **kwargs)
