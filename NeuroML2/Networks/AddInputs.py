
import neuroml
from pyneuroml.lems import generate_lems_file_for_neuroml


import neuroml.loaders as loaders
import neuroml.writers as writers
import random

fn = 'Bulb_3MC_15GC.net.nml'
doc = loaders.NeuroMLLoader.load(fn)

net = doc.networks[0]

mitral_pops = []
granule_pops = []

for pop in net.populations:
    print("Found population %s"%pop.id)
    if 'Mitral' in pop.id:
        mitral_pops.append(pop)
    if 'Granule' in pop.id:
        granule_pops.append(pop)
        
## Add stims to Mitrals

for mtp in mitral_pops:
    
    stim = neuroml.PulseGenerator(id='stim_%s'%mtp.id,
                                 delay='0ms',
                                 duration='2000ms',
                                 amplitude='%snA'%(.1 + .1 * random.random()))

    doc.pulse_generators.append(stim)


    input_list = neuroml.InputList(id="%s_input"%stim.id,
                                   component=stim.id,
                                   populations=mtp.id)

    syn_input = neuroml.Input(id=0,
                              target="../%s/0/%s" % (mtp.id, mtp.component),
                              destination="synapses")

    input_list.input.append(syn_input)
    net.input_lists.append(input_list)
        
        
## Add stims to Granules

for grp in granule_pops:
    
    stim = neuroml.PulseGenerator(id='stim_%s'%grp.id,
                                 delay='0ms',
                                 duration='2000ms',
                                 amplitude='%snA'%(.05 + .05 * random.random()))

    doc.pulse_generators.append(stim)


    input_list = neuroml.InputList(id="%s_input"%stim.id,
                                   component=stim.id,
                                   populations=grp.id)

    syn_input = neuroml.Input(id=0,
                              target="../%s/0/%s" % (grp.id, grp.component),
                              destination="synapses")

    input_list.input.append(syn_input)
    net.input_lists.append(input_list)

    
    
        
nml_file = fn.replace('.net.nml','_inputs.net.nml')

writers.NeuroMLWriter.write(doc,nml_file)

print("Saved network file to: "+nml_file)
     
###### Validate the NeuroML ######    

from neuroml.utils import validate_neuroml2

validate_neuroml2(nml_file)

sim_id = fn.split('.')[0]
target = net.id
duration=200
dt = 0.025
lems_file_name = 'LEMS_%s.xml'%sim_id
target_dir = "."

'''
interesting_seg_ids = [0]

to_plot = {'Some_voltages':[]}
to_save = {'%s_voltages.dat'%sim_id:[]}

for seg_id in interesting_seg_ids:
    to_plot.values()[0].append('%s/0/%s/%s/v'%(pop.id, pop.component,seg_id))
    to_save.values()[0].append('%s/0/%s/%s/v'%(pop.id, pop.component,seg_id))'''
    
generate_lems_file_for_neuroml(sim_id, 
                               nml_file, 
                               target, 
                               duration, 
                               dt, 
                               lems_file_name,
                               target_dir,
                               copy_neuroml = False)


'''gen_plots_for_all_v = False,
                               plot_all_segments = False,
                               gen_plots_for_quantities = to_plot,   #  Dict with displays vs lists of quantity paths
                               gen_saves_for_all_v = False,
                               save_all_segments = False,
                               gen_saves_for_quantities = to_save,   #  Dict with file names vs lists of quantity paths'''