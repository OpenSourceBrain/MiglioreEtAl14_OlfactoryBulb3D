# This script creates graphs of mitral cell voltages at various points vs various current stimulation values
# Also includes a closeup of one of the action potentials
# Run it with the following commmand: "nrniv -python mitralTest.py"

import sys
from neuron import h

h.load_file("stdlib.hoc")
h.load_file("stdgui.hoc")

from mkmitral import *
import csv

amps = [0.1, 1.0, 2, 5] # Current stimulation values in nA
delay = 40 # ms
duration = 100 # ms
tstop = 2*delay+duration
h.dt = 0.01 # ms
h.steps_per_ms = 1/h.dt
vinit = -65 # mV

cells = []
stims = []
graphs = []
closeup = h.Graph(0)
data = []

def main(gui=True):
    
    # For each current value, create a cell
    for c in xrange(0,len(amps)):
        
        cells.append(mkmitral(0))
        
        if gui:
            g=h.Graph(0)
            g.size(0,tstop,-80,50)
            g.view(0,-80,tstop,130, (c % 2)*425,(c / 2)*260,400,200) # Position the graphs on screen
            addVars(g, c)
            graphs.append(g)
        
        stim = h.IClamp(0.5, sec = cells[c].soma)
        stim.delay = delay
        stim.amp = amps[c]
        stim.dur = duration
        stims.append(stim)
    
        data.append([])

    if gui:
        # For one of the current values, create a closeup of the AP
        focusampindex = 1
        closedupStartTime = 90 # ms
        closedupEndTime = 95   # ms
        closeup.size(closedupStartTime,closedupEndTime,-80,50)
        closeup.view(closedupStartTime,-80,closedupEndTime-closedupStartTime,130, 850,0,400,200)
        addVars(closeup, focusampindex)

    initialize()
    integrate() # Plot the graphs

def addVars(graph, ampIndex):
    graph.addvar('soma ('       + str(amps[ampIndex]) + 'nA)', 'v(0.5)',1,0, sec = cells[ampIndex].soma)
    graph.addvar('initialseg (' + str(amps[ampIndex]) + 'nA)', 'v(0.5)',2,0, sec = cells[ampIndex].initialseg)
    graph.addvar('priden ('     + str(amps[ampIndex]) + 'nA)', 'v(0.5)',3,0, sec = cells[ampIndex].priden)

def initialize():
    h.finitialize(vinit)
    h.fcurrent()

def integrate():
    
    print("Running a NEURON simulation of duration %s ms and dt = %s ms"%(tstop,h.dt))
    if gui:
        for c in xrange(0,len(amps)):
            graphs[c].begin()
    
    while h.t< tstop:
        
        for c in xrange(0,len(amps)):
            
            if gui:
                graphs[c].plot(h.t)
                graphs[c].fastflush()
        
            data[c].append([h.t, cells[c].soma.v, cells[c].initialseg.v, cells[c].priden.v])
        
        if gui:
            closeup.plot(h.t)
            closeup.fastflush()

        h.fadvance()

    if gui:
        for c in xrange(0,len(amps)):
            graphs[c].flush()


        with open('mitralTest_%snA.dat'%amps[c], 'w') as outfile:
            writer = csv.writer(outfile, delimiter='\t')
            for row in data[c]:
                writer.writerow(row)
            print("Written data to: %s"%outfile)

gui = not '-nogui' in sys.argv 

main(gui)

if not gui or raw_input("Press ENTER to quit(), or SPACE + ENTER to continue") != " ":
    quit()
