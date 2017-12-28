import channels, cells

import pydevd
pydevd.settrace('192.168.177.1', port=4200, stdoutToServer=True, stderrToServer=True, suspend=False)


def runSuite():
    import_submodules("channels")
    import_submodules("cells")

    #compare(channels.nax.NEURON(), channels.nax.NeuroML())
    #compare(channels.kamt.NEURON(), channels.kamt.NeuroML())
    #compare(channels.kdrmt.NEURON(), channels.kdrmt.NeuroML())

    #compare(cells.mitral.NEURON(), cells.mitral.NeuroML())
    compare(cells.granule.NEURON(), cells.granule.NeuroML())

def compare(NEURONtest, NMLtest):
    NEURONtest.getResults()#OwnThread()
    NMLtest.getResults()#OwnThread()

    NEURONtest.compareTo(NMLtest)

    print("Comparison saved to " + NEURONtest.comparisonPath())
    print(NEURONtest.label + " NeuroML conversion differs from NEURON by " + str(NEURONtest.comparisonMean) + "% on average")

def import_submodules(package_name):
    import sys, importlib, pkgutil

    package = sys.modules[package_name]

    for loader, name, is_pkg in pkgutil.walk_packages(package.__path__):
        importlib.import_module(package_name + '.' + name)

        if is_pkg:
            import_submodules(package_name + '.' + name)

runSuite()