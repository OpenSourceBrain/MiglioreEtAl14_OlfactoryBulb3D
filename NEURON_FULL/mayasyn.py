# options

gpalette = 'jet' # or 'winter'
gthreshold = None
gweights = True
tube_active = True
scale_mode = 'none'
minfreq_shown = 4.0
maxfreq_shown = 30.0
import custom_params
custom_params.filename = 'fig7'
import params
import bindict
bindict.load('c10.dic')
import granules
syn_gid_begin = params.Nmitral+granules.Ngranule
from colors import palette
from math import sqrt
import binspikes
gthreshold = None 
tube_flag = False
flag_dict = True
interpolate_flag = False

from sys import argv

def granule_info(ggid):
  conns = bindict.ggid_dict[ggid]
  print '\n'
  print 'granule %d is connected with %d mitrals' % (ggid, len(conns))
  for gid in conns:
    info = bindict.gid_dict[gid+1]
    print '\tm%d, %d, %.2g' % info[:3]
  print '\n\n'


t_stop = 40000
t_sub = 2000

def gpo(ggid):
  import granules
  import misc
  import params
  p=granules.ggid2pos[ggid]
  pj=misc.Ellipsoid(params.bulbCenter,params.somaAxis[0]).project(p)
  u=misc.versor(p,params.bulbCenter)
  return list(p),u,list(pj)


   
def plane_dist(q, w, p):
  from math import sqrt
  s1 = .0
  s = 0.
  for j in range(3):
    s += (q[j] - p[j]) * w[j]
    s1 += w[j] ** 2
  return abs(s) / sqrt(s1)

weights = {}
# load weights
def loadweights(fweight):
  global weights
  weights = {}
  with open(fweight) as f:
    line = f.readline()
    while line:
      tokens = line.split()
      gid = int(tokens[0]); w = float(tokens[1])
      weights.update({ gid:w })
      line = f.readline()

#spk_history = '
sr = None

plotcnt = 0
def history_clean():
  global plotcnt
  from matplotlib import pyplot as plt
  for i in range(plotcnt):
    plt.close()
  plotcnt = 0
    
def history(gids):
  global plotcnt
  global sr
  if not sr:
    return
  actlbl.text = 'retrieving...'
  from matplotlib import pyplot as plt
  #plt.ion()
  #try:
  for call in [ binspikes.show_freqs, binspikes.show_raster, binspikes.show_weights ]:
    if call(sr, gids):
      plotcnt += 1

  plt.show()
  #except KeyError:
  #  pass
  actlbl.text = ''


  
# maximal inhibition associated to a granule
def gcolors(_min, _max):
  
  gcol = {}
  for gid in weights.keys():
    
    if gid % 2 == 1:
      
      ggid = gd.gid_dict[gid + 1][3]
      
      w_new = weights[gid]
      
      if w_new < _min or w_new > _max:
        continue
      
      if gcol.has_key(ggid):
        w_old = gcol[ggid]
        if w_old < w_new:
          gcol[ggid] = w_new
      else:
        gcol.update({ ggid:w_new })
        
  return gcol


# granules
#import gid_dict as gd
import bindict as gd


from mayavi.mlab import figure, text
fig = figure(bgcolor=(0, 0, 0))

global actlbl
def label_init():
  from mayavi.mlab import points3d
  obj = points3d(0., 0., 0., scale_factor=0.01, color=(0., 0., 0.))
  global actlbl
  actlbl = text(.4, .1, 'odorname', width=.15)
  actlbl.text = ''
  obj.remove()
  
label_init()

from mayavi.mlab import points3d
import params
import granules
#import synhistory as sh
from neuron import h



  


