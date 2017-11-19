# -*- coding: utf-8 -*-

"""
Common campaign and dataset definitions for 2011 Open Data @ 7 TeV.
"""


__all__ = ["campaign_opendata_2011", "dataset_singleTop", "dataset_WJets", "dataset_ZJets",
           "dataset_WWJets", "dataset_WZJets", "dataset_ZZJets"]


import order as od

from analysis.setup.processes import *


#
# define campaign
#

campaign_opendata_2011 = cmpgn = od.Campaign("opendata_2011", 1,
    ecm = 7,  # TeV
    bx  = 50, # ns
)


#
# define datasets
# (n_files is artificially set to have <= 5k events per file)
#

dataset_singleTop = cmpgn.add_dataset("singleTop", 210,
    keys     = ["http://opendata.cern.ch/record/210/files/single_top.root"],
    n_files  = 2,
    n_events = 5684,
)

dataset_WJets = cmpgn.add_dataset("WJets", 205,
    keys     = ["http://opendata.cern.ch/record/205/files/wjets.root"],
    n_files  = 22,
    n_events = 109737,
)

dataset_ZJets = cmpgn.add_dataset("ZJets", 206,
    keys     = ["http://opendata.cern.ch/record/206/files/dy.root"],
    n_files  = 16,
    n_events = 77729,
)

dataset_WWJets = cmpgn.add_dataset("WWJets", 207,
    keys     = ["http://opendata.cern.ch/record/206/files/dy.root"],
    n_files  = 1,
    n_events = 4580,
)

dataset_WZJets = cmpgn.add_dataset("WZJets", 208,
    keys     = ["http://opendata.cern.ch/record/206/files/dy.root"],
    n_files  = 1,
    n_events = 3367,
)

dataset_ZZJets = cmpgn.add_dataset("ZZJets", 209,
    keys     = ["http://opendata.cern.ch/record/206/files/dy.root"],
    n_files  = 1,
    n_events = 2421,
)


#
# link processes
#

dataset_singleTop.add_process(process_singleTop)
dataset_WJets.add_process(process_WJets)
dataset_ZJets.add_process(process_ZJets)
dataset_WWJets.add_process(process_WWJets)
dataset_WZJets.add_process(process_WZJets)
dataset_ZZJets.add_process(process_ZZJets)
