import os
import re
import sys

import numpy as np

sys.path.insert(0,'..')
from tests.NEURONTest import NEURONTest

class NEURONSynapseTest(NEURONTest):

    def getResults(self):

        os.chdir(self.modelDir())

        # Compile mod files
        self.printAndRun("nrnivmodl")

        # Start neuron and load mod files
        self.loadNEURONandModFiles()

        # Parse the mod file
        with open(self.modelFileName()) as f:
            modFile = f.read()

            # Get the name of the synapse
            synapse = re.compile("POINT_PROCESS (.*)").search(modFile).group(1)

            # Get the current variable
            currentVariable = re.compile(r"NONSPECIFIC_CURRENT (.*?)\W").search(modFile).group(1)

        # Create a passive test cell
        soma = self.h.Section()
        soma.insert('pas')

        # Create the synapse on the cell
        syn = getattr(self.h, synapse)(soma(0.5))

        # Perform any model specific preparations
        self.prepare(self.h, soma, syn)

        # Create a connection to stimulate the synapse
        # 50-100 LTP
        # 100-400 LTD
        # 700-1300 no change
        stimTimes = [50, 60, 70, 80, 90, 100, 200, 300, 400, 700, 1000, 1300]
        conn = self.h.NetCon(None, syn)
        conn.weight[0] = 1

        def stimSyn():
            for t in stimTimes:
                conn.event(t)

        fih = self.h.FInitializeHandler(stimSyn)


        self.h.tstop = np.max(stimTimes)+50
        self.h.steps_per_ms = 16
        self.h.dt = 1.0 / self.h.steps_per_ms

        # Setup recorders
        self.setupRecorders(t=self.h._ref_t,
                            v=soma(0.5)._ref_v,
                            i=getattr(syn, "_ref_" + currentVariable) )

        result = {"synStim": []}

        # Run simulation
        self.h.run()

        # Gather output variables - subsample to once per ms
        t, v, i = self.subSampleTVI(self.h.steps_per_ms / 4)

        result["synStim"].append({
            "label": "Synapse stimulation",
            "time": t,
            "voltage": v,
            "current": i,
        })

        # # DEBUG
        # # Plot the current traces
        # from matplotlib import pyplot as plt
        # for trace in result["synStim"]:
        #     plt.plot(trace["time"], trace["current"], label=trace["label"])
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
            resultKey = "synStim",
            variable = "current"
        )