# -*- coding: utf-8 -*-

"""
Functions that apply systematic uncertainties.
"""


__all__ = ["apply_jer"]


from random import gauss

from analysis.framework.opendata import *


def apply_jer(events, direction):
    for event in events:
        apply_event_jer(event, direction)


def apply_event_jer(event, direction):
    for i in range(event["NJet"]):
        jet = load_jet(event, i)

        # shift and smear by 5%
        if direction == "up":
            jet *= gauss(1.05, 0.05)
        elif direction == "down":
            jet *= gauss(0.95, 0.05)

        dump_particle(event, i, jet, "Jet")