class GranulesManager:

  def __init__(self):
    self.intr = set()
    self.gran = set()
    
    self.actor1 = None
    self.actor2 = None
    
    self.gran_color = (0., 157 / 255., 157 / 255.)
    self.intr_color = (250. / 255, 210. / 255, 51. / 255)
    
    self.sel_color = (1., 0., 0.)
    self.sel_actor = []
    
    self.priden_visible = True
    
    #self.gr1 = []
    #self.gr2 = []
    
    self.sel_descriptor = None
    self.sel_factor = 1.25
    
    self.mitrals = None
    self.colors = None
    self.projected = False
    self._gran = None
    self._intr = None
    self.vmin = None
    self.vmax = None

  def show_freqs(self, tstart, twin, inhib=False):
    colors = {}
    for ggid in self.gran.union(self.intr):
      frmax = 0
      for gid in bindict.ggid_dict[ggid]:
        try:
          fr = (len([ t for t in sr.retrieve(gid) if t > tstart and t <= (tstart+twin) ])+0.)/twin*1000
        except KeyError:
          continue

        if fr > frmax:
          frmax = fr

      colors[ggid] = frmax

    self.vmin = min(colors.values())
    self.vmax = max(colors.values())
    self.setup_colors(colors)
    self.show()
    
      

  def setrange(self, vmin, vmax):
    self.vmin = vmin
    self.vmax = vmax

  def cut(self, w, pos, dep):

      if not self._gran:
        self._gran = self.gran
        self._intr = self.intr
  
      def _cut(s):
        from math import sqrt
        scutted = set()
        for g in s:
          if self.projected:
            i = -1
          else:
            i = 0
          p = gpo(g)[i]

          d = plane_dist(p, w, pos)
          if d <= dep:
            scutted.add(g)
        return scutted
          
      self.gran = _cut(self.gran)
      self.intr = _cut(self.intr)

      self.show()
    

  def uncut(self):
    if self._gran:
      self.gran = self._gran
      self._gran = None
      
    if self._intr:
      self.intr = self._intr
      self._intr = None

    self.show()

  def setup_colors(self, colors):
    self.colors = colors.copy()

  def unselect(self):
    for act1, act2 in self.sel_actor:
      if act1:
        fig.scene.remove_actor(act1)
      if act2:
        fig.scene.remove_actor(act2)
    self.sel_actor = []
      
  def select(self, gid):
    from params import granule_priden2_len as l, granule_diam as diam

    pos, u, proj = gpo(gid)
    
    r = params.ranstream(gid, 0)
    r.uniform(-params.grid_dim * .5, params.grid_dim * .5)

    
    pos2 = []
    for i in range(3):
      d = r.repick()
      pos[i] += d # perturb
      pos2.append(proj[i] + u[i] * l + d)

    # draw priden actor
    src = tvtk.LineSource(point1=tuple(pos), point2=tuple(pos2))
    mapper = tvtk.PolyDataMapper(input=src.output)
    priden_actor = tvtk.Actor(mapper=mapper)
    priden_actor.property.color = self.sel_color
    
    if not self.priden_visible:
      priden_actor.property.opacity = 0.
      
    # draw soma actor
    src = tvtk.SphereSource(center=tuple(pos), radius=diam * .5 * self.sel_factor)
    mapper = tvtk.PolyDataMapper(input=src.output)
    soma_actor = tvtk.Actor(mapper=mapper)
    soma_actor.property.color = self.sel_color
    fig.scene.add_actor(priden_actor)
    fig.scene.add_actor(soma_actor)
    self.sel_actor.append((priden_actor, soma_actor))



    
  def show(self, not_in_weights=False):

    def drawgranules(gids, gcolor, *arg):
      
      from params import granule_diam as diam
      x = []
      y = []
      z = []
      if self.colors:
        s = []
        
      if self.colors and not not_in_weights:
          gids = gids.intersection(self.colors.keys())
          
      for gid in gids:
        if self.projected:
          if scale_mode == 'scalar':
            u, p = gpo(gid)[-2:]

            if self.colors:
              try:
                s.append(self.colors[gid] / 20 * 20 * 0.9 + 10)
              except KeyError:
                continue

              dep = -(100 - s[-1]) / 20 * params.grid_dim # depth from colors
              p = [ dep * u[0] + p[0], dep * u[1] + p[1], dep * u[2] + p[2]]
              diam = 0.42
          elif scale_mode == 'none':
            p = gpo(gid)[2]
        else:
          p = gpo(gid)[0]
      
        if self.colors and not (self.projected and scale_mode == 'scalar'):
          
          try:
            color = self.colors[gid]
          except KeyError:
            color = 0
            
          if gthreshold:
            if color >= gthreshold:
              s.append(1)
            else:
              s.append(0)
          else:
            s.append(color)
          
        
        r = params.ranstream(gid, 0)
        r.uniform(-params.grid_dim * .5, params.grid_dim * .5)          
        x.append(p[0] + r.repick())
        y.append(p[1] + r.repick())
        z.append(p[2] + r.repick())

      #print 'drawn mitral:',len(x)

      if self.colors:
        if self.vmin != None and self.vmax != None:
          return points3d(x, y, z, s, scale_factor=diam, vmin=self.vmin, vmax=self.vmax, scale_mode=scale_mode, colormap=gpalette)
        return points3d(x, y, z, s, scale_factor=diam, scale_mode=scale_mode,colormap=gpalette)
      return points3d(x, y, z, scale_factor=diam, color=gcolor,colormap=gpalette)

    
    if self.actor1:
      self.actor1.remove()
    if self.actor2:
      self.actor2.remove()
    self.actor1 = drawgranules(self.gran, self.gran_color)
    
    if len(self.intr) > 0:
      self.actor2 = drawgranules(self.intr, self.intr_color)
    else:
      self.actor2 = None
  
  def clean(self):

    self.unselect()
    self.intr.clear()
    self.gran.clear()
    if self.actor1:
      self.actor1.remove()
    self.actor1 = None
    if self.actor2:
      self.actor2.remove()
    self.actor2 = None
    self._gran = None
    self._intr = None
    
    #self.gr1 = []
    #self.gr2 = []
    
  def add(self, ci):
    new = set()
    for _ci in ci:
      new.add(_ci[3])
    self.intr.update(self.gran.intersection(new))
    self.gran.symmetric_difference_update(new)
    self.intr = set(sorted(self.intr))
    self.gran = set(sorted(self.gran))

  def pick_callback(self, picker):
    def find(pt3d, s):
      i = picker.point_id / pt3d.glyph.glyph_source.glyph_source.output.points.to_array().shape[0]
      if i != -1:
        return list(s)[i]
      return None

    if picker.actor in self.actor1.actor.actors and self.colors:
      #print 'intersection:',len(self.gran.intersection(self.colors.keys()))
      gid = find(self.actor1, self.gran.intersection(self.colors.keys()))
    else:
      if picker.actor in self.actor1.actor.actors:
        gid = find(self.actor1, self.gran)
      elif picker.actor and self.actor2 and picker.actor in self.actor2.actor.actors:
        gid = find(self.actor2, self.intr)
      else:
        gid = None

    # select
    if gid:
      granule_info(gid) # print information about granule
      self.select(gid)
      # description
      if self.sel_descriptor:
        self.sel_descriptor.sel_description = 'granule %d' % gid


      # mitrals segment highlight
      if self.mitrals:
        for g in gd.ggid_dict[gid]:
          mgid, isec, x = gd.gid_dict[g + 1][:3]
          try:
            iseg = int(x * len(self.mitrals[mgid].dend[isec]))
            self.mitrals[mgid].dend[isec][iseg].property.color = self.mitrals[mgid].sel_color
            #print gid, gd.gid_dict[g][2], g
            print '(%d, 0, %.3g, \'granule_gid_%d\')' % (gid, gd.gid_dict[g][2], g)
            #print 'ok', self.mitrals[mgid].dend[isec][iseg].property.color,  self.mitrals[mgid].sel_color
          except:
            pass
          
      if sr:
        
        #actlbl.text = 'retrieving...'
        gids = set()
        gids.add(gid)
        gids.update(gd.ggid_dict[gid])        
        history(gids)
        #from matplotlib import pyplot as plt
        #plt.ion()
        #gr1, gr2 = history(spk_history, gids)
        #self.gr1.append(gr1)
        #self.gr2.append(gr2)
        #plt.show()
        #actlbl.text = ''


