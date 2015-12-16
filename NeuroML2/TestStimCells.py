
from pyneuroml import pynml
from pyneuroml.lems import generate_lems_file_for_neuroml

import neuroml as nml

ref = "TestStimCells"
number_cells = 1
nml_file0 = "PartialBulb_%iMTCells.net.nml"%number_cells    
nml_file1 = nml_file0.replace('.net.nml', '_%s.net.nml'%ref)


nml_doc = pynml.read_neuroml2_file(nml_file0)


for i in range(number_cells):
    stim = "2nA"
    input_id = ("input_%s_%i"%(stim, i))
    pg = nml.PulseGenerator(id=input_id,
                                delay="40ms",
                                duration="100ms",
                                amplitude=stim)
    nml_doc.pulse_generators.append(pg)

    pop = 'Pop_Mitral_0_%i'%i
    # Add these to cells
    input_list = nml.InputList(id=input_id,
                             component=pg.id,
                             populations=pop)
    input = nml.Input(id='0', 
                          target="../%s[%i]"%(pop, i), 
                          destination="synapses")  
    input_list.input.append(input)
    nml_doc.networks[0].input_lists.append(input_list)
    

pynml.write_neuroml2_file(nml_doc, nml_file1)

plots = {}
saves = {}
for i in range(number_cells):
    p = []
    plots['Mitral_0_%i'%i] = p
    p.append('Pop_Mitral_0_%i/0/Mitral_0_%i/0/v'%(i,i))
    #p.append('Pop_Mitral_0_%i/0/Mitral_0_%i/681/v'%(i,i))
    #p.append('Pop_Mitral_0_%i/0/Mitral_0_%i/20/v'%(i,i))
    p.append('Pop_Mitral_0_%i/0/Mitral_0_%i/43/v'%(i,i))
    #save_plot.append('Pop_Mitral_0_%i/0/Mitral_0_%i/682/v'%(i,i))
    #save_plot.append('Pop_Mitral_0_%i/0/Mitral_0_%i/20/v'%(i,i))
    #save_plot.append('Pop_Mitral_0_%i/0/Mitral_0_%i/43/v'%(i,i))
    
print plots
print saves

generate_lems_file_for_neuroml(ref, 
                                nml_file1, 
                                "network", 
                                180, 
                                0.01, 
                                'LEMS_%s.xml'%ref,
                                '.',
                                gen_plots_for_all_v = False,
                                gen_plots_for_quantities = plots,
                                gen_saves_for_all_v = False,
                                gen_saves_for_quantities = saves,
                                copy_neuroml=False)


