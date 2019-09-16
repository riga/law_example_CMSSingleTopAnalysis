# coding: utf-8

"""
Common campaign and dataset definitions for 2011 Open Data @ 7 TeV.
"""


__all__ = [
    "campaign_opendata_2011", "dataset_singleTop", "dataset_WJets", "dataset_ZJets",
    "dataset_WWJets", "dataset_WZJets", "dataset_ZZJets",
]


import order as od

import analysis.config.processes as procs


#
# define campaign
#

campaign_opendata_2011 = cp = od.Campaign("opendata_2011", 1,
    ecm=7,  # TeV
    bx=50,  # ns
)


#
# define datasets
# (n_files is set artificially to have <= 5k events per file)
#

dataset_singleTop = cp.add_dataset("singleTop", 210,
    processes=[procs.process_singleTop],
    keys=["http://opendata.cern.ch/record/210/files/single_top.root"],
    n_files=2,
    n_events=5684,
)

dataset_WJets = cp.add_dataset("WJets", 205,
    processes=[procs.process_WJets],
    keys=["http://opendata.cern.ch/record/205/files/wjets.root"],
    n_files=22,
    n_events=109737,
)

dataset_ZJets = cp.add_dataset("ZJets", 206,
    processes=[procs.process_ZJets],
    keys=["http://opendata.cern.ch/record/206/files/dy.root"],
    n_files=16,
    n_events=77729,
)

dataset_WWJets = cp.add_dataset("WWJets", 207,
    processes=[procs.process_WWJets],
    keys=["http://opendata.cern.ch/record/206/files/dy.root"],
    n_files=1,
    n_events=4580,
)

dataset_WZJets = cp.add_dataset("WZJets", 208,
    processes=[procs.process_WZJets],
    keys=["http://opendata.cern.ch/record/206/files/dy.root"],
    n_files=1,
    n_events=3367,
)

dataset_ZZJets = cp.add_dataset("ZZJets", 209,
    processes=[procs.process_ZZJets],
    keys=["http://opendata.cern.ch/record/206/files/dy.root"],
    n_files=1,
    n_events=2421,
)
