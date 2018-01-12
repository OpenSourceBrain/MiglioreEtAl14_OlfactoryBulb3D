import imp, sys, os; sys.path.insert(0,'..'); sys.path.insert(0,'../NEURON');
from tests.NEURONTest import NEURONTest
# from tests.networks.NEURONNetworkTestDebugger import NEURONNetworkTestDebugger as NEURONNetworkTest
from tests.networks.NEURONNetworkTest import NEURONNetworkTest as NEURONNetworkTest
from tests.networks.NeuroMLNetworkTest import NeuroMLNetworkTest


currentRangeMC = (-1, 3)
currentRangeGC = (-0.01, 0.1)
syngmax = 0.1 # Make the synapse do something interesting

class NEURON(NEURONNetworkTest):

    def __init__(self):
        super(NEURON, self).__init__()

        self.path = "../NEURON/customsim.py"
        self.label = "Net_1MC_1GC"
        self.currentRangeMC = currentRangeMC
        self.currentRangeGC = currentRangeGC
        self.resultsFile = "results/networks/Net_1MC_1GC/NEURON.json"

    def prepare(self, h):
        # Build the network with 1GC 1MC
        sys.path.append(os.getcwd())
        import customsim
        import modeldata
        customsim.setup(1, 1)
        model = modeldata.getmodel()


        h.AmpaNmda[0].gmax = syngmax
        h.FastInhib[0].gmax = syngmax

        net = {
            "granule": model.granules[110821],
            "mitral": model.mitrals[0]
        }

        h.celsius = 24

        return net

class NeuroML(NeuroMLNetworkTest):
    def __init__(self):
        super(NeuroML, self).__init__()

        self.path = "../NeuroML2/Networks/Bulb_1MC_1GC.net.nml"
        self.label = "Net_1MC_1GC"
        self.currentRangeMC = currentRangeMC
        self.currentRangeGC = currentRangeGC
        self.resultsFile = "results/networks/Net_1MC_1GC/NeuroML.json"

    def prepare(self, h):
        networkFile = os.path.basename(self.path)+"_TestBed_nrn.py"

        # Load the python file with the network code
        with open(networkFile, 'rb') as f:
            modelFile = imp.load_module(
                networkFile.replace(".py",""),
                f,
                networkFile,
                ('.py', 'rb', imp.PY_SOURCE)
            )

        model = modelFile.NeuronSimulation(tstop=5, dt=0.01)

        h.AmpaNmdaSynapse[0].gMax = syngmax
        h.FIsyn[0].gbase = syngmax

        net = {
            "granule": h.a_Pop_Granule_0_110821[0],
            "mitral": h.a_Pop_Mitral_0_0[0]
        }

        h.celsius = 24

        return net

class NetPyNE(NEURONTest):
    def __init__(self):
        super(NetPyNE, self).__init__()

        self.path = "../NeuroML2/Networks/Bulb_1MC_1GC.net.nml"
        self.label = "Net_1MC_1GC"
        self.resultsFile = "results/networks/Net_1MC_1GC/NetPyNE.json"

    def prepare(self, h, soma, mechanism):
        raise NotImplementedError()

