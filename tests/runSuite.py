import channels, cells, synapses, networks

import pydevd
pydevd.settrace('192.168.177.1', port=4200, stdoutToServer=True, stderrToServer=True, suspend=False)

def runSuite():
    import_submodules("channels")
    import_submodules("cells")
    import_submodules("synapses")
    import_submodules("networks")

    summary = []

    summary.append(compare(channels.nax))
    summary.append(compare(channels.kamt))
    summary.append(compare(channels.kdrmt))

    summary.append(compare(cells.mitral))
    summary.append(compare(cells.granule))

    summary.append(compare(synapses.FI))
    summary.append(compare(synapses.AmpaNmda))

    summary.append(compare(networks.Net_1MC_1GC))

    summary.append(compare(networks.Net_1MC_1GC, conversion = "NetPyNE"))

    generateReport(summary)

def compare(modelTestModule, conversion = "NeuroML"):
    NEURONtest = modelTestModule.NEURON()
    conversionTest =  getattr(modelTestModule, conversion)()

    # Remove result plot before comparison
    import os
    if os.path.isfile(NEURONtest.comparisonPath()):
        os.remove(NEURONtest.comparisonPath())

    try:
        NEURONtest.getResultsOwnThread()
    except:
        NEURONtest.error = True

    try:
        conversionTest.getResultsOwnThread()
    except:
        conversionTest.error = True

    if NEURONtest.error or conversionTest.error:
        print(NEURONtest.label + " " + conversion + " comparison could not be peformed because of errors running one of the models")
    else:
        NEURONtest.compareTo(conversionTest)

        print("Comparison saved to " + NEURONtest.comparisonPath())
        print(NEURONtest.label + " "+ conversion +" conversion output differs from NEURON by " + str(NEURONtest.comparisonMean) + "% on average")

    return { "result": NEURONtest, "conversion": conversion }

def generateReport(summary):
    import os, math

    def round_to_n(x, n):
        if not x: return 0
        power = -int(math.floor(math.log10(abs(x)))) + (n - 1)
        factor = (10 ** power)
        return round(x * factor) / factor

    reportHTML = "<html><body><h2>Test Summary</h2>"

    # Create overview
    reportHTML = reportHTML + "<table>"
    reportHTML = reportHTML + "<tr><td>Model</td><td>Conversion Percent Difference from Original</td></tr>"

    for item in summary:
        reportHTML = reportHTML + "<tr><td>" + item["result"].label + " " + item["conversion"] + "</td><td>" + ((str(round_to_n(item["result"].comparisonMean, 4)) + "%") if not item["result"].error else 'ERROR')+ "</td></tr>"

    reportHTML = reportHTML + "</table>"

    reportHTML = reportHTML + "<h2>Test Details</h2>"

    # Create detailed plots
    reportHTML = reportHTML + "<table style='width: 100%; overflow: hidden; table-layout: fixed;'>"
    for item in summary:
        if not item["result"].error:
            reportHTML = reportHTML + "<tr><td><img src='"+ item["result"].comparisonPath() +"' style='width: 100%;'/></td></tr>"
    reportHTML = reportHTML + "</table>"



    reportHTML = reportHTML+"</body></html>"

    with open("report.html", "w") as f:
        f.write(reportHTML)

    print("Summary report generated in " + os.path.abspath('report.html'))

def import_submodules(package_name):
    import sys, importlib, pkgutil

    package = sys.modules[package_name]

    for loader, name, is_pkg in pkgutil.walk_packages(package.__path__):
        importlib.import_module(package_name + '.' + name)

        if is_pkg:
            import_submodules(package_name + '.' + name)



runSuite()