import misc
from misc import mean
from tvtk.api import tvtk
cone_factor = 2.
def vtkCone(p, q):
    from math import pi


    phi_base, theta_base = misc.Spherical.to(q, p)[1:]

    quads = tvtk.CellArray() #vtk.vtkCellArray()
    points = tvtk.Points()   #vtk.vtkPoints()
    
    for i in range(11):
        # rotate
        phi, theta = misc.convert_direction((i % 10) * 2 * pi / 10, pi * .5, phi_base, theta_base)
        
        # generate  new points
        _p = tuple(misc.Spherical.xyz(p[3] * .5 * cone_factor, phi, theta, p[0:3]))
        _q = tuple(misc.Spherical.xyz(q[3] * .5 * cone_factor, phi, theta, q[0:3]))
        
        # insert points
        points.append(_p)
        points.append(_q)
        
        if i >= 1:
            # create a face            
            quad = tvtk.Quad()
            n = points.number_of_points - 1
            
            quad.point_ids.set_id(0, n - 3) # p
            quad.point_ids.set_id(1, n - 2) # q
            quad.point_ids.set_id(2, n) # q
            quad.point_ids.set_id(3, n - 1) # p
            
            # insert the new face
            quads.insert_next_cell(quad)

    # create the actor
    polydata = tvtk.PolyData(points=points, polys=quads)
    mapper = tvtk.PolyDataMapper(input=polydata)
    actor = tvtk.Actor(mapper=mapper)
    return actor


def vtkLine(p1, p2):
  src = tvtk.LineSource(point1=tuple(p1), point2=tuple(p2))
  mapper = tvtk.PolyDataMapper(input=src.output)
  actor = tvtk.Actor(mapper=mapper)
  return actor
