# -*- coding: utf-8 -*-

"""
Event reconstruction and helpers.
"""


__all__ = ["reconstruct_singleTop"]


import six

from analysis.framework.opendata import *


def reconstruct_singleTop(events, selected_objects):
    import numpy as np

    names = ["Jet1_Pt"]

    reco_data = np.empty((len(events),), dtype=[(name, "<f4") for name in names])

    for event, objects, reco in six.moves.zip(events, selected_objects, reco_data):
        jets, btagged_jets, mu, met = objects

        reco["Jet1_Pt"] = jets[0].Pt()

    return reco_data
