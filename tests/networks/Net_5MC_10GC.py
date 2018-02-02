import sys, os; sys.path.insert(0,'..'); sys.path.insert(0,'../NEURON');
from tests.NEURONTest import NEURONTest
# from tests.networks.NEURONNetworkTestDebugger import NEURONNetworkTestDebugger as NEURONNetworkTest
from tests.networks.NEURONNetworkTest import NEURONNetworkTest as NEURONNetworkTest
from tests.networks.NeuroMLNetworkTest import NeuroMLNetworkTest

currentMC = 1

class NEURON(NEURONNetworkTest):

    def __init__(self):
        super(NEURON, self).__init__()

        self.path = "../NEURON/customsim.py"
        self.label = "Net_5MC_10GC"
        self.currentMC = currentMC
        self.resultsFile = "results/networks/Net_5MC_10GC/NEURON.json"

    def prepare(self, h):
        # Build network
        sys.path.append(os.getcwd())
        import customsim
        import modeldata
        customsim.setup(5, 2)
        model = modeldata.getmodel()

        for syn in h.AmpaNmda:
            syn.gmax = 100

        for syn in h.FastInhib:
            syn.gmax = 4

        net = {
            "granules": [
                {'id': 63634, 'cell': model.granules[63634]},
                {'id': 122244, 'cell': model.granules[122244]},
                {'id': 110821, 'cell': model.granules[110821]},
                {'id': 106198, 'cell': model.granules[106198]},
                {'id': 116279, 'cell': model.granules[116279]},
                {'id': 110559, 'cell': model.granules[110559]},
                {'id': 100735, 'cell': model.granules[100735]},
                {'id': 92220, 'cell': model.granules[92220]},
                {'id': 112690, 'cell': model.granules[112690]},
                {'id': 94639, 'cell': model.granules[94639]}
            ],
            "mitrals": [
                {'id': 0, 'cell': model.mitrals[0]},
                {'id': 1, 'cell': model.mitrals[1]},
                {'id': 2, 'cell': model.mitrals[2]},
                {'id': 3, 'cell': model.mitrals[3]},
                {'id': 4, 'cell': model.mitrals[4]}
            ]
        }

        h.celsius = 24

        return net

class NeuroML(NeuroMLNetworkTest):
    def __init__(self):
        super(NeuroML, self).__init__()

        self.path = "../NeuroML2/Networks/Bulb_5MC_10GC.net.nml"
        self.label = "Net_5MC_10GC"
        self.currentMC = currentMC
        self.resultsFile = "results/networks/Net_5MC_10GC/NeuroML.json"

    def prepare(self, h):
        modelFile = self.load_python_network()
        model = modelFile.NeuronSimulation(tstop=5, dt=0.01) # The params are ignored

        for syn in h.AmpaNmdaSynapse:
            syn.gMax = 100

        for syn in h.FIsyn:
            syn.gbase = 4

        net = {
            "granules": [
                {'id': 63634, 'cell': h.a_Pop_Granule_0_63634[0]},
                {'id': 122244, 'cell': h.a_Pop_Granule_0_122244[0]},
                {'id': 110821, 'cell': h.a_Pop_Granule_0_110821[0]},
                {'id': 106198, 'cell': h.a_Pop_Granule_0_106198[0]},
                {'id': 116279, 'cell': h.a_Pop_Granule_0_116279[0]},
                {'id': 110559, 'cell': h.a_Pop_Granule_0_110559[0]},
                {'id': 100735, 'cell': h.a_Pop_Granule_0_100735[0]},
                {'id': 92220, 'cell': h.a_Pop_Granule_0_92220[0]},
                {'id': 112690, 'cell': h.a_Pop_Granule_0_112690[0]},
                {'id': 94639, 'cell': h.a_Pop_Granule_0_94639[0]}
            ],
            "mitrals": [
                {'id': 0, 'cell': h.a_Pop_Mitral_0_0[0]},
                {'id': 1, 'cell': h.a_Pop_Mitral_0_1[0]},
                {'id': 2, 'cell': h.a_Pop_Mitral_0_2[0]},
                {'id': 3, 'cell': h.a_Pop_Mitral_0_3[0]},
                {'id': 4, 'cell': h.a_Pop_Mitral_0_4[0]}
            ]
        }

        h.celsius = 24

        return net

