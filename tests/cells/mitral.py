import sys; sys.path.insert(0,'..'); sys.path.insert(0,'../NEURON');
from tests.cells.NEURONCellTest  import NEURONCellTest
from tests.cells.NeuroMLCellTest import NeuroMLCellTest

class NEURON(NEURONCellTest):

    def __init__(self):
        super(NEURON, self).__init__()

        self.path = "../NEURON/mkmitral.py"
        self.label = "mitral"
        self.resultsFile = "results/cells/mitral/NEURON.json"
        self.currentRange = (-1, 3)

    def prepare(self, h):
        import mkmitral

        cell = mkmitral.mkmitral(0)

        h.celsius = 24

        return cell

class NeuroML(NeuroMLCellTest):
    def __init__(self):
        super(NeuroML, self).__init__()

        self.path = "../NeuroML2/MitralCells/Exported/Mitral_0_0.cell.nml"
        self.label = "mitral"
        self.resultsFile = "results/cells/mitral/NeuroML.json"
        self.id = "Mitral_0_0"
        self.currentRange = (-1, 3)

    def prepare(self, h):
        # Load the cell hoc
        h.load_file(self.id+".hoc")

        cell = getattr(h,self.id)()

        h.celsius = 24

        return cell



