import sys; sys.path.insert(0,'..')
from tests.synapses.NEURONSynapseTest import NEURONSynapseTest
from tests.synapses.NeuroMLSynapseTest import NeuroMLSynapseTest

class NEURON(NEURONSynapseTest):

    def __init__(self):
        super(NEURON, self).__init__()

        self.path = "../NEURON/ampanmda.mod"
        self.label = "AmpaNmda"
        self.resultsFile = "results/synapses/AmpaNmda/NEURON.json"

    def prepare(self, h, soma, syn):
        syn.gmax = 2000

class NeuroML(NeuroMLSynapseTest):
    def __init__(self):
        super(NeuroML, self).__init__()

        self.path = "../NeuroML2/Synapses/AmpaNmda.synapse.xml"
        self.label = "AmpaNmda"
        self.resultsFile = "results/synapses/AmpaNmda/NeuroML.json"

    def prepare(self, h, soma, syn):
        syn.gMax = 2000

