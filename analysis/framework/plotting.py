# coding: utf-8

"""
Plotting functions.
"""


__all__ = ["stack_plot"]


def stack_plot(events, variable, path, weight="EventWeight"):
    import matplotlib
    matplotlib.use("AGG")
    import matplotlib.pyplot as plt

    values, weights, labels, colors = [], [], [], []
    s, b = 0., 0.
    for process, evts in list(events.items())[::-1]:
        values.append(evts[variable.expression])
        weights.append(evts[weight])
        labels.append(process.label)
        colors.append(process.color)
        if process == "singleTop":
            s += weights[-1].sum()
        else:
            b += weights[-1].sum()

    use_weight = variable.get_aux("weight", True)

    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.set_xlim(variable.x_min, variable.x_max)
    ax.set_xlabel(variable.get_full_x_title())
    ax.set_ylabel(variable.get_full_y_title())
    ax.tick_params("both", direction="in", top=True, right=True)

    ax.hist(values, variable.bin_edges, weights=weights if use_weight else None, histtype="step",
        stacked=True, fill=True, color=colors, edgecolor="black", linewidth=0.5)
    ax.legend(labels[::-1])
    ax.text(1, 1, r"S / $\sqrt{B}$ = %.2f" % (s / b ** 0.5,), ha="right", va="bottom", size="small",
        transform=ax.transAxes)

    fig.savefig(path, bbox_inches="tight")
