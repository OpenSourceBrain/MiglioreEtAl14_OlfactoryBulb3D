import os, sys, re, json
from matplotlib import pyplot as plt
import numpy as np
sys.path.insert(0,'..')
from tests.NEURONTest import NEURONTest

class NEURONCellTest(NEURONTest):

    def getResults(self):

        os.chdir(self.modelDir())

        # Compile mod files
        self.printAndRun("nrnivmodl")

        # Start neuron and load mod files
        from neuron import h, gui
        self.h = h

        # Perform any model specific preparations
        cell = self.prepare(h)
        soma = cell.soma

        # Create a current clamp
        ic = h.IClamp(soma(0.5))
        ic.delay = 50
        ic.dur = 100
        ic.amp = -65

        h.tstop = ic.delay + ic.dur + 50 # With extra 50ms at the end
        h.steps_per_ms = 16
        h.dt = 1.0 / h.steps_per_ms

        # Record time, voltage, and current
        self.setupRecorders(t = h._ref_t, v = soma(0.5)._ref_v, i = ic._ref_i)

        # Create test levels
        icLevels = np.linspace(np.min(self.currentRange),
                               np.max(self.currentRange),
                               num=11)

        result = {"iclamp": []}

        # Run simulations for each IClamp test level
        for level in icLevels:
            ic.amp = level

            h.run()

            # Gather output variables - subsample to once per ms
            t, v, i = self.subSampleTVI(h.steps_per_ms)

            result["iclamp"].append({
                "label": str(level) + " nA",
                "time": t,
                "voltage": v,
                "current": i,
            })

        # DEBUG
        # Plot the voltage traces
        for trace in result["iclamp"]:
            plt.plot(trace["time"], trace["voltage"], label=trace["label"])

        plt.legend()
        plt.show()

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