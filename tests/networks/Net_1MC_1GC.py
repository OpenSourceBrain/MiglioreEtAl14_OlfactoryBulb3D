import os
import sys

sys.path.insert(0,'..'); sys.path.insert(0,'../NEURON');
# from tests.networks.NEURONNetworkTestDebugger import NEURONNetworkTestDebugger as NEURONNetworkTest
from tests.networks.NEURONNetworkTest import NEURONNetworkTest as NEURONNetworkTest
from tests.networks.NeuroMLNetworkTest import NeuroMLNetworkTest

currentMC = 1

class NEURON(NEURONNetworkTest):

    def __init__(self):
        super(NEURON, self).__init__()

        self.path = "../NEURON/customsim.py"
        self.label = "Net_1MC_1GC"
        self.currentMC = currentMC
        self.resultsFile = "results/networks/Net_1MC_1GC/NEURON.json"

    def prepare(self, h):
        # Build the network with 1GC 1MC
        sys.path.append(os.getcwd())
        import customsim
        import modeldata
        customsim.setup(1, 1)
        model = modeldata.getmodel()


        h.AmpaNmda[0].gmax = 100
        h.FastInhib[0].gmax = 4

        net = {
            "granules": [{'id':110821, 'cell':model.granules[110821]}],
            "mitrals": [{'id':0, 'cell':model.mitrals[0]}]
        }

        h.celsius = 24

        # import sys
        # sys.path.append("/home/justas/Repositories/BlenderNEURON/ForNEURON");
        # from blenderneuron import BlenderNEURON
        # self.blender = BlenderNEURON(h)


        return net

    # def on_run_complete(self):
    #     self.blender.send_model()

class NeuroML(NeuroMLNetworkTest):
    def __init__(self):
        super(NeuroML, self).__init__()

        self.path = "../NeuroML2/Networks/Bulb_1MC_1GC.net.nml"
        self.label = "Net_1MC_1GC"
        self.currentMC = currentMC
        self.resultsFile = "results/networks/Net_1MC_1GC/NeuroML.json"

    def prepare(self, h):
        modelFile = self.load_python_network()

        self.model = modelFile.NeuronSimulation(tstop=5, dt=0.01) # Params don't matter here

        h.AmpaNmdaSynapse[0].gMax = 100
        h.FIsyn[0].gbase = 4

        net = {
            "granules": [{'id':110821, 'cell':h.a_Pop_Granule_0_110821[0]}],
            "mitrals": [{'id':0, 'cell':h.a_Pop_Mitral_0_0[0]}]
        }

        h.celsius = 24

        # sys.path.append("/home/justas/Repositories/BlenderNEURON/ForNEURON");
        # from blenderneuron import BlenderNEURON
        # self.blender = BlenderNEURON(h)

        return net

    # def on_run_complete(self):
    #     self.blender.send_model()

