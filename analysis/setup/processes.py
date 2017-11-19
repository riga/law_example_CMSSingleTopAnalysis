# -*- coding: utf-8 -*-

"""
Common process definitions.
"""


__all__ = ["process_singleTop", "process_VJets", "process_WJets", "process_ZJets", "process_VVJets",
           "process_WWJets", "process_WZJets", "process_ZZJets"]


import order as od
import scinum as sn


#
# define processes
# (cross sections are made up as all datasets in this example correspond to 50/fb)
#

process_singleTop = od.Process("singleTop", 1000,
    label       = r"Single $t/\bar{t}$",
    label_short = "ST",
    color       = (67, 118, 201),
    xsecs       = {
        7: sn.Number(5684. / 50, ("rel", 0.07)),
    },
)

process_VJets = od.Process("VJets", 2000,
    label       = r"V + Jets",
    label_short = "V",
    color       = (235, 230, 10),
)

process_WJets = process_VJets.add_process("WJets", 2100,
    label       = r"W + Jets",
    label_short = "W",
    xsecs       = {
        7: sn.Number(109737. / 50, ("rel", 0.05)),
    },
)

process_ZJets = process_VJets.add_process("ZJets", 2200,
    label       = r"Z + Jets",
    label_short = "DY",
    xsecs       = {
        7: sn.Number(77729. / 50, ("rel", 0.05)),
    },
)

process_VVJets = od.Process("VVJets", 3000,
    label       = r"Diboson",
    label_short = "VV",
    color       = (81, 142, 25),
)

process_WWJets = process_VJets.add_process("WWJets", 3100,
    label       = r"WW + Jets",
    label_short = "WW",
    xsecs       = {
        7: sn.Number(4580. / 50, ("rel", 0.04)),
    },
)

process_WZJets = process_VJets.add_process("WZJets", 3200,
    label       = r"WZ + Jets",
    label_short = "WZ",
    xsecs       = {
        7: sn.Number(3367. / 50, ("rel", 0.04)),
    },
)

process_ZZJets = process_VJets.add_process("ZZJets", 3300,
    label       = r"ZZ + Jets",
    label_short = "ZZ",
    xsecs       = {
        7: sn.Number(2421. / 50, ("rel", 0.04)),
    },
)
