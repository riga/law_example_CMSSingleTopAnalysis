# coding: utf-8

"""
Event selection.
"""


__all__ = ["select_singletop"]


from analysis.framework.opendata import load_met, load_electron, load_muon, load_jet


def select_singletop(events, callback=None):
    indexes = []
    objects = []

    cb = callable(callback)

    for i, event in enumerate(events):
        objs = select_event_singletop(event)
        if objs:
            indexes.append(i)
            objects.append(objs)
        if cb:
            callback(i)

    return indexes, objects


def select_event_singletop(event):
    # trigger selection
    if not event["triggerIsoMu24"]:
        return False

    # MET selection
    met = load_met(event)
    if met.Pt() <= 25:
        return False

    # electron selection
    eles = []
    veto_eles = []
    for i in range(event["NElectron"]):
        ele = load_electron(event, i)
        if ele.Pt() > 20 and abs(ele.Eta()) < 2.1 and ele.Iso < 0.12:
            eles.append(ele)
        elif ele.Pt() > 10 and abs(ele.Eta()) < 2.4 and ele.Iso < 0.24:
            veto_eles.append(ele)

    # muon selection
    mus = []
    veto_mus = []
    for i in range(event["NMuon"]):
        mu = load_muon(event, i)
        if mu.Pt() > 20 and abs(mu.Eta()) < 2.1 and mu.Iso < 0.12:
            mus.append(mu)
        elif mu.Pt() > 10 and abs(mu.Eta()) < 2.4 and mu.Iso < 0.24:
            veto_mus.append(mu)

    # overall lepton selection, we only focus on muons
    if len(mus) != 1 or len(eles) + len(veto_eles) + len(veto_mus) > 0:
        return False
    mu = mus[0]

    # jet selection
    jets = []
    for i in range(event["NJet"]):
        jet = load_jet(event, i)
        if jet.ID and jet.Pt() > 25 and abs(jet.Eta()) < 4.5:
            jets.append(jet)
    if len(jets) < 2:
        return False
    # sort by pt
    jets.sort(key=lambda jet: -jet.Pt())

    # btag selection (TCHP medium)
    btagged_jets = filter(lambda jet: jet.btag > 1.93, jets)
    if len(btagged_jets) < 1:
        return False

    return (jets, btagged_jets, mu, met)
