import os
import sys
from neuron import h

import pydevd
pydevd.settrace('10.211.55.3', port=4200, stdoutToServer=True, stderrToServer=True)

h.chdir('../NEURON')
sys.path.append('../NEURON')

def __main__():

    import customsim
    import runsim
    
    MCs = 1
    GCsPerMC = 1
    netFile = "../NeuroML2/Networks/Bulb_%iMC_%iGC.net.nml" % (MCs, MCs*GCsPerMC)
    
    networkTemplatePath =    "../NeuroML2/Networks/NetworkTemplate.xml"
    includeTemplatePath =    "../NeuroML2/Networks/IncludeTemplate.xml"
    populationTemplatePath = "../NeuroML2/Networks/PopulationTemplate.xml"
    projectionTemplatePath = "../NeuroML2/Networks/ProjectionTemplate.xml"
    
    customsim.setup(MCs, GCsPerMC)





if __name__ == "__main__":
    __main__()