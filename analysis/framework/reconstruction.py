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
        reconstruct_event_singleTop(event, objects, reco)

    return reco_data


def reconstruct_event_singleTop(event, selected_objects, reco_data):
    jets, btagged_jets, mu, met = selected_objects

    reco_data["Jet1_Pt"] = jets[0].Pt()
    # TODO
