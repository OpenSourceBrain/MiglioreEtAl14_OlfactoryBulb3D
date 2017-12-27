import sys; sys.path.insert(0,'..')
from tests.channels.NEURONChannelTest import NEURONChannelTest

class NEURON(NEURONChannelTest):

    def __init__(self):
        super(NEURON, self).__init__()

        self.path = "../NEURON/naxn.mod"
        self.label = "nax"
        self.resultsFile = "results_NEURON.json"

    def prepare(self, model):
        model.gbar = 0.010

