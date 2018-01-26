import sys, os; sys.path.insert(0,'..'); sys.path.insert(0,'../NEURON');
from tests.NEURONTest import NEURONTest
# from tests.networks.NEURONNetworkTestDebugger import NEURONNetworkTestDebugger as NEURONNetworkTest
from tests.networks.NEURONNetworkTest import NEURONNetworkTest as NEURONNetworkTest
from tests.networks.NeuroMLNetworkTest import NeuroMLNetworkTest

currentRangeMC = (-1, 3)
currentRangeGC = (-0.01, 0.1)

class NEURON(NEURONNetworkTest):

    def __init__(self):
        super(NEURON, self).__init__()

        self.path = "../NEURON/customsim.py"
        self.label = "Net_2MC_2GC"
        self.currentRangeMC = currentRangeMC
        self.currentRangeGC = currentRangeGC
        self.resultsFile = "results/networks/Net_2MC_2GC/NEURON.json"

    def prepare(self, h):
        # Build the network with 2GC 2MC
        sys.path.append(os.getcwd())
        import customsim
        import modeldata
        customsim.setup(2, 1)
        model = modeldata.getmodel()

        net = {
            "granule": model.granules[112690],
            "mitral": model.mitrals[1]
        }

        h.celsius = 24

        sys.path.append("/home/justas/Repositories/BlenderNEURON/ForNEURON");
        from blenderneuron import BlenderNEURON
        self.blender = BlenderNEURON(h)

        return net

    def on_run_complete(self):
        self.blender.send_model()

class NeuroML(NeuroMLNetworkTest):
    def __init__(self):
        super(NeuroML, self).__init__()

        self.path = "../NeuroML2/Networks/Bulb_2MC_2GC.net.nml"
        self.label = "Net_2MC_2GC"
        self.currentRangeMC = currentRangeMC
        self.currentRangeGC = currentRangeGC
        self.resultsFile = "results/networks/Net_2MC_2GC/NeuroML.json"

    def prepare(self, h):
        # Load the python file with the network code
        modelFile = self.load_python_network()

        model = modelFile.NeuronSimulation(tstop=5, dt=0.01) # The params are ignored

        net = {
            "granule": h.a_Pop_Granule_0_112690[0],
            "mitral": h.a_Pop_Mitral_0_1[0]
        }

        h.celsius = 24

        return net

