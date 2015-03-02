from neuron import h

h.chdir('../NEURON')
h.load_file('mitral.hoc')

sys.path.append('../NEURON')

from mkmitral import mkmitral

if __name__ == "__main__":

  num_cells_to_export = 30

  cells = []
  for mgid in range(num_cells_to_export):
    print mgid
    cells.append(mkmitral(mgid))

  from pyneuroml.neuron import export_to_neuroml2

  export_to_neuroml2(None, 
                     "../NeuroML2.ManyCells%i.net.nml" % num_cells_to_export, 
                     includeBiophysicalProperties=False,
                     separateCellFiles=True)

  

  
