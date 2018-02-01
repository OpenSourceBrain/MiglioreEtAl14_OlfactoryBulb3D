# 3D Model of the Olfactory Bulb (Migliore et al. 2014)
This repository hosts the NeuroML conversion of the Migliore et. al. (2014) model of the olfactory bulb. The original NEURON model has 125 glomeruli, 625 Mitral cells (MCs), and ~125,000 Granule cells (GCs). This project converted the original model channels, cells, synapses, network connectivity, and odor input into NeuroML format. Each converted component has been individualy validated by comparing their responses to the original versions. The conversion error of the channels and synapses is <1%, while cell and network conversion error is <5% (see Validation below). Scaled down network model (5 MCs) is hosted in this repository, while larger versions can be obtained via the export scripts (see Exporting below). [Click here to view an interactive visualization of a 5 Mitral and 10 Granule Cell Network](http://www.opensourcebrain.org/projects/miglioreetal14_olfactorybulb3d?explorer=https%3A%2F%2Fraw.githubusercontent.com%2FJustasB%2FMiglioreEtAl14_OlfactoryBulb3D%2Fmaster%2FNeuroML2%2FNetworks%2FBulb_5MC_10GC.net.nml)

![30 cells](https://raw.githubusercontent.com/OpenSourceBrain/MiglioreEtAl14_OlfactoryBulb3D/master/images/30cells.jpg)
3D rendering of the converted network consisting of 30 Mitral cells

## Overview
![Mitral Spikes with GC response](https://github.com/JustasB/MiglioreEtAl14_OlfactoryBulb3D/blob/master/images/1MC1000GCs.gif)
Stimulation of a single Mitral cell and the response of its Granule cells

### Model Structure
#### Network
The original model depicts a small patch of the mamallian olfactory bulb, consisting of 125 glomeruli with 5 MCs each. Each MC is connected to several hundred GCs via dendro-dendritic synapses. Each GC connects to one MC. MCs are not connected to each other. MC-GC synapses consist of AMPA-NMDA exchitatory synapses onto GCs and Fast Inhbitory synapses onto MCs. Network input is provided by stimulation of MC glomerular tufted dendrites via double exponential synapses with peak current values taken from optical imaging odor maps of a mamallian olfactory bulb.

![Model Diagram](https://github.com/JustasB/MiglioreEtAl14_OlfactoryBulb3D/blob/master/images/modelDiagram.jpg)
 - Cells
 - Synapses
 - Input
 
 # Conversion Validation 
  - Show summary here
  - Link to the html report 
  - OMV
  - Comparison Suite
  
 # Folder Organization
  - Neuron
  - Full
  - NML2
  - Python
  - tests
  
 # How to Download and Use the Converted Model
  - JNML -neuron -> run or python _nrn.py
  - Comparison suite -> plots
  - Visualization via:
  - OSB explorer
  - NEURON modelView
  - BlenderNEURON
  


  
 



This repository contains the original NEURON code from the model:

Migliore M, Cavarretta F, Hines ML, Shepherd GM (2014) Distributed organization of a brain microcircuit analysed by three-dimensional modeling: the olfactory bulb [Front. Comput. Neurosci.](http://journal.frontiersin.org/article/10.3389/fncom.2014.00050/abstract) 8:50, obtained from [ModelDB](http://senselab.med.yale.edu/ModelDB/ShowModel.cshtml?model=151681).

There is an initial version of (elements of) this model in [NeuroML 2 format](https://github.com/OpenSourceBrain/MiglioreEtAl14_OlfactoryBulb3D/tree/master/NeuroML2). 



The developing NeuroML 2 version of the model can be **viewed with the OSB 3D Explorer** as shown above. A [5 Mitral cell](http://www.opensourcebrain.org/projects/miglioreetal14_olfactorybulb3d?explorer=https%3A%2F%2Fraw.githubusercontent.com%2FOpenSourceBrain%2FMiglioreEtAl14_OlfactoryBulb3D%2Fmaster%2FNeuroML2%2FMitralCells%2FExported%2FPartialBulb_5MTCells.net.nml) version of the network or a [30 Mitral cell](http://www.opensourcebrain.org/projects/miglioreetal14_olfactorybulb3d?explorer=https%3A%2F%2Fraw.githubusercontent.com%2FOpenSourceBrain%2FMiglioreEtAl14_OlfactoryBulb3D%2Fmaster%2FNeuroML2%2FMitralCells%2FExported%2FPartialBulb_30MTCells.net.nml) version (slow to load!) are available.

For the latest status of this project, see the [issues](https://github.com/OpenSourceBrain/MiglioreEtAl14_OlfactoryBulb3D/issues).

[![Build Status](https://travis-ci.org/OpenSourceBrain/MiglioreEtAl14_OlfactoryBulb3D.svg)](https://travis-ci.org/OpenSourceBrain/MiglioreEtAl14_OlfactoryBulb3D)
