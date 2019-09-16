# coding: utf-8

"""
Interface to the numpy-converted open data format.
"""


__all__ = [
    "load_value", "dump_value", "load_particle", "dump_particle", "load_electron", "load_muon",
    "load_met", "load_jet", "load_mc_lepton", "load_mc_neutrino",
]


# lorentz vector attributes
_vector_attrs = ("_E", "_Px", "_Py", "_Pz")


def make_particle(E, px, py, pz):
    import ROOT
    ROOT.PyConfig.IgnoreCommandLineOptions = True
    ROOT.gROOT.SetBatch()

    return ROOT.TLorentzVector(px, py, pz, E)


def load_value(event, field, i=-1, default=0.):
    if not field:
        return default

    value = event[field]
    if i >= 0:
        value = value[i]

    return value


def dump_value(event, field, value, i=-1):
    if i >= 0:
        event[field][i] = value
    else:
        event[field] = value


def load_particle(event, i, name, vector_attrs=_vector_attrs, attrs=None):
    vector = [load_value(event, attr and name + attr, i) for attr in vector_attrs]
    particle = make_particle(*vector)

    # extend particle attributes
    ext = {"name": name}
    if i >= 0:
        ext["i"] = i
    if attrs:
        ext.update({attr.strip("_"): load_value(event, name + attr, i) for attr in attrs})
    particle.__dict__.update(ext)

    return particle


def dump_particle(event, i, particle, name, vector_attrs=_vector_attrs, attrs=None):
    for getter, attr in zip(_vector_attrs, vector_attrs):
        if attr:
            dump_value(event, name + attr, getattr(particle, getter.lstrip("_"))(), i)

    if attrs:
        for attr in attrs:
            dump_value(event, name + attr, getattr(particle, attr.lstrip("_")), i)


def load_electron(event, i):
    return load_particle(event, i, "Electron", attrs=("_Charge", "_Iso"))


def load_muon(event, i):
    return load_particle(event, i, "Muon", attrs=("_Charge", "_Iso"))


def load_jet(event, i):
    return load_particle(event, i, "Jet", attrs=("_btag", "_ID"))


def load_met(event):
    met = load_particle(event, -1, "MET", (None, "_px", "_py", None))
    met.SetE(met.Pt())
    return met


def load_mc_lepton(event):
    lep = load_particle(event, -1, "MClepton", (None, "_px", "_py", "_pz"), attrs=("PDGid",))
    lep.SetE((lep.P() ** 2. + get_lepton_mass(lep.PDGid) ** 2.) ** 0.5)
    return lep


def load_mc_neutrino(event):
    nu = load_particle(event, -1, "MCneutrino", (None, "_px", "_py", "_pz"))
    nu.SetE(nu.P())
    return nu


def get_lepton_mass(pdg_id, default=0.):
    return {
        11: 510.9989461e-6,
        13: 105.6583745e-3,
        15: 1.77682
    }.get(abs(pdg_id), default)
