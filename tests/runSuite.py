import channels

import pydevd
pydevd.settrace('192.168.177.1', port=4200, stdoutToServer=True, stderrToServer=True, suspend=False)


def runSuite():
    import_submodules("channels")

    compare(channels.nax.NEURON.NEURON(), channels.nax.NeuroML.NeuroML())

def compare(NEURONtest, NMLtest):
    NEURONtest.getResultsOwnThread()
    NMLtest.getResultsOwnThread()

    # TODO: store results file with full-ish path
    # remove ploting code, move to later
    # add compare code

def import_submodules(package_name):
    import sys, importlib, pkgutil

    package = sys.modules[package_name]

    for loader, name, is_pkg in pkgutil.walk_packages(package.__path__):
        importlib.import_module(package_name + '.' + name)

        if is_pkg:
            import_submodules(package_name + '.' + name)

runSuite()