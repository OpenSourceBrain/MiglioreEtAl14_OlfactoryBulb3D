import sys, os; sys.path.insert(0,'..'); sys.path.insert(0,'../NEURON');
from tests.cells.NEURONCellTest  import NEURONCellTest
from tests.cells.NeuroMLCellTest import NeuroMLCellTest

class NEURON(NEURONCellTest):

    def __init__(self):
        super(NEURON, self).__init__()

        self.path = "../NEURON/granule.hoc"
        self.label = "granule"
        self.resultsFile = "results/cells/granule/NEURON.json"
        self.currentRange = (-0.01, 0.1)

    def prepare(self, h):

        # Build the network with 1GC
        sys.path.append(os.getcwd())
        import customsim
        import modeldata
        customsim.setup(1, 1)
        model = modeldata.getmodel()
        cell = model.granules[110821] # The GC of the first MC

        h.celsius = 24

        return cell

class NeuroML(NeuroMLCellTest):
    def __init__(self):
        super(NeuroML, self).__init__()

        self.path = "../NeuroML2/GranuleCells/Exported/Granule_0_110821.cell.nml"
        self.label = "granule"
        self.resultsFile = "results/cells/granule/NeuroML.json"
        self.id = "Granule_0_110821"
        self.currentRange = (-0.01, 0.1)

    def prepare(self, h):
        # Load the cell hoc
        h.load_file(self.id+".hoc")

        cell = getattr(h,self.id)()

        h.celsius = 24

        return cell



