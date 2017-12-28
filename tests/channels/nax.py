import sys; sys.path.insert(0,'..')
from tests.channels.NEURONChannelTest import NEURONChannelTest
from tests.channels.NeuroMLChannelTest import NeuroMLChannelTest

class NEURON(NEURONChannelTest):

    def __init__(self):
        super(NEURON, self).__init__()

        self.path = "../NEURON/naxn.mod"
        self.label = "nax"
        self.resultsFile = "results/channels/nax/NEURON.json"

    def prepare(self, h, soma, mechanism):
        h.celsius = 24

        soma.Ra = 150
        soma.cm = 0.7
        soma.ena = 50

        mechanism.gbar = 0.04
        mechanism.sh = 5

class NeuroML(NeuroMLChannelTest):
    def __init__(self):
        super(NeuroML, self).__init__()

        self.path = "../NeuroML2/Channels/nax.channel.nml"
        self.label = "nax"
        self.resultsFile = "results/channels/nax/NeuroML.json"

    def prepare(self, h, soma, mechanism):
        h.celsius = 24

        soma.Ra = 150
        soma.cm = 0.7
        soma.ena = 50

        mechanism.gmax = 0.04

