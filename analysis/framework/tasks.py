# -*- coding: utf-8 -*-

"""
Base task classes that are used across the analysis.
"""

__all__ = ["AnalysisTask", "ConfigTask", "ShiftTask", "DatasetTask"]


import os

import luigi
import law
import order as od


class AnalysisTask(law.SandboxTask):

    version = luigi.Parameter(description="task version, required")

    analysis = "singletop"

    exclude_db = True

    @classmethod
    def get_task_namespace(cls):
        return cls.analysis

    def __init__(self, *args, **kwargs):
        super(AnalysisTask, self).__init__(*args, **kwargs)

        # store the analysis instance
        self.analysis_inst = od.Analysis.get_instance(self.analysis)

        # other attributes
        self.local_root = os.environ["ANALYSIS_LOCAL_STORE"]

    @property
    def store_parts(self):
        return (self.analysis, self.__class__.__name__)

    @property
    def store_parts_opt(self):
        parts = tuple()
        if self.version != law.parameter.NO_STR:
            parts += (self.version,)
        return parts

    @property
    def local_store(self):
        parts = (self.local_root,) + self.store_parts + self.store_parts_opt
        return os.path.join(*parts)

    def local_path(self, *parts):
        return os.path.join(self.local_store, *[str(part) for part in parts])

    def local_target(self, *parts):
        return law.LocalFileTarget(self.local_path(*parts))

    @property
    def remote_store(self):
        parts = ("law_analysis",) + self.store_parts + self.store_parts_opt
        return os.path.join(*parts)

    def remote_path(self, *parts):
        return os.path.join(self.remote_store, *[str(part) for part in parts])

    @property
    def default_log_file(self):
        # return self.local_path("log.txt")
        return "-"


class ConfigTask(AnalysisTask):

    config = "singletop_opendata_2011"

    exclude_db = True

    def __init__(self, *args, **kwargs):
        super(ConfigTask, self).__init__(*args, **kwargs)

        # store the campaign and config instances
        self.config_inst = self.analysis_inst.get_config(self.config)
        self.campaign_inst = self.config_inst.campaign

    @property
    def store_parts(self):
        return super(ConfigTask, self).store_parts + (self.config,)


class ShiftTask(ConfigTask):

    shift = luigi.Parameter(default="nominal", significant=False, description="systematic shift to "
        "apply, default: nominal")
    effective_shift = luigi.Parameter(default="nominal")

    shifts = set()

    exclude_db = True
    exclude_params_db = {"effective_shift"}
    exclude_params_req = {"effective_shift"}
    exclude_params_sandbox = {"effective_shift"}

    @classmethod
    def modify_param_values(cls, params):
        if params["shift"] == "nominal":
            return params

        # shift known to config?
        config_inst = od.Config(cls.config)
        if params["shift"] not in config_inst.shifts:
            raise Exception("shift {} unknown to config {}".format(params["shift"], config_inst))

        # check if the shift is known to the task
        if params["shift"] in cls.shifts:
            params["effective_shift"] = params["shift"]

        return params

    def __init__(self, *args, **kwargs):
        super(ShiftTask, self).__init__(*args, **kwargs)

        # store the shift instance
        self.shift_inst = self.config_inst.get_shift(self.effective_shift)

    @property
    def store_parts(self):
        return super(ShiftTask, self).store_parts + (self.effective_shift,)


class DatasetTask(ShiftTask):

    dataset = luigi.Parameter(default="singleTop", description="the dataset name, default: "
        "singleTop")

    exclude_db = True

    @classmethod
    def modify_param_values(cls, params):
        if params["shift"] == "nominal":
            return params

        # shift known to config?
        config_inst = od.Config.get_instance(cls.config)
        if params["shift"] not in config_inst.shifts:
            raise Exception("shift {} unknown to config {}".format(params["shift"], config_inst))

        # check if the shift is known to the task or dataset
        dataset_inst = od.Dataset.get_instance(params["dataset"])
        if params["shift"] in cls.shifts or params["shift"] in dataset_inst.info:
            params["effective_shift"] = params["shift"]

        return params

    def __init__(self, *args, **kwargs):
        super(DatasetTask, self).__init__(*args, **kwargs)

        # store the dataset instance and the dataset info instance that corresponds to the shift
        self.dataset_inst = self.config_inst.get_dataset(self.dataset)
        self.dataset_info_inst = self.dataset_inst.get_info(
            self.shift_inst.name if self.shift_inst.name in self.dataset_inst.info else "nominal")

        # also, when there is only one linked process in the current dataset, store it
        if len(self.dataset_inst.processes) == 1:
            self.process_inst = list(self.dataset_inst.processes.values())[0]
        else:
            self.process_inst = None

    @property
    def store_parts(self):
        parts = super(DatasetTask, self).store_parts
        # insert the dataset name right before the shift
        parts = parts[:-1] + (self.dataset, parts[-1])
        return parts

    def create_branch_map(self):
        return {i: i for i in range(self.dataset_info_inst.n_files)}
