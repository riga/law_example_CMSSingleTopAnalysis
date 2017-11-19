# -*- coding: utf-8 -*-

"""
TODO.
"""


import law
import six

from analysis.framework.tasks import DatasetTask
import analysis.setup.singleTop


class FetchData(DatasetTask):

    sandbox = "docker::riga/law_example_base"
    force_sandbox = True

    def output(self):
        return law.LocalFileTarget(self.local_path("data.root"))

    @law.decorator.log
    def run(self):
        output = self.output()
        output.parent.touch()

        # fetch the input file
        src = self.dataset_info_inst.keys[0]
        six.moves.urllib.request.urlretrieve(src, output.path)
