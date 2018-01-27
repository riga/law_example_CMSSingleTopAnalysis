# -*- coding: utf-8 -*-

"""
Simple task chain that fetches public data, converts them to structured numpy arrays, applies
a simple selection and event reconstruction, and outputs some simple histograms.

Each public data file is treated en bloc by the tasks in this file. For a map-reduce-like task
chain, see branched.py.
"""


from collections import OrderedDict

import law
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
        return law.LocalFileTarget(self.local_path("data.root"))

    @law.decorator.log
    def run(self):
        output = self.output()
        output.parent.touch()

        # fetch the input file
        src = self.dataset_info_inst.keys[0]
        six.moves.urllib.request.urlretrieve(src, output.path)


class ConvertData(DatasetTask):

    sandbox = "docker::riga/law_example_singletop"
    force_sandbox = True

    def requires(self):
        return FetchData.req(self)

    def output(self):
        return law.LocalFileTarget(self.local_path("data.npz"))

    @law.decorator.log
    def run(self):
        import root_numpy as rnp

        events = rnp.root2array(self.input().path)

        output = self.output()
        output.parent.touch()
        output.dump(events=events)

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
        return law.LocalFileTarget(self.local_path("data.npz"))

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

        output = self.output()
        output.parent.touch()
        output.dump(events=events)


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
        return law.LocalFileTarget(self.local_path("hists.tgz"))

    @law.decorator.log
    def run(self):
        # load input arrays per dataset, map them to the first linked process
        events = OrderedDict()
        for dataset, inp in self.input().items():
            process = list(dataset.processes.values())[0]
            events[process] = inp.load()["events"]
            self.publish_message("loaded events for dataset {}".format(dataset.name))

        tmp = law.LocalDirectoryTarget(is_tmp=True)
        tmp.touch()

        for variable in self.config_inst.variables:
            stack_plot(events, variable, tmp.child(variable.name + ".pdf", "f").path)
            self.publish_message("written histogram for variable {}".format(variable.name))

        output = self.output()
        output.parent.touch()
        output.dump(tmp)
