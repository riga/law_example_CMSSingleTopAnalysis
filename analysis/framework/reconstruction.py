# coding: utf-8

"""
Event reconstruction and helpers.
"""


__all__ = ["reconstruct_singletop"]


from six.moves import zip


def reconstruct_singletop(events, selected_objects, callback=None):
    import numpy as np

    names = ["Jet1_Pt"]

    reco_data = np.empty((len(events),), dtype=[(name, "<f4") for name in names])

    for i, (event, objects, reco) in enumerate(zip(events, selected_objects, reco_data)):
        reconstruct_event_singletop(event, objects, reco)
        if callable(callback):
            callback(i)

    return reco_data


def reconstruct_event_singletop(event, selected_objects, reco_data):
    jets, btagged_jets, mu, met = selected_objects

    reco_data["Jet1_Pt"] = jets[0].Pt()
    # TODO
