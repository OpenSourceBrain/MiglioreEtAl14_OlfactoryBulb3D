import imp, sys, os; sys.path.insert(0,'..'); sys.path.insert(0,'../NEURON');
from tests.NEURONTest import NEURONTest
# from tests.networks.NEURONNetworkTestDebugger import NEURONNetworkTestDebugger as NEURONNetworkTest
from tests.networks.NEURONNetworkTest import NEURONNetworkTest as NEURONNetworkTest
from tests.networks.NeuroMLNetworkTest import NeuroMLNetworkTest

currentMC = 1

class NEURON(NEURONNetworkTest):

    def __init__(self):
        super(NEURON, self).__init__()

        self.path = "../NEURON/customsim.py"
        self.label = "Net_1MC_2GC"
        self.currentMC = currentMC
        self.resultsFile = "results/networks/Net_1MC_2GC/NEURON.json"

    def prepare(self, h):
        # Build the network with 2GC 1MC
        sys.path.append(os.getcwd())
        import customsim
        import modeldata
        customsim.setup(1, 2)
        model = modeldata.getmodel()

        for syn in h.AmpaNmda:
            syn.gmax = 100

        for syn in h.FastInhib:
            syn.gmax = 4

        net = {
            "granules": [
                {'id':110821, 'cell':model.granules[110821]},
                {'id':92220, 'cell':model.granules[92220]}
            ],
            "mitrals": [
                {'id': 0, 'cell': model.mitrals[0]}
            ]
        }

        h.celsius = 24

        return net

class NeuroML(NeuroMLNetworkTest):
    def __init__(self):
        super(NeuroML, self).__init__()

        self.path = "../NeuroML2/Networks/Bulb_1MC_2GC.net.nml"
        self.label = "Net_1MC_2GC"
        self.currentMC = currentMC
        self.resultsFile = "results/networks/Net_1MC_2GC/NeuroML.json"

    def prepare(self, h):
        modelFile = self.load_python_network()
        model = modelFile.NeuronSimulation(tstop=5, dt=0.01) # The params are ignored

        for syn in h.AmpaNmdaSynapse:
            syn.gMax = 100

        for syn in h.FIsyn:
            syn.gbase = 4

        net = {
            "granules": [
                {'id': 110821, 'cell':h.a_Pop_Granule_0_110821[0]},
                {'id': 92220, 'cell':h.a_Pop_Granule_0_92220[0]}
            ],
            "mitrals": [
                {'id': 0, 'cell':h.a_Pop_Mitral_0_0[0]}
            ]
        }

        h.celsius = 24

        return net

