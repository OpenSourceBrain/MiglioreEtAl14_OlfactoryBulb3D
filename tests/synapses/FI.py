import sys; sys.path.insert(0,'..')
from tests.synapses.NEURONSynapseTest import NEURONSynapseTest
from tests.synapses.NeuroMLSynapseTest import NeuroMLSynapseTest

class NEURON(NEURONSynapseTest):

    def __init__(self):
        super(NEURON, self).__init__()

        self.path = "../NEURON/fi.mod"
        self.label = "FI"
        self.resultsFile = "results/synapses/FI/NEURON.json"

    def prepare(self, h, soma, syn):
        syn.gmax = 1
        syn.tau2 = 100

class NeuroML(NeuroMLSynapseTest):
    def __init__(self):
        super(NeuroML, self).__init__()

        self.path = "../NeuroML2/Synapses/FI.synapse.xml"
        self.label = "FI"
        self.resultsFile = "results/synapses/FI/NeuroML.json"

    def prepare(self, h, soma, syn):
        syn.gbase = 1