max_frequency_showed = 80.
min_frequency_showed = 50.
class vtkMitral:

  
  def __vtkconvert(self):
    def drawsoma():
      pts = self.mitral.soma.points
      center = misc.centroid(pts)

      # calc. soma radius
      radius = 0.
      for p in pts:
        radius += misc.distance(p, center)
      radius /= len(pts)

      if tube_flag:
        radius *= cone_factor

      # versor
      u = tuple(misc.versor(self.mitral.apic.points[0], self.mitral.apic.points[1]))

      src = tvtk.ConeSource(center=tuple(center[0:3]), radius=radius, height=radius, direction=u, resolution=20)
      mapper = tvtk.PolyDataMapper(input=src.output)
      actor = tvtk.Actor(mapper=mapper)
      fig.scene.add_actor(actor)

      actor.property.color = self.soma_color 
      return actor

    # create a colored segment on the scene
    def mksegment(p1, p2, color):
      if tube_active:
        actor = vtkCone(p1, p2)
      else:
        actor = vtkLine(p1[0:3], p2[0:3])
      
      actor.property.color = color
      fig.scene.add_actor(actor)
      return actor
          
    def drawsection(pts):
      section = []
      for i in range(1, len(pts)):
        section.append(mksegment(pts[i - 1], pts[i], self.section_color))
      return section
    
    #fig.scene.disable_render = True
    self.soma = drawsoma()
    self.apic = drawsection(self.mitral.apic.points)
    for i in range(len(self.mitral.tuft)):
      self.tuft.append(drawsection(self.mitral.tuft[i].points))


    # gid associated to a segment
    self.dend_gids = []
    for i in range(len(self.mitral.dend)):
      self.dend.append(drawsection(self.mitral.dend[i].points))
      
      aux = []
      for i in range(len(self.dend[-1])):
        aux.append(set())
      self.dend_gids.append(aux)
      

    #fig.scene.disable_render = False
    

  def __interpolate(self, dg):
    def look(seg, forward=True):
      info = set()

      def move():
        newseg = []

        for i in range(len(seg)):
          isec, iseg = seg[i][1:]

          if forward:
            iseg += 1

            if iseg >= len(self.dend[isec]):
              # find sons
              for s in self.mitral.dend[isec].sons:
                newseg.append((2, self.mitral.dend.index(s), 0))
            else:
              newseg.append((2, isec, iseg))

          else:
            iseg -= 1
            if iseg < 0:
              try:
                isec = self.mitral.dend.index(self.mitral.dend[isec].parent)
                iseg = len(self.dend[isec]) - 1
                newseg.append((2, isec, iseg))
              except:
                pass
            else:
              newseg.append((2, isec, iseg))
        return newseg

      
      while len(seg) > 0:
        seg = move() # move the segment

        # check if none
        i = 0
        while i < len(seg):
          isec, iseg = seg[i][1:]
          if len(dg[isec][iseg]) > 0:
            info.add(seg[i])
            del seg[i]
          else:
            i += 1

      return info
        
        

    interpinfo = {}

    # scan
    for isec in range(len(dg)):
      for iseg in range(len(dg[isec])):
        if len(dg[isec][iseg]) == 0: # not touched
          linked = look([(2, isec, iseg)])
          linked.update(look([(2, isec, iseg)], forward=False))
          interpinfo.update({ (2, isec, iseg):linked })

    return interpinfo

  def __init__(self, mgid):
    self.__cutted = False
    self.weights_max=True
    self.mgid = mgid

    from getmitral import getmitral as genMitral

    self.mitral = genMitral(mgid)


    self.soma = None
    self.apic = None
    self.dend = []
    self.tuft = []

    self.soma_color = (250. / 255, 210. / 255, 51. / 255)
    self.section_color = (1., 1., 1.)

    self.__vtkconvert()

    self.sel_color = (0., 1., 0.)
    self.sel_all = False

    import granules
    self.conn_info = []
    if flag_dict:
      grans=set()
      for gid in gd.mgid_dict[mgid]:
        if gid >= params.gid_granule_begin+granules.Ngranule and gid%2 == 0:
          self.conn_info.append(gd.gid_dict[gid])
          grans.add(self.conn_info[-1][3])
      print 'Mitral %d has %d synapses in %d granules'%(mgid, len(self.conn_info), len(grans))

      even = set()
      for gid in gd.mgid_dict[mgid]:
        if gid >= params.gid_granule_begin+granules.Ngranule and gid%2 == 0:
          isec,x = gd.gid_dict[gid][1:3]
          iseg = int(x*len(self.dend[isec]))
          if x >= 1: iseg = len(self.dend[isec])-1
          if (isec, iseg) not in even:
            self.dend_gids[isec][iseg].add(gid)
            even.add((isec, iseg))
          self.dend_gids[isec][iseg].add(gid-1)
          
      #for gid in gd.mgid_dict[mgid]:
      #  if gid >= params.gid_granule_begin + granules.Ngranule:
      #    if gid % 2 == 0:
      #      self.conn_info.append(gd.gid_dict[gid])
      #      
      #for gid in gd.mgid_dict[mgid]:
      #  if gid >= params.Nmitral + granules.Ngranule:
      #    if gid % 2 == 0:
      #      isec, x = gd.gid_dict[gid][1:3]
      #      iseg = int(x * len(self.dend[isec]))
      #      
      #      if x >= 1:
      #        iseg = len(self.dend[isec]) - 1
      #        
      #      self.dend_gids[isec][iseg].add(gid)
    else:
      from mkmitral import mkmitral
      from m2g_connections import determine_mitral_connections
      self.conn_info = determine_mitral_connections(mgid, mkmitral(mgid))
      

    self.interpolate = self.__interpolate(self.dend_gids) # complete the colors info using interpolation


          
    #self.gr1 = []
    #self.gr2 = []
    self.__show_weights = False
    self.__show_freqs = False

  def remove(self):
    delactor = fig.scene.remove_actor
    
    def delactors(actors):
      for x in actors:
        delactor(x)

    #fig.scene.disable_render = True
    delactor(self.soma)
    delactors(self.apic)
    for sec in self.dend:
      delactors(sec)
    for sec in self.tuft:
      delactors(sec)
    #fig.scene.disable_render = False
      
  def __set_segment(self, info):

    for secinfo, ind_color in info.items():

      # interpolate
      sec_type, isec, iseg = secinfo

      if sec_type == -1: # soma
        o = self.soma
      elif sec_type == 0: # tuft
        o = self.tuft[isec][iseg]
      elif sec_type == 1: # apical
        o = self.apic[iseg]
      elif sec_type == 2: # dendrites
        o = self.dend[isec][iseg]

      # set
      o.property.color = palette[ind_color]
      o.property.opacity = 1.      


    # set the information to interpolate
    if interpolate_flag:
      for seginfo, seginterp in self.interpolate.items():
        isec, iseg = seginfo[1:]

        # mean
        ind_color = 0
        for sectype, isec2, iseg2 in seginterp:
          ind_color += info[(2, isec2, iseg2)]
        ind_color = int(round((0. + ind_color) / len(seginterp)))

        # set color
        self.dend[isec][iseg].property.color = palette[ind_color]
    else:
      for sectype, isec, iseg in self.interpolate.keys():
        self.dend[isec][iseg].property.opacity = 0.

    if self.__cutted:
      self.cut(*self.__cutted)
      

      

  def show_freqs(self, tstart, tdur, inhib=False):
    if not sr and not self.__show_weights:
      return
    self.__show_freqs = True
    self.__tstart = tstart
    self.__tdur = tdur
    
    freqs = {}
    
    if inhib:
      n = {}
      
    for gid in bindict.mgid_dict[self.mgid]:
      if gid % 2 != 0: continue
      if gid < syn_gid_begin: continue
      
      # find segment index
      isec, x = bindict.gid_dict[gid][1:3]
      nseg = len(self.dend[isec])
      iseg = int(x*nseg)
      if iseg >= nseg:
        iseg = nseg-1

      # use it like key
      key = (2, isec, iseg)

      # already examined
      if not inhib and key in freqs:
        continue

      # calculate frequency
      
      if inhib:
        fr = len([ t for t in sr.retrieve(gid-1) if t >= tstart and t < (tstart+tdur) ])

        # color index
        colindex = int((fr-minfreq_shown)/(maxfreq_shown-minfreq_shown)*len(palette))
        if colindex < 0:
          colindex = 0
        elif colindex >= len(palette):
          colindex = len(palette)-1

        if key not in freqs:
          freqs[key] = colindex
          n[key] = 1.0
        else:
          freqs[key] += colindex
          n[key] += 1
          
      else:
        
        fr = len([ t for t in sr.retrieve(gid) if t >= tstart and t < (tstart+tdur) ])

        # color index
        colindex = int((fr-minfreq_shown)/(maxfreq_shown-minfreq_shown)*len(palette))
        if colindex < 0:
          colindex = 0
        elif colindex >= len(palette):
          colindex = len(palette)-1

        freqs[key] = colindex

    if inhib:
      for key in freqs:
        freqs[key] = int(freqs[key] / n[key])

    # show frequencies
    self.__set_segment(freqs)
        
      
      




  def setup_colors(self, colors, odd=True):
    ws = {}
    for isec in range(len(self.apic)): ws.update({ (1, 0, isec):0 })
    for ituft in range(len(self.tuft)):
      for isec in range(len(self.tuft[ituft])): ws.update({ (0, ituft, isec):0 })

    from mgrs import gid_mgrs_begin
    for gid in bindict.mgid_dict[self.mgid]:
      if gid < gid_mgrs_begin or gid % 2 != 0: continue
      isec, x = bindict.gid_dict[gid][1:3]
      if x >= 1:
        iseg = len(self.dend[isec])-1
      else:
        iseg = int(x*len(self.dend[isec]))


      w = colors[gid]
      ns = {}
      try:
        ws[(2, isec, iseg)] = (ws[(2, isec, iseg)]*ns[(2, isec, iseg)] + w*(len(palette)-1))/(n+1)
        ns[(2, isec, iseg)] += 1
      except KeyError:
        ws[(2, isec, iseg)] = w*(len(palette)-1)
        ns[(2, isec, iseg)] = 1
                   
    self.__set_segment({ gid:int(ws[gid]) for gid in ws })

        
        
      
    

  def show_weights(self, excit):
    
    if len(weights) == 0 or self.__show_freqs: return

    self.__show_weights = True
    self.__excit = excit

    w = {}
    for isec in range(len(self.apic)): w.update({ (1, 0, isec):[0] })
    for ituft in range(len(self.tuft)):
      for isec in range(len(self.tuft[ituft])): w.update({ (0, ituft, isec):[0] })
    
    for gid in bindict.mgid_dict[self.mgid]:
      if gid >=  syn_gid_begin and gid % 2 == 0:
        isec, x = bindict.gid_dict[gid][1:3]
        if x >= 1:
          iseg = len(self.dend[isec])-1
        else:
          iseg = int(x*len(self.dend[isec]))
          
        if not excit: gid-=1

        try:
          wsym = weights[gid]
          try:
            w[(2, isec, iseg)].append(wsym)
          except KeyError:
            w.update({(2, isec, iseg):[wsym]})
        except KeyError:
          print 'gid %d not found' % gid



    if excit:
      max_steps = 0. + 2 * binspikes.sighalf_excit
    else:

      max_steps = 0. + 2 * binspikes.sighalf_inhib

    for k, ws in w.items():
      if self.weights_max:
        _w = max(ws)
      else:
        _w = mean(ws)
      
      w[k] = int(_w/max_steps*(len(palette)-1))

    self.__set_segment(w)
          

  def clean_freqs(self):
    self.__show_freqs = False
    
    # color all black
    for dnd in self.dend:
      for seg in dnd:
        seg.property.opacity = 1.

    self.clean()

  def clean_weight(self):
    self.__show_weights = False
    
    # color all black
    for dnd in self.dend:
      for seg in dnd:
        seg.property.opacity = 1.

    self.clean()
    
  def __color_section(self, sec, color):
    for s in sec:
      s.property.color = color
      
  def clean(self):
    if self.__show_weights:
      self.show_weights(self.__excit)
      
    elif self.__show_freqs:
      self.show_freqs(self.__tstart, self.__tdur)

    else:
      self.soma.property.color = self.soma_color
      for sec in self.dend:
        for seg in sec:
          seg.property.color = self.section_color
      for sec in self.tuft:
        for seg in sec:
          seg.property.color = self.section_color
      for seg in self.apic:
        seg.property.color = self.section_color

      if not self.__cutted:
        self.soma.property.opacity = 1
        for sec in self.dend:
          for seg in sec:
            seg.property.opacity = 1
        for sec in self.tuft:
          for seg in sec:
            seg.property.opacity = 1
        for seg in self.apic:
          seg.property.opacity = 1
      else:
        self.cut(*self.__cutted)
        
  # select actor
  def select(self, actor):
    if self.sel_all:
      self.soma.property.color = self.sel_color
      self.__color_section(self.apic, self.sel_color)
      for i in range(len(self.tuft)):
        self.__color_section(self.tuft[i], self.sel_color)
      for i in range(len(self.dend)):
        self.__color_section(self.dend[i], self.sel_color)
    else:
      actor.property.color = self.sel_color
      

      
  def pick_callback(self, picker):
    #self.clean() # clean
    
    actor = picker.actor



    # checks
    flag = False
    if actor == self.soma:
      self.select(self.soma)
      if sr:
        history(set([ self.mgid ]))
      flag = True

    if not flag:
      try:
        j = self.apic.index(actor)
        self.select(self.apic[j])
        flag = True
      except ValueError:
        pass

    if not flag:
      for i in range(len(self.tuft)):
        try:
          j = self.tuft[i].index(actor)
          self.select(self.tuft[i][j])
          flag = True
          break
        except ValueError:
          pass

    if not flag:        
      for i in range(len(self.dend)):
        try:
          j = self.dend[i].index(actor)

          flag = True
          self.select(self.dend[i][j])
          
          if self.granules and not self.sel_all:
            self.granules.unselect()
            for g in self.dend_gids[i][j]:
              if g%2 != 0:
                self.granules.select(gd.gid_dict[g+1][3])
            
          if sr:
            #
            #actlbl.text = 'retrieving...'
            #gids = set()
            #gids.update(self.dend_gids[i][j]) # excit
            #for g in self.dend_gids[i][j]: # inhib
            #  gids.add(g - 1)
            #gids.add(list(self.dend_gids[i][j])[0])
            #for g in self.dend_gids[i][j]:
            #  gids.add(g - 1) # inhib
            history(self.dend_gids[i][j])
            #print gids
           # gr1, gr2 = sh.history(spk_history, gids)
            #self.gr1.append(gr1)
            #self.gr2.append(gr2)
            #actlbl.text = ''
            
          
        except ValueError:
          pass


    if flag and self.sel_descriptor:
      self.sel_descriptor.sel_description = 'mitral %d' % self.mgid


  def cut(self, w, pos, dep):
    
    def set_cut_1(act, grw):
      from math import sqrt
      for i in range(1, len(grw.points)):
        p = grw.points[i]
        d = plane_dist(p, w, pos)
        if d <= dep and act[i - 1].property.opacity == 1:
          op = 1.
        else:
          op = 0.
        act[i - 1].property.opacity = op
        
    def set_cut_2(acts, grws):
      for i in range(len(acts)):
        set_cut_1(acts[i], grws[i])
      

    from misc import centroid, mean
    if plane_dist(centroid(self.mitral.soma.points), w, pos) <= dep:
      self.soma.property.opacity = 1.
    else:
      self.soma.property.opacity = 0.
    set_cut_1(self.apic, self.mitral.apic)
    set_cut_2(self.tuft, self.mitral.tuft)
    set_cut_2(self.dend, self.mitral.dend)
    self.__cutted = (tuple(w), tuple(pos), dep)

  def uncut(self):
    def set_op(act, op):
      act.property.opacity = op
      
    def set_op_1(acts, op):
      for a in acts:
        set_op(a, op)

    def set_op_2(acts_v, op):
      for x in acts_v:
        set_op_1(x, op)

    set_op(self.soma, 1.)
    set_op_1(self.apic, 1.)
    set_op_2(self.tuft, 1.)
    set_op_2(self.dend, 1.)
    self.__cutted = None
          


