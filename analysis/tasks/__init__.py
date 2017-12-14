# -*- coding: utf-8 -*-

"""
TODO.
"""


import law
import six

from analysis.framework.tasks import ConfigTask, DatasetTask
from analysis.framework.selection import select_singleTop as select
from analysis.framework.reconstruction import reconstruct_singleTop as reconstruct
from analysis.framework.util import join_struct_arrays
import analysis.setup.singleTop


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

    sandbox = "docker::riga/law_example_base"
    force_sandbox = True

    def requires(self):
        return FetchData.req(self)

    def output(self):
        return law.LocalFileTarget(self.local_path("data.npz"))

    @law.decorator.log
    def run(self):
        import root_numpy as rnp

        output = self.output()
        output.parent.touch()

        output.dump(events=rnp.root2array(self.input().path))


class SelectAndReconstruct(DatasetTask):

    sandbox = "docker::riga/law_example_base"
    force_sandbox = True

    def requires(self):
        return ConvertData.req(self)

    def output(self):
        return law.LocalFileTarget(self.local_path("data.npz"))

    @law.decorator.log
    def run(self):
        events = self.input().load()["events"]

        # selection
        indexes, selected_objects = select(events)
        self.publish_message("selected {} of {} events".format(len(indexes), len(events)))
        events = events[indexes]

        # reconstruction
        reco_data = reconstruct(events, selected_objects)
        self.publish_message("reconstructed {} variables".format(len(reco_data.dtype.names)))
        events = join_struct_arrays(events, reco_data)

        output = self.output()
        output.parent.touch()
        output.dump(events=events)


class CreateHistograms(ConfigTask):

    sandbox = "docker::riga/law_example_base"
    force_sandbox = True

    def requires(self):
        reqs = {}
        for dataset in self.config_inst.datasets:
            reqs[dataset] = SelectAndReconstruct.req(self, dataset=dataset.name)
        return reqs

    def output(self):
        return law.LocalFileTarget(self.local_path("hists.tgz"))

    @law.decorator.log
    def run(self):
        import matplotlib
        matplotlib.use("AGG")
        import matplotlib.pyplot as plt

        # load input arrays per dataset
        events = {}
        for dataset, inp in self.input().items():
            self.publish_message("loading events for dataset {}".format(dataset.name))
            events[dataset] = inp.load()["events"]

        pass
