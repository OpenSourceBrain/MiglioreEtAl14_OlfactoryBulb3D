import os, sys, re, json
from matplotlib import pyplot as plt
import numpy as np
sys.path.insert(0,'..');
from tests.NEURONTest import NEURONTest

class NEURONNetworkTestDebugger(NEURONTest):

    def getResults(self):

        os.chdir(self.modelDir())

        # Compile mod files
        self.printAndRun("nrnivmodl")

        # Start neuron and load mod files
        self.loadNEURONandModFiles()

        # Perform any model specific preparations
        net = self.prepare(self.h)

        result1 = self.performProtocol(
            inputCellLabel    = "MC",
            outputCellLabel   = "GC",
            currentRange = self.currentRangeMC,
            inputCell = net["mitral"],
            outputCell = net["granule"]
        )

        result = { "iclamp": result1 }

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

    def performProtocol(self, inputCellLabel, outputCellLabel, currentRange, inputCell, outputCell):
        ic = self.h.IClamp(inputCell.soma(0.5))
        ic.delay = 50
        ic.dur = 100
        ic.amp = -65

        self.h.tstop = ic.delay + ic.dur + 50  # With extra 50ms at the end
        self.h.steps_per_ms = 16
        self.h.dt = 1.0 / self.h.steps_per_ms

        # Record time, voltage, and current
        # self.setupRecorders(t=self.h._ref_t, v=outputCell.soma(0.5)._ref_v, i=ic._ref_i)

        # debugVar = self.h.FIsyn[0]._ref_i if hasattr(self.h, "FIsyn") else self.h.FastInhib[0]._ref_i
        debugVar = self.h.AmpaNmda[0]._ref_i if hasattr(self.h, "AmpaNmda") else self.h.AmpaNmdaSynapse[0]._ref_i

        self.setupRecorders(t=self.h._ref_t, v=outputCell.soma(0.5)._ref_v, i=debugVar)

        # Create test levels
        icLevels = [2]

        result = []

        # Run simulations for each IClamp test level
        for level in icLevels:
            ic.amp = level

            self.h.run()

            # Gather output variables - subsample to once per ms
            t, v, i = self.subSampleTVI(self.h.steps_per_ms)

            result.append({
                "label": outputCellLabel + " v with " + str(level) + " nA into " + inputCellLabel,
                "time": t,
                "voltage": v,
                "current": i,
            })

        return result

    def compareTo(self, target):
        return self.compareTraces(
            target,
            resultKey = "iclamp",
            variable = "current"
        )