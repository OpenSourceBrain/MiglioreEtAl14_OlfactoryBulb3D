import channels, cells, synapses

import pydevd
pydevd.settrace('192.168.177.1', port=4200, stdoutToServer=True, stderrToServer=True, suspend=False)

def runSuite():
    import_submodules("channels")
    import_submodules("cells")
    import_submodules("synapses")

    compare(channels.nax)
    compare(channels.kamt)
    compare(channels.kdrmt)

    compare(cells.mitral)
    compare(cells.granule)

    compare(synapses.FI)
    compare(synapses.AmpaNmda)

def compare(modelTestModule):
    NEURONtest = modelTestModule.NEURON()
    NMLtest =  modelTestModule.NeuroML()

    NEURONtest.getResultsOwnThread()
    NMLtest.getResultsOwnThread()

    NEURONtest.compareTo(NMLtest)

    print("Comparison saved to " + NEURONtest.comparisonPath())
    print(NEURONtest.label + " NeuroML conversion output differs from NEURON by " + str(NEURONtest.comparisonMean) + " on average")

def import_submodules(package_name):
    import sys, importlib, pkgutil

    package = sys.modules[package_name]

    for loader, name, is_pkg in pkgutil.walk_packages(package.__path__):
        importlib.import_module(package_name + '.' + name)

        if is_pkg:
            import_submodules(package_name + '.' + name)

runSuite()