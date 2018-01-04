import sys, os; sys.path.insert(0,'..'); sys.path.insert(0,'../NEURON');
from tests.NEURONTest import NEURONTest
from tests.networks.NEURONNetworkTest  import NEURONNetworkTest

class NEURON(NEURONNetworkTest):

    def __init__(self):
        super(NEURON, self).__init__()

        self.path = "../NEURON/customsim.py"
        self.label = "Net_1MC_1GC"
        self.currentRangeMC = (-1, 3)
        self.currentRangeGC = (-0.01, 0.1)
        self.resultsFile = "results/networks/Net_1MC_1GC/NEURON.json"

    def prepare(self, h):
        # Build the network with 1GC 1MC
        sys.path.append(os.getcwd())
        import customsim
        import modeldata
        customsim.setup(1, 1)
        model = modeldata.getmodel()

        h.NetCon[0].weight[0] = 500
        h.NetCon[1].weight[0] = 500

        net = {
            "granule": model.granules[110821],
            "mitral": model.mitrals[0]
        }

        h.celsius = 24

        return net

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

