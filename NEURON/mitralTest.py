from neuron import *
from mkmitral import *
import time

amps = [0.1, 1.0, 2, 5]
delay = 40
duration = 100
tstop = 2*delay+duration
h.dt = 0.05
vinit = -65

cells = []
stims = []
graphs = []


for c in xrange(0,len(amps)):
    
    cells.append(mkmitral(0))

    g=h.Graph(0)
    g.size(0,tstop,-80,50)
    g.view(0,-80,tstop,130, (c % 2)*425,(c / 2)*260,400,200)
    g.addvar('soma (' + str(amps[c]) + 'nA)',       'v(0.5)',1,0, sec = cells[c].soma)
    g.addvar('initialseg (' + str(amps[c]) + 'nA)', 'v(0.5)',2,0, sec = cells[c].initialseg)
    g.addvar('priden (' + str(amps[c]) + 'nA)',     'v(0.5)',3,0, sec = cells[c].priden)
    graphs.append(g)
    
    stim = h.IClamp(0.5, sec = cells[c].soma)
    stim.delay = delay
    stim.amp = amps[c]
    stim.dur = duration
    stims.append(stim)

focusampindex = 1
closeup=h.Graph(0)
closeup.size(90,95,-80,50)
closeup.view(90,-80,5,130, 850,0,400,200)
closeup.addvar('soma (' + str(amps[focusampindex]) + 'nA)',       'v(0.5)',1,0, sec = cells[focusampindex].soma)
closeup.addvar('initialseg (' + str(amps[focusampindex]) + 'nA)', 'v(0.5)',2,0, sec = cells[focusampindex].initialseg)
closeup.addvar('priden (' + str(amps[focusampindex]) + 'nA)',     'v(0.5)',3,0, sec = cells[focusampindex].priden)

def initialize():
    h.finitialize(vinit)
    h.fcurrent()

def integrate():
    
    i = 0
    g.begin()
    
    while h.t< tstop:
        h.fadvance()
        
        for c in xrange(0,len(amps)):
            graphs[c].plot(h.t)
            if i % 10 == 0:
                graphs[c].fastflush()

        closeup.plot(h.t)
        closeup.fastflush()
        
        i = i + 1

    g.flush()


initialize()
integrate()

if raw_input("Press ENTER to quit(), or SPACE + ENTER to continue") != " ":
    quit()
