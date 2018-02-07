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
        self.loadNEURONandModFiles()

        # Perform any model specific preparations
        cell = self.prepare(self.h)
        soma = cell.soma

        # Create a current clamp
        ic = self.h.IClamp(soma(0.01)) # was 0.5
        ic.delay = 50
        ic.dur = 100
        ic.amp = -65

        self.h.tstop = ic.delay + ic.dur + 50 # With extra 50ms at the end
        self.h.steps_per_ms = 16
        self.h.dt = 1.0 / self.h.steps_per_ms

        # Record time, voltage, and current
        self.setupRecorders(t = self.h._ref_t, v = soma(0.5)._ref_v, i = ic._ref_i)

        # Create vectors for each segment of each section
        # Need to keep track of section ids, and segments ids that can be be linked together with Blender ids
        # The ids need to be managed at morphology export time, so they stay consistent when streaming the membrane potential

        # Create test levels
        icLevels = np.linspace(np.min(self.currentRange),
                               np.max(self.currentRange),
                               num=11)

        result = {"iclamp": []}

        # Run simulations for each IClamp test level
        for level in icLevels:
            ic.amp = level

            self.h.run()

            # Gather output variables - subsample to once per ms
            t, v, i = self.subSampleTVI(self.h.steps_per_ms / 4)


            # DEBUG Blender
            # for key in self.vectors:
            #     self.vectors[key] = self.subSampleVector(self.vectors[key], self.h.steps_per_ms)

            # from exportHelper import sendVectorsToBlender as sendVectorsToBlender
            # sendVectorsToBlender(t, self.vectors)

            result["iclamp"].append({
                "label": str(level) + " nA",
                "time": t,
                "voltage": v,
                "current": i,
            })

        # # DEBUG
        # # # Plot the voltage traces
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