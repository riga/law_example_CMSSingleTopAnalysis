# -*- coding: utf-8 -*-

"""
Simple task chain that fetches public data, converts them to structured numpy arrays, applies
a simple selection and event reconstruction, and outputs some simple histograms.

Each public data file is treated en bloc by the tasks in this file. For a map-reduce-like task
chain, see branched.py.
"""


from collections import OrderedDict

import law
law.contrib.load("numpy", "root")

import six

from analysis.framework.tasks import ConfigTask, DatasetTask
from analysis.framework.selection import select_singletop as select
from analysis.framework.reconstruction import reconstruct_singletop as reconstruct
from analysis.framework.systematics import vary_jer
from analysis.framework.plotting import stack_plot
from analysis.framework.util import join_struct_arrays
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


class VaryJER(DatasetTask):

    shifts = {"jer_up", "jer_down"}

    sandbox = "docker::riga/law_example_singletop"
    force_sandbox = True

    def requires(self):
        return ConvertData.req(self)

    def output(self):
        return law.LocalFileTarget(self.local_path("data.npz"))

    @law.decorator.log
    def run(self):
        events = self.input().load()["events"]

        # vary jer in all events
        vary_jer(events, self.shift_inst.direction)

        output = self.output()
        output.parent.touch()
        output.dump(events=events)


class SelectAndReconstruct(DatasetTask):

    shifts = VaryJER.shifts

    sandbox = "docker::riga/law_example_singletop"
    force_sandbox = True

    def requires(self):
        return (ConvertData if self.shift_inst.is_nominal else VaryJER).req(self)

    def output(self):
        return self.local_target("data.npz")

    @law.decorator.log
    def run(self):
        events = self.input().load()["events"]

        # selection
        callback = self.create_progress_callback(len(events), (0, 50))
        indexes, selected_objects = select(events, callback=callback)
        self.publish_message("selected {} of {} events".format(len(indexes), len(events)))
        events = events[indexes]

        # reconstruction
        callback = self.create_progress_callback(len(events), (50, 100))
        reco_data = reconstruct(events, selected_objects, callback=callback)
        self.publish_message("reconstructed {} variables".format(len(reco_data.dtype.names)))
        events = join_struct_arrays(events, reco_data)

        with self.output().localize("w") as tmp:
            tmp.dump(events=events)


class CreateHistograms(ConfigTask):

    shifts = VaryJER.shifts

    sandbox = "docker::riga/law_example_singletop"
    force_sandbox = True

    def requires(self):
        reqs = OrderedDict()
        for dataset in self.config_inst.datasets:
            reqs[dataset] = SelectAndReconstruct.req(self, dataset=dataset.name)
        return reqs

    def output(self):
        return self.local_target("hists.tgz")

    @law.decorator.log
    def run(self):
        # load input arrays per dataset, map them to the first linked process
        events = OrderedDict()
        for dataset, inp in self.input().items():
            process = list(dataset.processes.values())[0]
            events[process] = inp.load()["events"]
            self.publish_message("loaded events for dataset {}".format(dataset.name))

        tmp_dir = law.LocalDirectoryTarget(is_tmp=True)
        tmp_dir.touch()

        for variable in self.config_inst.variables:
            stack_plot(events, variable, tmp_dir.child(variable.name + ".pdf", "f").path)
            self.publish_message("written histogram for variable {}".format(variable.name))

        with self.output().localize("w") as tmp:
            tmp.dump(tmp_dir)