class mayaBulbPlot:
  def __init__(self):
    self.sel_descriptor = None
    self.mitrals = {}
    self.granules = GranulesManager()
    self.sel_all = False
    self.picker = fig.on_mouse_pick(self.pick_callback)
    self.picker.tolerance = 0.002
    self.gran_select = True
    self.mitr_select = True
    self.other_select = True
    self.sel_color = (0., 1., 0.)
    self.other_callback = []
    

  def show_freqs(self, tstart, twin, inhib=False):
    for m in self.mitrals.values():
      m.show_freqs(tstart, twin, inhib)

  def draw_mitral(self, mgid):
    if self.mitrals.has_key(mgid):
      return

    m = vtkMitral(mgid)
    m.sel_color = self.sel_color
    m.granules = self.granules
    m.sel_all = self.sel_all # selection type
    m.sel_descriptor = self.sel_descriptor
    self.mitrals.update({ mgid:m })
    self.granules.add(m.conn_info) # draw granules
    self.granules.show()

  def show_weights(self, excit):
    for m in self.mitrals.values():
      m.show_weights(excit)

  def clean_weights(self):
    for m in self.mitrals.values():
      m.clean_weight()

  def clean_freqs(self):
    for m in self.mitrals.values():
      m.clean_freqs()

  def clean(self):
    for m in self.mitrals.values():
      m.remove()
    self.mitrals.clear()
    self.granules.clean()
    #sh.clean()
    #self.granules.gr1 = []
    #self.granules.gr2 = []
    if self.sel_descriptor:
      self.sel_descriptor.sel_description = ''

  def pick_callback(self, picker):

    # clean
    if self.sel_descriptor:
      self.sel_descriptor.sel_description = ''

    if not picker:
      return

    # clean object
    for m in self.mitrals.values():
      m.clean()

    self.granules.unselect()

    # callbacks

    # other callback
    if self.other_select:
      for obj in self.other_callback:
        obj.pick_callback(picker)
        
    if self.gran_select:
      self.granules.pick_callback(picker)
      
    if self.mitr_select:
      for m in self.mitrals.values():
        m.pick_callback(picker)
        

  def cut(self, w, o, dep):
    fig.scene.disable_render = True
    for m in self.mitrals.values():
      m.cut(w, o, dep)
    self.granules.cut(w, o, dep)
    fig.scene.disable_render = False

  def uncut(self):
    fig.scene.disable_render = True
    for m in self.mitrals.values():
      m.uncut()
    self.granules.uncut()
    fig.scene.disable_render = False
    



