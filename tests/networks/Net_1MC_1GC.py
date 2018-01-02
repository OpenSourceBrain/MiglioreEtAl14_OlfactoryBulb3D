import sys; sys.path.insert(0,'..')
from tests.NEURONTest import NEURONTest

class NEURON(NEURONTest):

    def __init__(self):
        super(NEURON, self).__init__()

        self.path = "../NEURON/customsim.py"
        self.label = "Net_1MC_1GC"
        self.resultsFile = "results/networks/Net_1MC_1GC/NEURON.json"

    def prepare(self, h, soma, mechanism):
        raise NotImplementedError()

class NeuroML(NEURONTest):
    def __init__(self):
        super(NeuroML, self).__init__()

        self.path = "../NeuroML/Networks/Bulb_1MC_1GC.net.nml"
        self.label = "Net_1MC_1GC"
        self.resultsFile = "results/networks/Net_1MC_1GC/NeuroML.json"

    def prepare(self, h, soma, mechanism):
        raise NotImplementedError()

class NetPyNE(NEURONTest):
    def __init__(self):
        super(NetPyNE, self).__init__()

        self.path = "../NeuroML/Networks/Bulb_1MC_1GC.net.nml"
        self.label = "Net_1MC_1GC"
        self.resultsFile = "results/networks/Net_1MC_1GC/NetPyNE.json"

    def prepare(self, h, soma, mechanism):
        raise NotImplementedError()

