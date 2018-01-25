import os, sys, re, json, imp
from matplotlib import pyplot as plt
import numpy as np
sys.path.insert(0,'..')
from tests.ModelTest import ModelTest
# from tests.networks.NEURONNetworkTestDebugger import NEURONNetworkTestDebugger as NEURONNetworkTest
from tests.networks.NEURONNetworkTest import NEURONNetworkTest

class NeuroMLNetworkTest(ModelTest):
    def getResults(self):

        # Gather info from network nml file to generate the LEMS test bed
        with open(self.path) as f:
            networkNML = f.read()
            networkID = re.compile('<network.*id="(.*?)"').search(networkNML).group(1)

        # Create a test bed for channel
        with open("networks/LEMS_TestBed_Template.xml") as f:
            testBed = f.read()

        testBed = testBed \
            .replace("[NetworkFile]", self.modelFileName()) \
            .replace("[NetworkID]", networkID)

        testBedFile = self.modelFileName() + "_TestBed.xml"

        # Place the lems test bed in same folder as the network
        with open(self.modelDir() + "/" + testBedFile, "w") as f:
            f.write(testBed)

        # Convert NML to NEURON
        os.chdir(self.modelDir())
        self.printAndRun("jnml " + testBedFile + " -neuron -nogui")

        # Return cwd to starting dir
        self.restoreStartDir()

        # Once converted to NEURON, create sub model
        subModel = NEURONNetworkTest()
        subModel.path = self.modelDir() + "/" + testBedFile.replace(".xml","_nrn.py")
        subModel.label = self.label
        subModel.prepare = self.prepare
        subModel.currentRangeMC = self.currentRangeMC
        subModel.currentRangeGC = self.currentRangeGC
        subModel.resultsFile = self.resultsFile

        # Now the converted mod file is ready for the protocol
        subModel.getResults()

    def load_python_network(self):

        networkFile = os.path.basename(self.path) + "_TestBed_nrn.py"

        # Imports underscore containing py file
        with open(networkFile, 'rb') as f:
            modelFile = imp.load_module(
                networkFile.replace(".py", ""),
                f,
                networkFile,
                ('.py', 'rb', imp.PY_SOURCE)
            )

        return modelFile