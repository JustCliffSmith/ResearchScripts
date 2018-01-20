# -*- coding: utf-8 -*-
"""
Created on Thu Jan  4 11:21:00 2018

@author: Justin Clifford Smith
"""

import numpy as np
from scipy.interpolate import griddata
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os

#initialize adatom position arrays
x = np.array([])
y = np.array([])
z = np.array([])

'''
def PES_data(openfile): 
  final = False
  for line in openfile:
     linelist = line.split()
     if linelist:
       if (linelist[0] == 'Final' and linelist[1] == 'atomic'):
         final = True
         return 1, 2 ,3
       if (linelist[0] == 'atom' and linelist[-1] == 'Ge' and final == True):
         x = float(linelist[1])
         y = float(linelist[2])
       if (len(linelist) > 10  and linelist[1] == 'Total' \
           and linelist[2] == 'energy' and linelist[3] == 'of'):
         z = float(linelist[-2])
         return x, y, z

#Get data for PES
for output in os.listdir('.'):
    with open(output) as outputfile:
#        xapp, yapp, zapp = 
        coords = PES_data(outputfile)
        print(coords)
        x = np.append(x,xapp).astype(np.float)
        y = np.append(y,yapp).astype(np.float)
        z = np.append(z,zapp).astype(np.float)

'''
final = False

#Get data for PES
for output in os.listdir('.'):
  if output.startswith('subcont.output'): #TODO, generalize as CLI
    with open(output) as openfile:
        for line in openfile:
            linelist = line.split()
            if linelist:
                if (linelist[0] == 'Final' and linelist[1] == 'atomic'):
                    final = True
                if (linelist[0] == 'atom' and linelist[-1] == 'Ge' \
                    and final == True):
                    x = np.append(x,linelist[1]).astype(np.float)
                    y = np.append(y,linelist[2]).astype(np.float)
                    final = False
                if (len(linelist) > 10  and linelist[1] == 'Total' \
                     and linelist[2] == 'energy' and linelist[3] == 'of'):
                    z = np.append(z,linelist[-2]).astype(np.float)

#normalize data to one for the largest negative value
z = np.multiply(z, 1/np.amin(z))

#get atomic positions for scatter
for files in os.listdir('.'):
  if files.endswith(".in"):
    print('Extracting atomic positions from {}'.format(files))
    xscIn = np.array([])
    yscIn = np.array([])
    zscIn = np.array([])
    xscAs = np.array([])
    yscAs = np.array([])
    zscAs = np.array([])
#    xscGe = np.array([])
#    yscGe = np.array([])
#    zscGe = np.array([])
    latvec = np.array([])
    latcount = 0
    with open(files) as geometryfile:
      for line in geometryfile:
        linelist = line.split()
        if linelist:
          if linelist[0] == 'lattice_vector' and latcount < 2:
            latvec = np.append(latvec,linelist[1]).astype(np.float) #x
            latvec = np.append(latvec,linelist[2]).astype(np.float) #y
            latcount += 1 #only want first two lattice vectors
          if (linelist[0] == 'atom' and linelist[-1] == 'In' ):
            xscIn = np.append(xscIn,linelist[1]).astype(np.float)
            yscIn = np.append(yscIn,linelist[2]).astype(np.float)
            zscIn = np.append(zscIn,linelist[3]).astype(np.float)
          if (linelist[0] == 'atom' and linelist[-1] == 'As'):
            xscAs = np.append(xscAs,linelist[1]).astype(np.float)
            yscAs = np.append(yscAs,linelist[2]).astype(np.float)
            zscAs = np.append(zscAs,linelist[3]).astype(np.float)
#          if (linelist[0] == 'atom' and linelist[-1] == 'Ge'):
#            xscGe = np.append(xscGe,linelist[1]).astype(np.float)
#            yscGe = np.append(yscGe,linelist[2]).astype(np.float)
#            zscGe = np.append(zscGe,linelist[3]).astype(np.float)


#define the grid dimensions
xi = np.linspace(0, latvec[0] + latvec[2], 1000)
yi = np.linspace(0, latvec[3], 1000)
#grid the data
zi = griddata((x, y), z, (xi[None,:], yi[:,None]), method='cubic')
#draw the edges of the surface cell 
ax = plt.axes()
ax.arrow(0, 0, latvec[2], latvec[3], head_width=None, lw=1, color='k') # left
ax.arrow(0, 0, latvec[0], 0, head_width=None, lw=1, color='k') #bottom
ax.arrow(latvec[0], 0, latvec[2], latvec[3], head_width=None, lw=1, color='k') #right
ax.arrow(latvec[2], latvec[3], latvec[0], 0, head_width=None, lw=1, color='k') #top
#contour the gridded data, plotting dots
plt.contour(xi, yi, zi, 15, linewidths=0.5, colors='k')
plt.contourf(xi, yi, zi*2, 15, cmap=plt.cm.jet)
plt.colorbar() # draw colorbar
#plt.scatter(xscIn[-11:], yscIn[-11:], zscIn[-11:]**3/15, c='c', zorder=1)
#plt.scatter(xscAs[-8:], yscAs[-8:], zscAs[-8:]**3/15, c='k', zorder=1)
plt.scatter(xscIn[-7:], yscIn[-7:], 100*(zscIn[-7:]/zscIn[-1])**4, c='c', zorder=1)
plt.scatter(xscAs[-8:], yscAs[-8:], 100*(zscAs[-8:]/zscAs[-1])**4, c='k', zorder=1)
#plt.scatter(xscGe, yscGe, (zscGe)**2, c='g', zorder=1)
plt.xlim(0,latvec[0] + latvec[2])
plt.ylim(0,latvec[3] + .1)
#plt.savefig('PES_output.png', bbox_inches='tight')
plt.show()


