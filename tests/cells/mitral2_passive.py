import sys, os; sys.path.insert(0,'..'); sys.path.insert(0,'../NEURON');
from tests.cells.NEURONCellTest  import NEURONCellTest
from tests.cells.NeuroMLCellTest import NeuroMLCellTest

class NEURON(NEURONCellTest):

    def __init__(self):
        super(NEURON, self).__init__()

        self.path = "../NEURON/mkmitral.py"
        self.label = "mitral2_passive"
        self.resultsFile = "results/cells/mitral2_passive/NEURON.json"
        self.currentRange = (-1, 3)

    def prepare(self, h):
        # Build the network with 1MC
        sys.path.append(os.getcwd())
        import customsim
        import modeldata
        customsim.setup(2, 1)
        model = modeldata.getmodel()
        cell = model.mitrals[1]  # The second MC

        h.celsius = 24

        self.disableNonPassiveChannels(h)

        return cell

    def disableNonPassiveChannels(self, h):
        for section in h.allsec():

            try: section.gbar_nax = 0
            except: pass

            try: section.gbar_kdrmt = 0
            except: pass

            try: section.gbar_kamt = 0
            except: pass

class NeuroML(NeuroMLCellTest):
    def __init__(self):
        super(NeuroML, self).__init__()

        self.path = "../NeuroML2/MitralCells/Exported/Mitral_0_1.cell.nml"
        self.label = "mitral2_passive"
        self.resultsFile = "results/cells/mitral2_passive/NeuroML.json"
        self.id = "Mitral_0_1"
        self.currentRange = (-1, 3)

    def prepare(self, h):
        # Load the cell hoc
        h.load_file(self.id+".hoc")

        cell = getattr(h,self.id)()

        h.celsius = 24

        self.disableNonPassiveChannels(h)

        return cell

    def disableNonPassiveChannels(self, h):

        for section in h.allsec():
            try: section.gmax_nax__sh10 = 0
            except: pass

            try: section.gmax_nax__sh0 = 0
            except: pass

            try: section.gmax_kamt = 0
            except: pass

            try: section.gmax_kdrmt = 0
            except: pass



