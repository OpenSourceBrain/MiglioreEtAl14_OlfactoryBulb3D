import os, sys, re, json
from matplotlib import pyplot as plt
import numpy as np
sys.path.insert(0,'..')
from tests.NEURONTest import NEURONTest

class NEURONChannelTest(NEURONTest):
    def getResults(self):

        os.chdir(self.modelDir())

        # Compile mod files
        self.printAndRun("nrnivmodl")

        # Start neuron and load mod files
        from neuron import h, gui

        # Parse the mod file
        with open(self.modelFileName()) as f:
            modFile = f.read()

            # Get the name of the mechanism
            mechanism = re.compile("SUFFIX (.*)").search(modFile).group(1)

            # Get the current used
            currentVariable = re.compile(r"USEION.*WRITE (.*?)\W").search(modFile).group(1)

        # Create a test cell and insert the mechanism into the soma
        soma = h.Section()
        soma.insert(mechanism)

        # Perform any model specific preparations
        self.prepare(getattr(soma(0.5), mechanism))

        # Create a voltage clamp
        vc = h.SEClamp(soma(0.5))
        vc.rs = 0.0001
        vc.dur1 = vc.dur3 = 50
        vc.amp1 = vc.amp3 = -65
        vc.dur2 = 100

        h.tstop = vc.dur1 + vc.dur2 + vc.dur3
        h.steps_per_ms = 16
        h.dt = 1.0 / h.steps_per_ms

        # Setup recorders
        tVector = h.Vector()
        tVector.record(h._ref_t)

        vVector = h.Vector()
        vVector.record(soma(0.5)._ref_v)

        iVector = h.Vector()
        iVector.record(getattr(soma(0.5), "_ref_" + currentVariable))

        # Create test levels
        vcLevels = np.linspace(-80, 20, num=11)

        result = {"vclamp": []}

        # Run simulations for each VClamp test level
        for level in vcLevels:
            vc.amp2 = level

            h.run()

            # Gather output variables - subsample to once per ms
            t = self.subSampleVector(tVector, h.steps_per_ms)
            v = self.subSampleVector(vVector, h.steps_per_ms)
            i = self.subSampleVector(iVector, h.steps_per_ms)

            result["vclamp"].append({
                "label": str(level) + " mV",
                "time": t,
                "voltage": v,
                "current": i,
            })

        # Plot the current traces
        for trace in result["vclamp"]:
            plt.plot(trace["time"], trace["current"], label=trace["label"])

        plt.legend()
        plt.show()

        # Save the traces to json file for later comparison
        self.resultsFilePath = self.startPath + "/results/channels/" + self.label + "/" + self.resultsFile

        with open(self.resultsFilePath, "w") as file:
            json.dump(result, file)

        # Return cwd to starting dir
        self.restoreStartDir()

        return self.resultsFilePath