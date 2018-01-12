import sys, os; sys.path.insert(0,'..'); sys.path.insert(0,'../NEURON'); sys.path.insert(0,'../Python/Export')
from tests.cells.NEURONCellTest  import NEURONCellTest
from tests.cells.NeuroMLCellTest import NeuroMLCellTest

class NEURON(NEURONCellTest):

    def __init__(self):
        super(NEURON, self).__init__()

        self.path = "../NEURON/granule.hoc"
        self.label = "granule_passive"
        self.resultsFile = "results/cells/granule_passive/NEURON.json"
        self.currentRange = (-0.01, 0.1)

    def prepare(self, h):

        # Build the network with desired number of GCs - including spines
        sys.path.append(os.getcwd())
        import customsim
        import modeldata
        customsim.setup(1, 1)
        model = modeldata.getmodel()
        cell = model.granules[110821] # The GC of the first MC

        h.celsius = 24

        self.disableNonPassiveChannels(h)

        from exportHelper import sendToBlender as sendToBlender
        sendToBlender(cell.soma)

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

        self.path = "../NeuroML2/GranuleCells/Exported/Granule_110821.cell.nml"
        self.label = "granule_passive"
        self.resultsFile = "results/cells/granule_passive/NeuroML.json"
        self.id = "Granule_110821"
        self.currentRange = (-0.01, 0.1)

    def prepare(self, h):
        # Load the cell hoc
        h.load_file(self.id+".hoc")

        cell = getattr(h,self.id)()

        h.celsius = 24

        self.disableNonPassiveChannels(h)

        return cell

    def disableNonPassiveChannels(self, h):
        for section in h.allsec():
            try: section.gmax_nax__sh15 = 0
            except: pass

            try: section.gmax_kamt = 0
            except: pass

            try: section.gmax_kdrmt = 0
            except: pass

