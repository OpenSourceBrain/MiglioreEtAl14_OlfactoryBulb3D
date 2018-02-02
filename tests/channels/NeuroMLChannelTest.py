import os, sys, re, json
from matplotlib import pyplot as plt
import numpy as np
sys.path.insert(0,'..')
from tests.ModelTest import ModelTest
from tests.channels.NEURONChannelTest import NEURONChannelTest

class NeuroMLChannelTest(ModelTest):
    def getResults(self):

        # Gather info from channel nml file to generate the test bed
        with open(self.path) as f:
            channelNML = f.read()
            suffix = re.compile('<ionChannel.*id="(.*?)"').search(channelNML).group(1)

        # Create a test bed for channel
        with open("channels/LEMS_TestBed_Template.xml") as f:
            testBed = f.read()

        testBed = testBed \
            .replace("[ChannelFile]", self.modelFileName()) \
            .replace("[ChannelSuffix]", suffix)

        testBedFile = self.modelFileName() + "_TestBed.xml"

        # Place the lems test bed in same folder as the channel
        with open(self.modelDir() + "/" + testBedFile, "w") as f:
            f.write(testBed)

        # Convert NML to NEURON
        os.chdir(self.modelDir())
        self.printAndRun("jnml " + testBedFile + " -neuron")

        # Return cwd to starting dir
        self.restoreStartDir()

        # Once converted to NEURON, create sub model
        subModel = NEURONChannelTest()
        subModel.path = self.modelDir() + "/" + suffix + ".mod"
        subModel.label = self.label
        subModel.prepare = self.prepare
        subModel.resultsFile = self.resultsFile

        # Now the converted mod file is ready for the protocol
        resultsFile = subModel.getResults()

        return resultsFile