import os, sys, re, json
from matplotlib import pyplot as plt
import numpy as np
sys.path.insert(0,'..');
from tests.NEURONTest import NEURONTest

class NEURONNetworkTest(NEURONTest):

    def getResults(self):

        os.chdir(self.modelDir())

        # Compile mod files
        self.printAndRun("nrnivmodl")

        # Start neuron and load mod files
        self.loadNEURONandModFiles()

        # Perform any model specific preparations
        net = self.prepare(self.h)

        # Record time and voltage
        self.tVector = self.h.Vector()
        self.tVector.record(self.h._ref_t)

        vectors = []
        ics = []

        for mc in net["mitrals"]:
            # Inject into MC tuft
            ic = self.h.IClamp(mc["cell"].priden(1.0))
            ic.delay = 25
            ic.dur = 150
            ic.amp = self.currentMC
            ics.append(ic)

            # Record at the soma
            vector = self.h.Vector()
            vector.record(mc["cell"].soma(0.5)._ref_v)
            vectors.append({"label":"MC"+str(mc["id"])+" soma V","vector":vector})

        for gc in net["granules"]:
            # Record at each GC primary dendrite
            vector = self.h.Vector()
            vector.record(gc["cell"].priden(1.0)._ref_v)
            vectors.append({"label":"GC"+str(gc["id"])+" pridend V","vector":vector})

        self.h.tstop = 200
        self.h.steps_per_ms = 16
        self.h.dt = 1.0 / self.h.steps_per_ms

        result = []

        # Run simulations
        self.h.run()

        # Gather output variables - subsample to once per ms
        t = self.subSampleVector(self.tVector, self.h.steps_per_ms)

        for vector in vectors:
            v = self.subSampleVector(vector["vector"], self.h.steps_per_ms)

            result.append({
                "label": vector["label"],
                "time": t,
                "voltage": v
            })

        self.on_run_complete()

        result = { "iclamp": result }

        # DEBUG
        # # Plot the voltage traces
        # for trace in result["iclamp"]:
        #     plt.plot(trace["time"], trace["voltage"], label=trace["label"])
        #
        # plt.legend()
        # plt.show()

        # Save the traces to json file for later comparison
        self.saveResults(result)

        # Return cwd to starting dir
        self.restoreStartDir()

    def compareTo(self, target):
        return self.compareTraces(
            target,
            resultKey = "iclamp",
            variable = "voltage"
        )