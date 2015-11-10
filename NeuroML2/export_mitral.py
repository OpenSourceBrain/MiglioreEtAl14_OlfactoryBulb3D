from neuron import h

import sys

h.chdir('../NEURON')
h.load_file('mitral.hoc')

sys.path.append('../NEURON')

from mkmitral import mkmitral

from pyneuroml.neuron import export_to_neuroml2
from pyneuroml import pynml
    
if __name__ == "__main__":

    num_cells_to_export = 30

    cells = []
    for mgid in range(num_cells_to_export):
      print mgid
      cells.append(mkmitral(mgid))


    nml_net_file = "../NeuroML2/PartialBulb_%iMTCells.net.nml" % num_cells_to_export
    export_to_neuroml2(None, 
                       nml_net_file, 
                       includeBiophysicalProperties=False,
                       separateCellFiles=True)
                       
    for i in range(num_cells_to_export):
         
        nml_cell_file = "../NeuroML2/Mitral_0_%i.cell.nml" % i        

        nml_doc = pynml.read_neuroml2_file(nml_cell_file)

        cell = nml_doc.cells[0]

        print("Loaded cell with %i segments"%len(cell.morphology.segments))
        bad_root = -1
        root_id = 0
        for seg in cell.morphology.segments:
            if seg.parent is None:
                if seg.id != 0:
                    bad_root = seg.id
                    seg.id = root_id
                    print("Changing root id from %i to %i"%(bad_root,root_id))
                    
        if bad_root > 0:
            for seg in cell.morphology.segments:
                if seg.parent is not None:
                    if seg.parent.segments == bad_root:
                        seg.parent.segments = root_id
            for sg in cell.morphology.segment_groups:
                for memb in sg.members:
                    if memb.segments == bad_root:
                        memb.segments = root_id
                        
        
                    

        pynml.write_neuroml2_file(nml_doc, nml_cell_file)


    pynml.nml2_to_svg(nml_net_file)

  

  
