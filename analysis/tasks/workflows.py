# -*- coding: utf-8 -*-

"""
Task chain using workflows that fetches public data, converts them to structured numpy arrays,
splits them to achieve a map-reduce-like workflow, applies a simple selection and event
reconstruction, "reduces" them again into a single file per dataset, and outputs some simple
histograms.

Each chunk of a public data file is treated as a branch of a workflow allowing for higher
concurrency during task processing. For a more simple, straight-forward task chain, see simple.py.
"""


from collections import OrderedDict

import law
law.contrib.load("numpy", "root", "docker")
import six

from analysis.framework.tasks import ConfigTask, DatasetTask
from analysis.framework.selection import select_singletop as select
from analysis.framework.reconstruction import reconstruct_singletop as reconstruct
from analysis.framework.systematics import vary_jer
from analysis.framework.plotting import stack_plot
from analysis.framework.util import join_struct_arrays, partial_slices
import analysis.setup.singletop


class FetchData(DatasetTask):

    def output(self):
        return self.local_target("data.root")

    @law.decorator.log
    def run(self):
        with self.output().localize("w") as tmp:
            # fetch the input file
            src = self.dataset_info_inst.keys[0]
            six.moves.urllib.request.urlretrieve(src, tmp.path)


class ConvertData(DatasetTask):

    sandbox = "docker::riga/law_example_singletop"
    force_sandbox = True

    def requires(self):
        return FetchData.req(self)

    def output(self):
        return self.local_target("data.npz")

    @law.decorator.log
    def run(self):
        # load via the root_numpy formatter which converts root trees into numpy arrays
        events = self.input().load(formatter="root_numpy")

        with self.output().localize("w") as tmp:
            tmp.dump(events=events)

        self.publish_message("converted {} events".format(len(events)))


class MapData(DatasetTask, law.LocalWorkflow):

    sandbox = "docker::riga/law_example_singletop"
    force_sandbox = True

    def workflow_requires(self):
        reqs = super(MapData, self).workflow_requires()
        reqs["data"] = self.requires_from_branch()
        return reqs

    def requires(self):
        return ConvertData.req(self)

    def output(self):
        return self.local_target("data_{}.npz".format(self.branch))

    @law.decorator.log
    def run(self):
        events = self.input().load(allow_pickle=True)["events"]

        # "map" events into chunks, use the numer of files stored in the dataset instance
        slices = partial_slices(events.shape[0], self.dataset_info_inst.n_files)
        start, end = slices[self.branch]
        chunk = events[start:end]

        with self.output().localize("w") as tmp:
            tmp.dump(events=chunk)


class VaryJER(DatasetTask, law.LocalWorkflow):

    shifts = {"jer_up", "jer_down"}

    sandbox = "docker::riga/law_example_singletop"
    force_sandbox = True

    def workflow_requires(self):
        reqs = super(VaryJER, self).workflow_requires()
        reqs["data"] = self.requires_from_branch()
        return reqs

    def requires(self):
        return MapData.req(self)

    def output(self):
        return self.local_target("data_{}.npz".format(self.branch))

    @law.decorator.log
    def run(self):
        events = self.input().load(allow_pickle=True)["events"]

        # vary jer in all events
        vary_jer(events, self.shift_inst.direction)

        with self.output().localize("w") as tmp:
            tmp.dump(events=events)


class SelectAndReconstruct(DatasetTask, law.LocalWorkflow):

    shifts = VaryJER.shifts

    sandbox = "docker::riga/law_example_singletop"
    force_sandbox = True

    def workflow_requires(self):
        reqs = super(SelectAndReconstruct, self).workflow_requires()
        reqs["data"] = self.requires_from_branch()
        return reqs

    def requires(self):
        return (MapData if self.shift_inst.is_nominal else VaryJER).req(self)

    def output(self):
        return self.local_target("data_{}.npz".format(self.branch))

    @law.decorator.log
    def run(self):
        events = self.input().load(allow_pickle=True)["events"]

        # selection
        indexes, selected_objects = select(events)
        self.publish_message("selected {} of {} events".format(len(indexes), len(events)))
        events = events[indexes]

        # reconstruction
        reco_data = reconstruct(events, selected_objects)
        self.publish_message("reconstructed {} variables".format(len(reco_data.dtype.names)))
        events = join_struct_arrays(events, reco_data)

        with self.output().localize("w") as tmp:
            tmp.dump(events=events)


class ReduceData(DatasetTask):

    shifts = VaryJER.shifts

    sandbox = "docker::riga/law_example_singletop"
    force_sandbox = True

    def requires(self):
        return SelectAndReconstruct.req(self)

    def output(self):
        return self.local_target("data.npz")

    @law.decorator.log
    def run(self):
        import numpy as np

        # load input arrays per dataset and "reduce" them by concatenating
        events = None
        for inp in self.input()["collection"].targets.values():
            chunk = inp.load(allow_pickle=True)["events"]
            events = np.concatenate([events, chunk]) if events is not None else chunk

        with self.output().localize("w") as tmp:
            tmp.dump(events=events)


class CreateHistograms(ConfigTask):

    shifts = VaryJER.shifts

    sandbox = "docker::riga/law_example_singletop"
    force_sandbox = True

    def requires(self):
        reqs = OrderedDict()
        for dataset in self.config_inst.datasets:
            reqs[dataset] = ReduceData.req(self, dataset=dataset.name)
        return reqs

    def output(self):
        return law.LocalFileTarget(self.local_path("hists.tgz"))

    @law.decorator.log
    def run(self):
        # load input arrays per dataset, map them to the first linked process
        events = OrderedDict()
        for dataset, inp in self.input().items():
            process = list(dataset.processes.values())[0]
            events[process] = inp.load(allow_pickle=True)["events"]
            self.publish_message("loaded events for dataset {}".format(dataset.name))

        tmp_dir = law.LocalDirectoryTarget(is_tmp=True)
        tmp_dir.touch()

        for variable in self.config_inst.variables:
            stack_plot(events, variable, tmp_dir.child(variable.name + ".pdf", "f").path)
            self.publish_message("written histogram for variable {}".format(variable.name))

        with self.output().localize("w") as tmp:
            tmp.dump(tmp_dir)
