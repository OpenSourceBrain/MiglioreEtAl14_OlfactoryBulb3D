import sys; sys.path.insert(0,'..')
from tests.channels.NEURONChannelTest import NEURONChannelTest
from tests.channels.NeuroMLChannelTest import NeuroMLChannelTest

class NEURON(NEURONChannelTest):

    def __init__(self):
        super(NEURON, self).__init__()

        self.path = "../NEURON/kdrmt.mod"
        self.label = "kdrmt"
        self.resultsFile = "results/channels/kdrmt/NEURON.json"

    def prepare(self, h, soma, mechanism):
        h.celsius = 24

        soma.Ra = 150
        soma.cm = 0.7
        soma.ek = -90

        mechanism.gbar = 0.001

class NeuroML(NeuroMLChannelTest):
    def __init__(self):
        super(NeuroML, self).__init__()

        self.path = "../NeuroML2/Channels/kdrmt.channel.nml"
        self.label = "kdrmt"
        self.resultsFile = "results/channels/kdrmt/NeuroML.json"

    def prepare(self, h, soma, mechanism):
        h.celsius = 24

        soma.Ra = 150
        soma.cm = 0.7
        soma.ek = -90

        mechanism.gmax = 0.001

