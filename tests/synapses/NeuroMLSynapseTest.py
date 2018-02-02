import os, sys, re, json
from matplotlib import pyplot as plt
import numpy as np
sys.path.insert(0,'..')
from tests.ModelTest import ModelTest
from tests.synapses.NEURONSynapseTest import NEURONSynapseTest

class NeuroMLSynapseTest(ModelTest):
    def getResults(self):

        # Gather info from synapse nml file to generate the test bed
        with open(self.path) as f:
            synNML = f.read()
            id = re.compile('<.*id="(.*?)"').search(synNML).group(1)

        # Create a test bed for channel
        with open("synapses/LEMS_TestBed_Template.xml") as f:
            testBed = f.read()

        testBed = testBed \
            .replace("[SynapseFile]", self.modelFileName()) \
            .replace("[SynapseID]", id)

        testBedFile = self.modelFileName() + "_TestBed.xml"

        # Place the lems test bed in same folder as the synapse
        with open(self.modelDir() + "/" + testBedFile, "w") as f:
            f.write(testBed)

        # Convert NML to NEURON
        os.chdir(self.modelDir())
        self.printAndRun("jnml " + testBedFile + " -neuron")

        # Return cwd to starting dir
        self.restoreStartDir()

        # Once converted to NEURON, create sub model
        subModel = NEURONSynapseTest()
        subModel.path = self.modelDir() + "/" + id + ".mod"
        subModel.label = self.label
        subModel.prepare = self.prepare
        subModel.resultsFile = self.resultsFile

        # Now the converted mod file is ready for the protocol
        resultsFile = subModel.getResults()

        return resultsFile