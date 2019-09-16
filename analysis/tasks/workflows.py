# coding: utf-8

"""
Task chain using workflows that fetches public data, converts them to structured numpy arrays,
splits them to achieve a map-reduce-like workflow, applies a simple selection and event
reconstruction, "reduces" them again into a single file per dataset, and outputs some simple
histograms.

Each chunk of a public data file is treated as a branch of a workflow allowing for higher
concurrency during task processing. For a more simple, straight-forward task chain, see simple.py.
"""


from collections import OrderedDict

import six
import law
law.contrib.load("numpy", "root", "docker")

import analysis.config.singletop  # noqa: F401
from analysis.framework.tasks import ConfigTask, DatasetTask
from analysis.framework.selection import select_singletop as select
from analysis.framework.reconstruction import reconstruct_singletop as reconstruct
from analysis.framework.systematics import vary_jer
from analysis.framework.plotting import stack_plot
from analysis.framework.util import join_struct_arrays


class FetchData(DatasetTask):

    sandbox = law.NO_STR
    allow_empty_sandbox = True

    def output(self):
        return self.local_target("data.root")

    @law.decorator.safe_output
    def run(self):
        # fetch the input file and save it
        with self.localize_output("w") as output:
            src = self.dataset_info_inst.keys[0]
            six.moves.urllib.request.urlretrieve(src, output.path)


class ConvertData(DatasetTask):

    sandbox = "docker::riga/law_example_singletop"

    def requires(self):
        return FetchData.req(self)

    def output(self):
        return self.local_target("data.npz")

    @law.decorator.safe_output
    def run(self):
        # load via the root_numpy formatter which converts root trees into numpy arrays
        events = self.input().load(formatter="root_numpy")
        self.publish_message("converted {} events".format(len(events)))

        # dump the written events
        with self.localize_output("w") as output:
            output.dump(events=events, formatter="numpy")


class MapData(DatasetTask, law.LocalWorkflow):

    sandbox = "docker::riga/law_example_singletop"

    def workflow_requires(self):
        # extend requirements of the workflow, i.e., the object that steers all branch tasks
        reqs = super(MapData, self).workflow_requires()
        reqs["data"] = ConvertData.req(self)
        return reqs

    def requires(self):
        return ConvertData.req(self)

    def output(self):
        # encode the branch number into the output target name
        return self.local_target("data_{}.npz".format(self.branch))

    @law.decorator.safe_output
    def run(self):
        # load the events
        events = self.input().load(allow_pickle=True, formatter="numpy")["events"]

        # "map" events into chunks, use the numer of files stored in the dataset instance
        slices = law.util.partial_slices(events.shape[0], self.dataset_info_inst.n_files)
        start, end = slices[self.branch]
        chunk = events[start:end]

        # dump the chunk of events
        with self.localize_output("w") as output:
            output.dump(events=chunk, formatter="numpy")


class VaryJER(DatasetTask, law.LocalWorkflow):

    shifts = {"jer_up", "jer_down"}

    sandbox = "docker::riga/law_example_singletop"

    def workflow_requires(self):
        # extend the workflow requirements
        reqs = super(VaryJER, self).workflow_requires()
        reqs["data"] = MapData.req(self)
        return reqs

    def requires(self):
        return MapData.req(self)

    def output(self):
        return self.local_target("data_{}.npz".format(self.branch))

    @law.decorator.safe_output
    def run(self):
        # load the event chunk
        events = self.input().load(allow_pickle=True, formatter="numpy")["events"]

        # vary jer in all events
        vary_jer(events, self.shift_inst.direction)

        # dump events
        with self.localize_output("w") as output:
            output.dump(events=events, formatter="numpy")


class SelectAndReconstruct(DatasetTask, law.LocalWorkflow):

    shifts = VaryJER.shifts

    sandbox = "docker::riga/law_example_singletop"

    def workflow_requires(self):
        # extend the workflow requirements
        reqs = super(SelectAndReconstruct, self).workflow_requires()
        reqs["data"] = self.requires_from_branch()
        return reqs

    def requires(self):
        return (MapData if self.shift_inst.is_nominal else VaryJER).req(self)

    def output(self):
        return self.local_target("data_{}.npz".format(self.branch))

    @law.decorator.safe_output
    def run(self):
        # load the events
        events = self.input().load(allow_pickle=True, formatter="numoy")["events"]

        # selection
        callback = self.create_progress_callback(len(events), (0, 50))
        indexes, selected_objects = select(events, callback=callback)
        self.publish_message("selected {} out of {} events".format(len(indexes), len(events)))
        events = events[indexes]

        # reconstruction
        callback = self.create_progress_callback(len(events), (50, 100))
        reco_data = reconstruct(events, selected_objects, callback=callback)
        self.publish_message("reconstructed {} variables".format(len(reco_data.dtype.names)))
        events = join_struct_arrays(events, reco_data)

        # dump events
        with self.localize_output("w") as output:
            output.dump(events=events, formatter="numpy")


class ReduceData(DatasetTask):

    shifts = SelectAndReconstruct.shifts

    sandbox = "docker::riga/law_example_singletop"

    def requires(self):
        return SelectAndReconstruct.req(self)

    def output(self):
        return self.local_target("data.npz")

    @law.decorator.safe_output
    def run(self):
        import numpy as np

        # load input arrays per dataset and "reduce" them by concatenating
        events = None
        for inp in self.input()["collection"].targets.values():
            chunk = inp.load(allow_pickle=True, formatter="numpy")["events"]
            events = np.concatenate([events, chunk]) if events is not None else chunk

        # dump events
        with self.localize_output("w") as output:
            output.dump(events=events, formatter="numpy")


class CreateHistograms(ConfigTask):

    shifts = SelectAndReconstruct.shifts

    sandbox = "docker::riga/law_example_singletop"

    def requires(self):
        reqs = OrderedDict()
        for dataset in self.config_inst.datasets:
            reqs[dataset] = SelectAndReconstruct.req(self, dataset=dataset.name)
        return reqs

    def output(self):
        return self.local_target("hists.tgz")

    @law.decorator.safe_output
    def run(self):
        # load input arrays per dataset, map them to the first linked process
        events = OrderedDict()
        for dataset, inp in self.input().items():
            process = list(dataset.processes.values())[0]
            events[process] = inp.load(allow_pickle=True, formatter="numpy")["events"]
            self.publish_message("loaded events for dataset {}".format(dataset.name))

        # create a temporary directory in which the histograms are saved
        tmp_dir = law.LocalDirectoryTarget(is_tmp=True)
        tmp_dir.touch()

        # create plots
        for variable in self.config_inst.variables:
            stack_plot(events, variable, tmp_dir.child(variable.name + ".pdf", "f").path)
            self.publish_message("written histogram for variable {}".format(variable.name))

        # save the output directory as an archive
        with self.localize_output("w") as output:
            output.dump(tmp_dir, formatter="tar")
