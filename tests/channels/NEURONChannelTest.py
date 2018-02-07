import os
import re
import sys

import numpy as np

sys.path.insert(0,'..')
from tests.NEURONTest import NEURONTest

class NEURONChannelTest(NEURONTest):

    def getResults(self):

        os.chdir(self.modelDir())

        # Compile mod files
        self.printAndRun("nrnivmodl")

        # Start neuron and load mod files
        self.loadNEURONandModFiles()

        # Parse the mod file
        with open(self.modelFileName()) as f:
            modFile = f.read()

            # Get the name of the mechanism
            mechanism = re.compile("SUFFIX (.*)").search(modFile).group(1)

            # Get the current used
            currentVariable = re.compile(r"USEION.*WRITE (.*?)\W").search(modFile).group(1)

        # Create a test cell and insert the mechanism into the soma
        soma = self.h.Section()
        soma.insert(mechanism)

        # Perform any model specific preparations
        self.prepare(self.h, soma, getattr(soma(0.5), mechanism))

        # Create a voltage clamp
        vc = self.h.SEClamp(soma(0.5))
        vc.rs = 0.0001
        vc.dur1 = vc.dur3 = 50
        vc.amp1 = vc.amp3 = self.h.v_init = -65
        vc.dur2 = 100

        self.h.tstop = vc.dur1 + vc.dur2 + vc.dur3
        self.h.steps_per_ms = 16
        self.h.dt = 1.0 / self.h.steps_per_ms

        # Setup recorders
        self.setupRecorders(t=self.h._ref_t,
                            v=soma(0.5)._ref_v,
                            i=getattr(soma(0.5), "_ref_" + currentVariable) )

        # Create test levels
        vcLevels = np.linspace(-80, 20, num=11)

        result = {"vclamp": []}

        # Run simulations for each VClamp test level
        for level in vcLevels:
            vc.amp2 = level

            self.h.run()

            # Gather output variables - subsample to once per ms
            t, v, i = self.subSampleTVI(self.h.steps_per_ms / 4)

            result["vclamp"].append({
                "label": str(level) + " mV",
                "time": t,
                "voltage": v,
                "current": i,
            })

        # # DEBUG
        # # Plot the current traces
        # for trace in result["vclamp"]:
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
            resultKey = "vclamp",
            variable = "current"
        )