try:
  from enthought.traits.api import HasTraits, Range, String, Button, Int, Bool, Str, Float
  from enthought.traits.ui.api import View, Item
except:
  from traits.api import HasTraits, Range, String, Button, Int, Bool, Str, Float
  from traitsui.api import View, Item
    







  
if __name__ == '__main__':
  

  mbp = mayaBulbPlot()
  gcol = None
  
  if '-weights' in argv:
    loadweights(argv[argv.index('-weights') + 1])
    if gweights:
      valmin = None
      valmax = None

      
      try:
        valmin = float(argv[argv.index('-min') + 1])
      except:
        valmin = 0
      
      try:
        valmax = float(argv[argv.index('-max') + 1])
      except:

        valmax = 2 * binspikes.sighalf_inhib
      


      gcol = gcolors(valmin, valmax)
  elif '-nsyn' in argv:

      
    try:
      valmin = float(argv[argv.index('-min') + 1])
    except:
      valmin = 0
    
    try:
      valmax = float(argv[argv.index('-max') + 1])
    except:
      valmax = max(gcol.values())
      
    gcol = {}
    for ggid, syns in bindict.ggid_dict.items():
      l = len(syns)
      if l >= valmin and l <= valmax:
        gcol[ggid] = len(syns)
    mbp.granules.setup_colors(gcol)
    mbp.granules.setrange(valmin, valmax)
      

  if '-hist' in argv:
    #spk_history = argv[argv.index('-hist') + 1]
    if '-initweights' in argv:
      sr = binspikes.SpikesReader(argv[argv.index('-hist') + 1], argv[argv.index('-initweights') + 1])
    else:
      sr = binspikes.SpikesReader(argv[argv.index('-hist') + 1])

    
  try:
    from enthought.traits.api import HasTraits, Range, String, Button, Int, Bool, Str, Float
    from enthought.traits.ui.api import View, Item
  except:
    from traits.api import HasTraits, Range, String, Button, Int, Bool, Str, Float
    from traitsui.api import View, Item



    

  mbp.granules.projected = '-proj' in argv        
  mbp.granules.intr_color = mbp.granules.gran_color
  mbp.granules.priden_visible = False
  mbp.granules.mitrals = mbp.mitrals
  mbp.granules.sel_color = (1., 0., 1.)
  
  if gcol:
    mbp.granules.setup_colors(gcol)

    mbp.granules.setrange(0, 2*binspikes.sighalf_inhib)
    
  class BulbGUI(HasTraits):
    exectxt = Str
    execbtn = Button('exec')
    gid_txt = Int
    add_glom = Button('Add Glom')
    add_mitr = Button('Add Mitral')
    gid_cmd = Button('Find History')
    clean = Button('Clean')
    w_excit = Button('Weights Excit.')
    w_inhib = Button('Weights Inhib.')
    w_clean = Button('Weights Clean')


    start_cut = Button('Start Cut')
    cut = Button('Cut')
    clean_cut = Button('Clean Cut')
    freqs_exc = Button('Freqs exc. show')
    freqs_inh = Button('Freqs inhib. show')
    freqs_clean = Button('Clean Freqs')

    tstart = Float
    twin = Float
    max_freqs = Float
    min_freqs = Float

    dep = Float
    
    view = View(Item(name='gid_txt'), Item(name='add_mitr'), Item(name='add_glom'),
                Item(name='gid_cmd'), Item(name='clean'), Item(name='w_excit'),
                Item(name='w_inhib'), Item(name='w_clean'), Item(name='dep'),
                Item(name='start_cut'), Item(name='cut'), Item(name='clean_cut'), Item(name='freqs_exc'), Item(name='freqs_inh'), Item(name='freqs_clean'),
                Item(name='tstart'), Item(name='twin'), Item(name='max_freqs'), Item(name='min_freqs'),
                Item(name='exectxt'), Item(name='execbtn'))
    
    def __init__(self, mbp):
      self.edit_traits()
      #self.gr1 = []
      #self.gr2 = []
      self.mbp = mbp
      self.dep = 100.
      self._nihl = self._cp = None
      self.tstart = binspikes.tstop #-params.sniff_invl
      self.twin=1000 #params.sniff_invl
      self.cutting = False
      self.t_win = params.sniff_invl
      self.max_freqs = maxfreq_shown
      self.min_freqs = minfreq_shown
      
    def _freqs_exc_fired(self):
      self.mbp.show_freqs(self.tstart, self.twin)
      fig.scene.render()

    def _execbtn_fired(self):
      exec self.exectxt
      
    def _freqs_inh_fired(self):
      self.mbp.show_freqs(self.tstart, self.twin, True)
      fig.scene.render()

    def _freqs_clean_fired(self):
      self.mbp.clean_freqs()
      fig.scene.render()
      
    def _max_freqs_changed(self):
      global maxfreq_shown
      maxfreq_shown = self.max_freqs
      
    def _min_freqs_changed(self):
      global minfreq_shown
      minfreq_shown = self.min_freqs

    def _gid_cmd_fired(self):
      #if len(spk_history):
      gid = self.gid_txt
      gids = set([ gid ])
      if gid >= params.Nmitral + granules.Ngranule:
        if gid % 2:
          gid += 1
          gids.add(gid)
        else:
          gids.add(gid - 1)
      elif gid >= params.Nmitral:
          gids.update(set(gd.ggid_dict[gid]))

      # granule highlight
      def ghl(gid):
        if gid in mbp.granules.intr.union(mbp.granules.gran):
          mbp.granules.select(gid)

      # highlight scene objects
      if gid < params.Nmitral:
        if gid in mbp.mitrals:
          m = mbp.mitrals[gid]
          m.select(m.soma)
      elif gid < params.Nmitral + granules.Ngranule:
        ghl(gid)
      else:
        info = gd.gid_dict[gid]
        ghl(info[3])
        
        # highlight mitral
        if info[0] in mbp.mitrals:
          m = mbp.mitrals[info[0]]
          if info[2] >= 1:
            iseg = len(m.dend[info[1]]) - 1
          else:
            iseg = int(len(m.dend[info[1]]) * info[2])
          m.select(m.dend[info[1]][iseg])

      # make history
      history(gids)

        
        #gr1, gr2 = sh.history(spk_history, gids)
        #self.gr1.append(gr1)
        #self.gr2.append(gr2)
        #h.doNotify()

    def _clean_fired(self):
      fig.scene.disable_render = True
      #self.gr1 = []
      #self.gr2 = []
      #h.doNotify()
      self.mbp.clean()
      fig.scene.disable_render = False
      history_clean()



    def _w_excit_fired(self):
      #self.mbp.mitr_select = self.mbp.gran_select = True
      self.mbp.show_weights(True)
      fig.scene.render()

    def _w_inhib_fired(self):
      #self.mbp.mitr_select = self.mbp.gran_select = False
      self.mbp.show_weights(False)
      fig.scene.render()

    def _w_clean_fired(self):
      #self.mbp.mitr_select = self.mbp.gran_select = True
      self.mbp.clean_weights()
      fig.scene.render()

    def __add_mitrals(self, s):
      fig.scene.disable_render = True
      for mgid in s:
        self.mbp.draw_mitral(mgid)
      fig.scene.disable_render = False

    def _add_glom_fired(self):
      try:
        mitrals = set(range(params.Nmitral_per_glom * self.gid_txt, params.Nmitral_per_glom * (self.gid_txt + 1)))
        self.__add_mitrals(mitrals)
      except:
        pass
      
    def _add_mitr_fired(self):
      try:
        self.__add_mitrals(set([ self.gid_txt ]))
      except:
        pass

    def _start_cut_fired(self):
      if self.cutting: return
      
      self.cutting=True
      from mayavi import mlab
      from params import granule_origin as go, Nx_granule, Ny_granule, Nz_granule, grid_dim as d
      xl = Nx_granule * d
      yl = Ny_granule * d
      zl = Nz_granule * d
      
      self._nihl = mlab.points3d([ go[0], go[0] + xl ], [ go[1], go[1] + yl ], [ go[2], go[2] + zl ], opacity=0.)
      self._cp = mlab.pipeline.scalar_cut_plane(self._nihl)
      
    def _cut_fired(self):
      if self._nihl and self._cp:
        self.mbp.cut(self._cp.implicit_plane.normal, self._cp.implicit_plane.origin, self.dep)
        print self._cp.implicit_plane.normal,self._cp.implicit_plane.origin,self.dep
        self._nihl.remove()
        self._cp.remove()
        self._nihl = self._cp = None

    def _clean_cut_fired(self):
      self.mbp.uncut()

      
      if self._nihl:
        self._nihl.remove()
        self._nihl = None
        
      if self._cp:
        self._cp.remove()
        self._cp = None
    
  #import BulbSurf
  #bulb = BulbSurf.Bulb3d(fig)
  gui = BulbGUI(mbp)

      
  from mayavi import mlab
  mlab.show()
